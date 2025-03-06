from math import factorial

import numpy as np

try:
    from scipy.optimize import least_squares

    new_lq = True
except:
    from scipy.optimize import leastsq

    new_lq = False
from collections import OrderedDict

from PGLW.main.curve import Curve
from PGLW.main.distfunc import distfunc
from PGLW.main.geom_tools import RotX, RotY, RotZ, calculate_length, dotX
from PGLW.main.naturalcubicspline import NaturalCubicSpline

deg2rad = np.pi / 180.0


def _C(n, k):
    return factorial(n) / (factorial(k) * factorial(n - k))


class BezierCurve(Curve):
    """
    Computes a 2D/3D bezier curve

    Parameters
    ----------
    CPs: array
        Bezier control points with shape ((nCP, nd)) where nCP are the number
        of control points and nd is the dimension of the curve (2 or 3).
    ni: int
        number of points on the curve
    """

    def __init__(self, ni=100, CPs=None):
        super(BezierCurve, self).__init__()

        if isinstance(CPs, np.ndarray):
            self.CPs = CPs
        else:
            self.CPs = np.array([])
        self.ni = ni

    def add_control_point(self, p):
        """
        add a control point to the curve

        parameters
        -----------
        p: array
            array of shape 2 or 3 with control point
        """

        C = list(self.CPs)
        C.append(list(p))
        self.CPs = np.asarray(C)

    def update(self):
        """
        generate the curve
        """
        try:
            self.nd = self.CPs.shape[1]
        except:
            raise RuntimeError("CPs needs to an array of shape (m, n)")

        if self.ni == 0:
            self.ni = 100

        points = self._compute(self.CPs)
        self._s = calculate_length(points)
        self._s /= self._s[-1]
        self.initialize(points)

    def _compute(self, C):
        points = np.zeros((self.ni, self.nd), dtype=C.dtype)
        self.t = np.linspace(0.0, 1.0, self.ni, dtype=C.dtype)
        # control point iterator
        _n = range(C.shape[0])

        for i in range(self.ni):
            s = self.t[i]
            n = _n[-1]
            for j in range(self.nd):
                for m in _n:
                    # compute bernstein polynomial
                    b_i = _C(n, m) * s**m * (1 - s) ** (n - m)
                    # multiply ith control point by ith bernstein polynomial
                    points[i, j] += C[m, j] * b_i
        return points

    # def _compute_dp(self):
    #     """
    #     computes the derivatives (tangent vectors) along a Bezier curve
    #     wrt ``t``.
    #
    #     there is no trivial analytic function to compute derivatives wrt
    #     to a given space interval, so we just spline and redistribute
    #     see: http://pomax.github.io/bezierinfo/
    #     """
    #     C = np.zeros((self.CPs.shape[0] - 1, self.nd), dtype=self.CPs.dtype)
    #     nC = C.shape[0]
    #     for i in range(nC):
    #         C[i, :] = float(nC) * (self.CPs[i + 1] - self.CPs[i])
    #
    #     dp = self._compute(C)
    #
    #     self.dp = np.zeros(self.points.shape, self.points.dtype)
    #     for n in range(dp.shape[1]):
    #         spl = self._splcls(self._s, dp[:, n])
    #         self.dp[:, n] = spl(self.s)
    #
    #     self.dp = np.array([self.dp[i, :] / np.linalg.norm(self.dp[i, :]) for i in range(self.dp.shape[0])], dtype=self.points.dtype)

    def elevate(self):
        k = self.CPs.shape[0]
        CPs = np.zeros((k + 1, self.nd))
        CPs[0] = self.CPs[0]
        CPs[-1] = self.CPs[-1]
        for i in range(1, k):
            CPs[i, :] = ((k - i) * self.CPs[i, :] + i * self.CPs[i - 1, :]) / k
        self.CPs = CPs
        self.update()

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
        super(BezierCurve, self)._rotate(deg, Rot, center)

        if isinstance(center, type(None)):
            center = np.zeros([self.nd])
        deg *= deg2rad
        rot = Rot(deg)[: self.nd, : self.nd]
        self.CPs = (
            dotX(rot, (self.CPs - center), trans_vect=np.zeros([self.nd]))
            + center
        )

    def mirror(self, index, pos=0.0):
        """
        mirror the curve in either the x, y, or z direction

        parameters
        ----------
        index: int
            coordinate direction
        """
        super(BezierCurve, self).mirror(index, pos)

        if index > self.nd - 1:
            print("index larger than dimension of curve")
            return

        self.CPs[:, index] = (self.CPs[:, index] - pos) * -1.0 + pos

    def scale(self, x):
        """
        scale the curve

        parameters
        ----------
        x: float
            scaling parameter
        """
        super(BezierCurve, self).scale(x)

        self.CPs *= x

    def translate_x(self, x):
        """
        translate the curve in the x-direction

        parameters
        ----------
        x: float
            translation
        """
        super(BezierCurve, self).translate_x(x)

        self.CPs[:, 0] += x

    def translate_y(self, x):
        """
        translate the curve in the y-direction

        parameters
        ----------
        x: float
            translation
        """
        super(BezierCurve, self).translate_y(x)

        self.CPs[:, 1] += x

    def translate_z(self, x):
        """
        translate the curve in the z-direction

        parameters
        ----------
        x: float
            translation
        """
        super(BezierCurve, self).translate_z(x)

        self.CPs[:, 2] += x

    def _check_connectivity(self, index, seg):
        """Enforce bcs through Bezier control points"""

        C = self.points
        ip = list(set([0, -1]) - set([index]))[0]

        # point connectivity
        if hasattr(seg, "CPs"):
            p = seg.CPs[ip]
        else:
            p = seg.points[ip]
        bc = self.bc[index, : self.nd]
        Ci = (1 - bc) * C[index, :] + bc * p
        self.CPs[index] = Ci

        # self.CPs[idp] = [self.CPs[idp, j] + (self.CPs[idp]-self.CPs[index]) * seg.dp[j] for j in range(self.nd)]

    def plot(
        self,
        color=(1, 0, 0),
        points=False,
        CPs=True,
        scale=0.00008,
        vector=False,
        name="",
    ):
        """
        plot the curve using Mayavi

        parameters
        ----------
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
        super(BezierCurve, self).plot(
            color=color, points=points, scale=scale, vector=vector, name=name
        )

        # plot CPs
        if CPs:
            from mayavi import mlab

            C = np.asarray(self.CPs)
            mlab.plot3d(
                C[:, 0], C[:, 1], C[:, 2], tube_radius=None, color=(0, 0, 1)
            )
            mlab.points3d(
                C[:, 0],
                C[:, 1],
                C[:, 2],
                mode="sphere",
                color=(0, 0, 1),
                scale_factor=scale,
            )


class SegmentedBezierCurve(BezierCurve):
    """
    nth order Bezier curve segments forming a continuous
    curve

    parameters
    ----------
    nseg: int
        number of segments.
    nC: int
        number of control points along each segment.
    nd: int
        dimension of curve.
    bcs: list
        list of boundary conditions at joints: 0 for C0, 1 for C1.
    """

    def __init__(self, nseg, nC, nd=2, bcs=[]):
        super(SegmentedBezierCurve, self).__init__()

        self.CPs = np.zeros((nseg * (nC - 1) + 1, nd))
        self.segments = OrderedDict()
        self.sizes = np.asarray([100] * nseg)
        self.nseg = nseg
        self.nC = nC

        self.bcs = bcs
        if len(bcs) == 0:
            self.bcs = [1.0] * (nseg - 1)

        for ii, i in enumerate(range(0, (nseg - 1) * (nC - 1) + 1, nC - 1)):
            b = BezierCurve()
            b.ni = self.sizes[ii]
            b.CPs = self.CPs[i : i + nC, :]
            self.segments["seg%i" % i] = b

    def update(self):
        self.dCP = np.zeros((self.CPs.shape[0] - 1, self.CPs.shape[1]))
        for i in range(self.CPs.shape[1]):
            self.dCP[:, i] = np.diff(self.CPs[:, i])

        # check connectivity
        for ii, i in enumerate(
            range(self.nC, self.nseg * (self.nC - 1) + 1, self.nC - 1)
        ):
            bc = self.bcs[ii] + 1
            self.CPs[i] = self.CPs[i - 1] + self.dCP[i - bc]

        for i, seg in enumerate(self.segments.values()):
            seg.ni = self.sizes[i]
            seg.update()

        self._build_curve()

    def _compute_dp(self):
        for i, seg in enumerate(self.segments.values()):
            try:
                points = np.append(points, seg.dp[:-1, :], 0)
            except:
                points = seg.dp[:-1, :]
            _last = seg
        points = np.append(points, np.array([_last.dp[-1, :]]), 0)
        self.dp = points

    def _build_curve(self):
        if len(list(self.segments.items())) == 0:
            return
        for i, seg in enumerate(self.segments.values()):
            try:
                points = np.append(points, seg.points[:-1, :], 0)
            except:
                points = seg.points[:-1, :]
            _last = seg
        points = np.append(points, np.array([_last.points[-1, :]]), 0)
        self._s = calculate_length(points)
        self._s /= self._s[-1]
        self.initialize(points)


class BezierCircle(BezierCurve):
    def __init__(
        self,
        radius=1.0,
        ang0=0,
        ang1=np.pi / 2.0,
        ax="z",
        ni=200,
        nd=2,
        degree=3,
    ):
        super(BezierCircle, self).__init__()
        rot = ang0
        phi = ang1 - ang0
        C1x = 1.0
        C1y = 4.0 / 3.0 * np.tan(phi / 4.0)
        C2x = np.cos(phi) + 4.0 / 3.0 * np.tan(phi / 4.0) * np.sin(phi)
        C2y = np.sin(phi) - 4.0 / 3.0 * np.tan(phi / 4.0) * np.cos(phi)

        self.CPs = np.zeros((4, nd))
        self.CPs[0, :2] = [1.0, 0.0]
        self.CPs[-1, :2] = [np.cos(phi), np.sin(phi)]
        self.CPs[1, :2] = [C1x, C1y]
        self.CPs[2, :2] = [C2x, C2y]
        self.CPs *= radius
        self.update()
        self.rotate_x(rot)
        for deg in range(degree - 3):
            self.elevate()


class FitBezier(object):
    """
    Fit a Bezier curve to a 2D/3D discrete curve


    Parameters
    ----------
    curve_in : Curve-object
        Array of 2D or 3D points to be fitted ((n,j)) where n is the number of points
        and j is 2 or 3.
    CPs : array_like
        List containing x-coordinate distribution of the control points.
    constraints: array_like
        List containing simplified constraints for the control points ((n,j)) where j is 2 or 3.
        e.g. [[0, 0], [1,0], [1,1], [0, 0]]. Note that end points will always be clamped.
    lsq_factor : float
        A parameter determining the initial step bound for the leastsq minimization
    lsq_epsfcn : float
        step length for the forward-difference approximation of the Jacobian
    lsq_xtol : float
        Relative error desired in the approximate solution.
    """

    def __init__(
        self,
        curve_in,
        CPs,
        constraints=None,
        lsq_factor=0.2,
        lsq_epsfcn=1e-8,
        lsq_xtol=1.0e-8,
    ):
        self.curve_in = curve_in
        self.curve_out = BezierCurve()
        self.curve_out.ni = curve_in.ni

        self.fix_x = False
        self.CPs = CPs
        self.constraints = constraints
        nCPs = CPs.shape[0]
        self.lsq_factor = lsq_factor
        self.lsq_epsfcn = lsq_epsfcn
        self.lsq_xtol = lsq_xtol

    def execute(self):
        if len(self.CPs) == 0:
            self.CPs = np.zeros((self.nCPs, self.curve_in.nd))
            for i in range(self.curve_in.nd):
                s = np.linspace(0.0, 1.0, self.nCPs)
                self.CPs[:, i] = np.interp(
                    s,
                    np.asarray(self.curve_in.s, dtype=np.float64),
                    np.asarray(self.curve_in.points[:, i], dtype=np.float64),
                )
        else:
            self.nCPs = self.CPs.shape[0]
            if np.sum(self.CPs[:, 1]) == 0.0:
                self.CPs[:, 1] = np.interp(
                    self.CPs[:, 0],
                    np.asarray(self.curve_in.points[:, 0], dtype=np.float64),
                    np.asarray(self.curve_in.points[:, 1], dtype=np.float64),
                )

        # anchor first and last CP to start/end points of curve
        self.CPs[0] = self.curve_in.points[0]
        self.CPs[-1] = self.curve_in.points[-1]

        # flatten the list
        self.parameters = list(self.CPs.flatten())

        # constraints
        if self.constraints.shape[0] == 0:
            self.constraints = np.ones((self.CPs.shape[0], self.curve_in.nd))
        # fix end points
        self.constraints[0] = 0.0
        self.constraints[-1] = 0.0

        # optionally fix all x-coordinates
        if self.fix_x:
            self.constraints[:, 0] = 0.0

        # flatten constraints
        self.cons = self.constraints.flatten()

        # remove fixed parameters from list of parameters to be fitted
        # and add to fixedparams list
        self.fixedparams = []
        self.delparams = []

        for i in range(len(self.cons)):
            if self.cons[i] == 0:
                self.fixedparams.append(self.parameters[i])
                self.delparams.append(i)

        for i in range(len(self.delparams)):
            del self.parameters[self.delparams[i] - i]

        self.iters = []
        if new_lq:
            res = least_squares(
                self.minfunc, self.parameters
            )  # ,full_output=1,factor=self.lsq_factor,
            # epsfcn=self.lsq_epsfcn,xtol=self.lsq_xtol)
        else:
            res_ = leastsq(
                self.minfunc,
                self.parameters,
                full_output=1,
                factor=self.lsq_factor,
                epsfcn=self.lsq_epsfcn,
                xtol=self.lsq_xtol,
            )
            (popt, pcov, res, errmsg, ier) = res_

        self.res = res
        # print('Bezier fit iterations: %i' % res['nfev'])

    def minfunc(self, params):
        # gymnastics to re-insert fixed parameters into list passed to BezierCurve
        ii = 0
        params = list(params)
        for i in range(len(self.cons)):
            if self.cons[i] == 0.0:
                params.insert(i, self.fixedparams[ii])
                ii += 1
        params = np.array(params).reshape(
            len(params) // self.curve_in.nd, self.curve_in.nd
        )
        self.curve_out.CPs = params
        self.curve_out.update()
        self.curve_out.redistribute(s=self.curve_in.s)
        self.iters.append(self.curve_out.points.copy())

        res = np.zeros((self.curve_in.ni, self.curve_in.nd))
        for i in range(self.curve_in.ni):
            res[i, :] = [
                (self.curve_in.points[i, j] - self.curve_out.points[i, j])
                for j in range(self.curve_in.nd)
            ]
        self.res = res.flatten()

        return self.res
