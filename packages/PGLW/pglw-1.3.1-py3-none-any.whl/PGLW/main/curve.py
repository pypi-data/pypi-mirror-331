import copy

import numpy as np
from scipy.interpolate import Akima1DInterpolator, CubicSpline, interp1d, pchip

from PGLW.main.distfunc import distfunc
from PGLW.main.geom_tools import (
    RotX,
    RotY,
    RotZ,
    calculate_length,
    curvature,
    dotX,
)
from PGLW.main.naturalcubicspline import NaturalCubicSpline

deg2rad = np.pi / 180.0


class LinearSpline(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __call__(self, s):
        return np.interp(s, self.x, self.y)


class Curve(object):
    """
    Class for 2D and 3D curves
    """

    def __init__(
        self, points=None, spline="ncubic", nd=None, s=None, compute_dp=True
    ):
        self.spline_type = spline
        if spline == "linear":
            self._splcls = LinearSpline
        elif spline == "cubic":
            self._splcls = CubicSpline
        elif spline == "ncubic":
            self._splcls = NaturalCubicSpline
        elif spline == "akima":
            self._splcls = Akima1DInterpolator
        elif spline == "pchip":
            self._splcls = pchip

        if nd is not None and nd > points.shape[1]:
            points = np.vstack(
                (points.T, np.zeros(points.shape[0], dtype=points.dtype))
            ).T

        self._compute_dp_flag = compute_dp
        self._ignore_s = False
        if s is not None:
            self.s = s
            self._ignore_s = True

        if points is not None:
            self.initialize(points)

        self.name = ""

    def initialize(self, points):
        """
        called by __init__ to compute running curve length,
        curve gradients and splines.
        """

        self.points = np.asarray(points)
        self.ni = self.points.shape[0]
        self.nd = self.points.shape[1]

        # Checking if array has the correct size
        if not ((self.nd == 2) or (self.nd == 3)) or (self.ni < 2):
            raise ValueError(
                "The shape of the points needs to have the shape (>2,2) or "
                "(>2,3) but it is (%d,%d) (Maybe it should be transposed?)"
                % (self.ni, self.nd)
            )

        # Check if the same point twice
        if any(np.linalg.norm(np.diff(points, axis=0), axis=1) == 0):
            raise ValueError(
                "Neighboring points need to be unique. Check that two neigboring points are not the same."
            )

        self._compute_s()
        self.dp = np.zeros(self.points.shape)
        if self._compute_dp_flag:
            self._compute_dp()
        self._build_splines()

    def _compute_s(self):
        """
        compute normalized curve length
        """
        if not self._ignore_s:
            self.s = calculate_length(self.points)
        self.smax = self.s[-1]
        self.ds = np.diff(self.s)
        # self.ds = np.insert(self.ds, 0, [0.])
        self.s = self.s / self.s[-1]
        self.k = curvature(self.points)

    def _compute_dp(self):
        """compute the unit direction vectors along the curve"""

        t1 = np.gradient(self.points[:, :])[0]
        self.dp = np.array(
            [t1[i, :] / np.linalg.norm(t1[i, :]) for i in range(t1.shape[0])]
        )

    def _build_splines(self):
        """
        build splines for the curve using the user specified
        spline type
        """
        self._splines = []

        if self.points.shape[0] > 2:
            for j in range(self.points.shape[1]):
                self._splines.append(self._splcls(self.s, self.points[:, j]))
        else:
            for j in range(self.points.shape[1]):
                self._splines.append(
                    interp1d(self.s, self.points[:, j], kind="linear")
                )

    def redistribute(self, dist=None, s=None, ni=100, linear=False):
        """
        redistribute the points on the curve using distfunc
        or a user-supplied distribution

        parameters
        ----------
        dist: list
            list of control points with the form

            | [[s0, ds0, n0], [s1, ds1, n1], ... [s<n>, ds<n>, n<n>]]

            | where

                | s<n> is the curve fraction at each control point,
                | ds<n> is the cell size at each control point,
                | n<n> is the cell count at each control point.
        s: array
            normalized distribution of cells.
        ni: int
            if neither dist or s are supplied, points will be
            redistributed evenly using ni points.
        """
        if dist is not None:
            ni = dist[-1][-1]
            if linear:
                self.s = np.zeros(ni)
                for d0, d1 in zip(dist[:-1], dist[1:]):
                    self.s[d0[2] - 1 : d1[2]] = np.linspace(
                        d0[0], d1[0], d1[2] - d0[2] + 1
                    )
            else:
                self.s = distfunc(np.real(dist))
        elif s is not None:
            self.s = s
        else:
            self.s = np.linspace(0, 1, ni)

        self.ni = self.s.shape[0]
        points = np.zeros(
            (self.ni, self.points.shape[1]), dtype=self.points.dtype
        )
        for i in range(points.shape[1]):
            points[:, i] = self._splines[i](self.s)

        self.initialize(points)

    def interp_s(self, s):
        """
        interpolate (x,y) at some curve fraction s

        parameters
        ----------
        s: float
            normalized curve fraction

        returns
        -------
        p: array
            (x, y, [z]) coordinates of interpolated point
        """

        p = np.zeros(self.points.shape[1], dtype=self.points.dtype)
        for i in range(self.points.shape[1]):
            p[i] = self._splines[i](s)

        return p

    def sort(self, ids=[0, 1]):
        """sort using pointsort fortran module
        broken!"""

        # self.points[:,ids[0]], self.points[:,ids[1]], slist = pointsort(self.points[:,ids[0]], self.points[:,ids[1]])

        x, y, slist = reorder(self.points[:, ids[0]], self.points[:, ids[1]])

        slist -= 1
        self.points[:, :] = self.points[slist, :]

        # if self.nd > 2:
        #     idx = (set([0,1,2]) - set(ids)).pop()
        #     print 'warning: presently sorting is only done according to x and y'
        #     slist -= 1
        #     self.points[:, idx] = self.points[slist, idx]

    def split(self, s):
        """
        split the curve at curve fraction `s` into two new curves

        parameters
        ----------
        s: float
            curve fraction at which the curve will be split

        returns
        -------
        l1: array
            first curve
        l2: array
            second curve
        """
        isplit = np.where(abs(s - self.s) == abs(s - self.s).min())[0][0]
        P = self.interp_s(s)
        ds = P - self.points[isplit, :]
        try:
            np.testing.assert_almost_equal(np.max(abs(ds)), 0.0, 8)
            l1 = self.points[: isplit + 1, :].copy()
            l2 = self.points[isplit:, :].copy()
        except:
            l1 = np.vstack([self.points[: isplit + 1, :].copy(), P])
            l2 = np.vstack([P, self.points[isplit:, :].copy()])
        return l1, l2

    def divide_connector(self, ni):
        """
        divide curve into n sections of length `ni`

        parameters
        ----------
        ni: int
            size of curve sections

        returns
        -------
        cons: list
            list of new Curve instances
        """
        cons = []
        for i in range((self.points.shape[0] - 1) // (ni - 1)):
            c = Curve(
                points=self.points[(ni - 1) * i : (ni - 1) * (i + 1) + 1, :]
            )
            cons.append(c)

        return cons

    def join(self, segment):
        """
        Join this curve with another curve segment

        parameters
        ----------
        segment: object
            Curve object
        """
        points = segment.points.copy()
        for j in range(self.nd):
            if np.abs(self.points[-1, j] - points[0, j]) > 1.0e-14:
                points = points[::-1]
                if np.abs(self.points[-1, j] - points[0, j]) > 1.0e-14:
                    print("segments cannot be joined")
                    return

        points = np.append(self.points, points[1:], axis=0)
        # self.dist_ni = self.ni + points[1:].shape[0]
        # self.ni = self.ni + points[1:].shape[0]
        self.initialize(points)

    def invert(self):
        """invert the direction of the curve"""

        points = self.points[::-1]
        self.initialize(points)

    def rotate_x(self, deg, center=None):
        """
        rotate curve around an axis pointing in the x-direction

        parameters
        ----------
        deg: float
            rotation angle in degrees
        center: array
            center point of rotation
        """
        self._rotate(deg, RotX, center)

    def rotate_y(self, deg, center=None):
        """
        rotate curve around an axis pointing in the y-direction

        parameters
        ----------
        deg: float
            rotation angle in degrees
        center: array
            center point of rotation
        """

        self._rotate(deg, RotY, center)

    def rotate_z(self, deg, center=None):
        """
        rotate curve around an axis pointing in the z-direction

        parameters
        ----------
        deg: float
            rotation angle in degrees
        center: array
            center point of rotation
        """

        self._rotate(deg, RotZ, center)

    def _rotate(self, deg, Rot, center):
        if isinstance(center, type(None)):
            center = np.zeros([self.nd])
        degrad = deg * deg2rad
        rot = Rot(degrad)[: self.nd, : self.nd]
        points = (
            dotX(rot, (self.points - center), trans_vect=np.zeros([self.nd]))
            + center
        )
        self.initialize(points)

    def mirror(self, index, pos=0.0):
        """
        mirror the curve in either the x, y, or z direction

        parameters
        ----------
        index: int
            coordinate direction
        """

        if index > self.nd - 1:
            print("index larger than dimension of curve")
            return

        self.points[:, index] = (self.points[:, index] - pos) * -1.0 + pos

    def scale(self, x):
        """
        scale the curve

        parameters
        ----------
        x: float
            scaling factor
        """

        self.points *= x
        self.initialize(self.points)

    def translate_x(self, x):
        """
        translate the curve in the x-direction

        parameters
        ----------
        x: float
            translation
        """

        self.points[:, 0] += x
        self.initialize(self.points)

    def translate_y(self, x):
        """
        translate the curve in the y-direction

        parameters
        ----------
        x: float
            translation
        """

        self.points[:, 1] += x
        self.initialize(self.points)

    def translate_z(self, x):
        """
        translate the curve in the z-direction

        parameters
        ----------
        x: float
            translation
        """

        self.points[:, 2] += x
        self.initialize(self.points)

    def plot(
        self,
        color=(1, 0, 0),
        points=False,
        scale=None,
        vector=False,
        line_width=2.0,
        name=False,
    ):
        """
        plot the curve using Mayavi

        parameters
        -----------
        color: tuple
            tuple with color code
        points: bool
            show points along curve
        scale: float
            scale the points
        vector: bool
            show the direction of the curve
        line_width: float
            width of the line
        name: bool
            display the name of the curve in the plot
        """
        if scale is None:
            scale = self.smax / 200.0
        if self.nd == 2:
            x = np.zeros((self.points.shape[0], 3))
            x[:, :2] = self.points
        else:
            x = self.points
        from mayavi import mlab

        x = x.real
        mlab.plot3d(
            x[:, 0],
            x[:, 1],
            x[:, 2],
            tube_radius=None,
            color=color,
            line_width=line_width,
        )
        if points:
            mlab.points3d(
                x[:, 0],
                x[:, 1],
                x[:, 2],
                mode="sphere",
                color=(0, 0, 1),
                scale_factor=scale,
            )
            mlab.points3d(
                x[0, 0],
                x[0, 1],
                x[0, 2],
                mode="sphere",
                color=(1, 0.2, 1),
                scale_factor=scale,
            )
            mlab.points3d(
                x[-1, 0],
                x[-1, 1],
                x[-1, 2],
                mode="sphere",
                color=(1, 1, 1),
                scale_factor=scale,
            )
        if vector:
            # dp = 0.5*(self.dp[0] + self.dp[-1])
            mlab.plot3d(
                x[: self.ni // 2, 0],
                x[: self.ni // 2, 1],
                x[: self.ni // 2, 2],
                tube_radius=None,
                color=(0, 1, 0),
            )
        if name:
            pos = self.interp_s(0.5)
            width = np.max(
                np.min(0.01, len(self.name) * 0.005 * self.smax), 0.4
            )
            mlab.text3d(
                pos[0], pos[1], pos[2], self.name, scale=width, color=(1, 0, 0)
            )

    def copy(self):
        return copy.deepcopy(self)


class SegmentedCurve(Curve):
    """A curve that consists of multiple Curve segments."""

    def __init__(self, **kwargs):
        super(SegmentedCurve, self).__init__(**kwargs)

        self.segments = []

    def update(self):
        for i, seg in enumerate(self.segments):
            self._check_connectivity()
        self.build_curve()
        super(SegmentedCurve, self).initialize(self.points)

    def add_segment(
        self,
        segment=None,
        pos=-1,
        join_last=None,
        join_next=None,
        replace=False,
    ):
        """
        add a segment to the curve

        parameters
        ----------
        segment: object
            Curve object
        pos: int
            position in list of curves, default -1
        """
        if pos == -1:
            pos = len(self.segments)
        # if pos == 0:
        #     if join_last == None:
        #         join_last = np.zeros(2*self.nd)

        if replace:
            try:
                self.segments.pop(pos)
                self.remove("seg" + str(pos))
            except:
                pass

        name = "seg" + str(pos)
        if segment is not None:
            if isinstance(segment, (np.ndarray, list)):
                setattr(self, name, Curve(points=np.asarray(segment)))

            elif isinstance(segment, Curve):
                # something goes wrong in Windows with this
                # add statement, so for now we bypass it
                # and use setattr instead
                # self.add(name, Curve(points=segment.points))
                setattr(self, name, segment)
            seg = getattr(self, name)
            seg.bc = np.zeros((2, 2 * seg.nd))
            if join_last is not None:
                seg.bc[0, :] = np.asarray(join_last)
            # else:
            #     seg.bc = np.ones((2, 2*seg.nd))
            # seg.bc[0, :] = np.array((np.ones(seg.nd),np.ones(seg.nd))).flatten()
            if join_next is not None:
                seg.bc[1, :] = np.asarray(join_next)
            # else:
            #     seg.bc[1, :] = np.ones(2*seg.nd)

        self.segments.insert(pos, seg)

    def _check_connectivity(self):
        for i, seg in enumerate(self.segments):
            if sum(seg.bc[0, :]) > 0:
                try:
                    last = self.segments[i - 1]
                    seg._check_connectivity(0, last)
                except:
                    first = self.segments[-1]
                    seg._check_connectivity(0, first)

            if sum(seg.bc[1, :]) > 0:
                try:
                    next = self.segments[i + 1]
                    seg._check_connectivity(-1, next)
                except:
                    last = self.segments[0]
                    seg._check_connectivity(-1, last)

    def build_curve(self):
        if len(self.segments) == 0:
            return
        for i, seg in enumerate(self.segments):
            try:
                points = np.append(points, seg.points[:-1, :], 0)
            except:
                points = seg.points[:-1, :]
            _last = seg
            self.points = np.append(points, np.array([_last.points[-1, :]]), 0)

    def redistribute(self, dist=None, s=None, ni=None, linear=False):
        super(SegmentedCurve, self).redistribute(dist, s, ni, linear)


class Line(Curve):
    """
    Class for generating a 2D or 3D line

    parameters
    ----------
    p0: array
        array of size (2) or (3) with first point on line
    p1: array
        array of size (2) or (3) with last point on line
    ni: int
        number of points along line
    """

    def __init__(self, p0, p1, ni):
        points = np.zeros((ni, p0.shape[0]), dtype=p0.dtype)
        for d in range(p0.shape[0]):
            points[:, d] = np.linspace(p0[d], p1[d], ni, dtype=p0.dtype)

        super(Line, self).__init__(points)

        self.p0 = p0
        self.p1 = p1


class Circle(Curve):
    """
    Draws a circle or arc segment in 2D or 3D with center (0, 0, [0])
    and a given radius and number of points.

    parameters
    ----------
    radius: float
        circle radius.
    ang0: float
        starting angle in radians, default 0.
    ang1: float
        ending angle in radians, default 2*pi.
    ax: str
        axis about which to generate the circle, default z.
    ni: int
        number of points along arc.
    nd: int
        dimension of curve, 2 or 3.
    """

    def __init__(
        self,
        radius=1.0,
        ang0=0,
        ang1=2 * np.pi,
        p0=None,
        p1=None,
        ax="z",
        ni=200,
        nd=2,
    ):
        self.ni = ni
        self.nd = nd
        self._radius = radius
        self._ang0 = ang0
        self._ang1 = ang1
        self._ax = ax
        self._p0 = p0
        self._p1 = p1
        self._update = True
        points = self.get_points()
        super(Circle, self).__init__(points=points)

    @property
    def radius(self):
        return self._radius

    @property
    def ang0(self):
        return self._ang0

    @property
    def ang1(self):
        return self._ang1

    @property
    def ax(self):
        return self._ax

    def __enter__(self):
        self._update = False

    def __exit__(self):
        self._update = True

    def _set_new_val(self, name, value):
        old_val = copy.deepcopy(getattr(self, name))
        try:
            setattr(self, name, value)
            self.update()
        except:
            setattr(self, name, old_val)
            raise ValueError("Failed setting value %s=%s" % (name[1:], value))

    def update(self):
        if self._update:
            points = self.get_points()
            with self:
                self.initialize(points)

    def get_points(self):
        if self.ax == "z":
            ix = 0
            jx = 1
            kx = 2
        elif self.ax == "x":
            ix = 2
            jx = 1
            kx = 0
        elif self.ax == "y":
            ix = 0
            jx = 2
            kx = 1

        if isinstance(self._p0, np.ndarray):
            self._ang0 = np.arctan2(self._p0[jx], self._p0[ix])
        if isinstance(self._p1, np.ndarray):
            self._ang1 = np.arctan2(self._p1[jx], self._p1[ix])

        if self.ang0 < self.ang1:
            ang0 = self._ang1
            ang1 = self._ang0
        else:
            ang0 = self.ang0
            ang1 = self.ang1
        xy_point = self.radius * np.exp(1j * np.linspace(ang0, ang1, self.ni))
        if self.ang0 < self.ang1:
            xy_point = xy_point[::-1]
        points = np.zeros([self.ni, self.nd])
        if self.ax == "x":
            points[:, 1] = np.real(xy_point)
            points[:, 2] = np.imag(xy_point)
        elif self.ax == "y":
            points[:, 2] = np.real(xy_point)
            points[:, 0] = np.imag(xy_point)
        elif self.ax == "z":
            points[:, 0] = np.real(xy_point)
            points[:, 1] = np.imag(xy_point)
        else:
            raise ValueError("ax needs to be either: 'x', 'y' or 'z'")

        if isinstance(self._p0, np.ndarray):
            points[:, kx] = self._p0[kx]

        return points
