import copy
import pickle

import numpy as np
from numpy import newaxis as na
from scipy.interpolate import Akima1DInterpolator, CubicSpline, interp1d, pchip
from scipy.optimize import minimize

from PGLW.main.bezier import BezierCurve, FitBezier
from PGLW.main.curve import Curve, Line
from PGLW.main.erosion import ocean_erosion
from PGLW.main.geom_tools import act_tanh, calculate_length, curvature
from PGLW.main.naturalcubicspline import NaturalCubicSpline


class AirfoilShape(Curve):
    """
    Base class for airfoil shapes.

    The class automatically computes the LE and TE
    and can redistribute the points smoothly along the surface.
    Points along the surface need to be defined starting at the
    TE pressure side ending at the TE suction side.
    """

    def initialize(self, points, nd=None):
        if nd is not None and nd > points.shape[1]:
            points = np.vstack(
                (points.T, np.zeros(points.shape[0], dtype=points.dtype))
            ).T

        super(AirfoilShape, self).initialize(points)
        self.computeLETE()

    def _build_splines(self):
        self._splines = []

        for j in range(self.points.shape[1]):
            self._splines.append(self._splcls(self.s, self.points[:, j]))

    def computeLETE(self):
        """
        computes the leading and trailing edge of the airfoil.

        TE is computed as the mid-point between lower and upper TE points
        LE is computed as the point with maximum distance from the TE.
        """

        def _sdist(s):
            x = self._splines[0](s).real
            y = self._splines[1](s).real
            return -(
                ((x - self.TE[0].real) ** 2 + (y - self.TE[1].real) ** 2)
                ** 0.5
            )

        self.TE = np.zeros(self.nd)
        for i in range(self.nd):
            self.TE[i] = np.average(self.points[[0, -1], i])
        res = minimize(
            _sdist,
            (0.5),
            method="SLSQP",
            bounds=[(0, 1)],
            tol=1.0e-16,
            options={"eps": 1.0e-6},
        )

        self.sLE = res["x"][0]
        self.iLE = np.where(
            np.abs(self.s - self.sLE) == np.abs(self.s - self.sLE).min()
        )[0][0]
        xLE = self._splines[0](self.sLE)
        yLE = self._splines[1](self.sLE)
        self.LE = np.zeros(self.nd)
        self.LE[0] = xLE
        self.LE[1] = yLE
        if self.nd > 2:
            self.LE[2] = self._splines[2](self.sLE)
        self.chord = np.linalg.norm(self.LE - self.TE)
        self.curvLE = self._splcls(
            self.s, curvature(self.points / self.chord)
        )(self.sLE)

    def leading_edge_dist(self, ni):
        """function that returns a suitable normalized cell size based on airfoil LE curvature"""

        min_ds1 = 1.0 / ni * 0.1
        max_ds1 = 1.0 / ni * 0.5

        ds1 = max(
            (min_ds1 - max_ds1) / 30.0 * abs(self.curvLE) + max_ds1, min_ds1
        )

        return ds1

    def close_trailing_edge(self, close_te, ds_LE):
        # normalised trailing edge length
        len_TE = (
            np.sqrt(((self.points[-1, :] - self.points[0, :]) ** 2).sum())
            / self.main_seg.smax
        )
        # check whether TE is already closed
        if len_TE < 1e-10:
            print("TE is closed already and cannot be closed!")
            close_te = 0
        # automatic determination of cells to be used to close TE, such that it is similar to the
        # one used at the LE, if close_te=False it is not closed
        if isinstance(close_te, (bool)):
            if close_te:
                # estimate number of points on TE, such that the grid spacing is close to LE
                ni_TE = int(np.round(len_TE / ds_LE))
                # ensure there to be one point at least
                if ni_TE == 0:
                    ni_TE = 1
                close_te = ni_TE
            else:
                close_te = 0
        # close trailing edge
        if close_te > 0:
            # need at least three points to close TE
            close_te = max(close_te, 3)
            # to be able to split the TE an odd no. of points is requiered
            if close_te % 2 == 0:
                close_te += 1

            # construct the trailing edge segment, from suction to pressure side
            self.te_seg = Line(
                self.main_seg.points[-1, :],
                self.main_seg.points[0, :],
                close_te,
            )
            self.te_isplit = close_te // 2
        # storage
        self.ni_TE = close_te
        self.close_te = close_te

    def join_seg_points(self, segs=[]):

        points = segs[0].points
        if len(segs) > 1:
            segs = segs[1:]
            for seg in segs:
                points = np.append(points, seg.points, axis=0)
        # add trailing edge, first pressure side part and then suction
        if hasattr(self, "te_seg"):
            points = np.append(
                self.te_seg.points[self.te_isplit : -1], points, axis=0
            )
            points = np.append(
                points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
            )

        return points

    def join_points(self, segs=[]):

        points = segs[0]
        if len(segs) > 1:
            segs = segs[1:]
            for seg in segs:
                points = np.append(points, seg, axis=0)
        # add trailing edge, first pressure side part and then suction
        if hasattr(self, "te_seg"):
            points = np.append(
                self.te_seg.points[self.te_isplit : -1], points, axis=0
            )
            points = np.append(
                points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
            )

        return points

    def redistribute(
        self,
        ni,
        even=False,
        dist=None,
        dLE=False,
        dTE=-1.0,
        close_te=False,
        linear=False,
    ):
        """
        redistribute the points on the airfoil using fusedwind.lib.distfunc

        Parameters
        ----------
        ni : int
            total number of points along airfoil
        even : bool
            flag for getting an even distribution of points
        dist : list
            optional list of control points with the form
            [[s0, ds0, n0], [s1, ds1, n1], ... [s<n>, ds<n>, n<n>]]
            where\n
            s<n> is the normalized curve fraction at each control point,\n
            ds<n> is the normalized cell size at each control point,\n
            n<n> is the cell count at each control point.\n
            note: when dealing with open trailing edge airfoils, the points included
            in this list are the only ones taken into account. On the contrary, when
            closed trailing edge airfoils are to be meshed, the points of 'dist' are
            understood as additional control points (which are appended to the pre-defined
            logic for trailing edge sizing).
        dLE : float
            optional float specifying cell size at LE.
            If not specified, a suitable leading edge cell size is
            automaticallry calculated based on the local curvature
        dTE : float
            optional trailing edge cell size. If set to -1 the cell size will increase
            from the LE to TE according to the tanh distribution function used
            in distfunc. If set to 'dTE' the grid size is equal to the one used to
            discretize the trailing edge.
        close_te: int/bool
            close trailing edge with line segment consisting of n points if an integer,
            if bool and True the number of points will be determined automatically, such the
            grid spacing is similar to the one at the LE

        """
        # main segement initialized with input coordinates (essentially a copy)
        self.main_seg = Curve(
            points=self.points, spline=self.spline_type, compute_dp=False
        )
        # compute normalized LE cell size if not specified
        if dLE:
            ds_LE = dLE
        else:
            ds_LE = self.leading_edge_dist(ni)
        ds_TE = dTE
        # close TE with straight line
        self.close_trailing_edge(close_te, ds_LE)

        # no. of cells across main body (identical to ni if no TE closure)
        main_ni = (ni - 1) - (max(self.ni_TE - 1, 0)) + 1

        # determine mesh control points
        if dist == None:
            # even distribution
            if even:
                dTE = 1.0 / main_ni
                ds_LE = 1.0 / main_ni
            else:
                # match TE spacing on main_seg with spacing over TE
                if dTE == "dTE":
                    if hasattr(self, "te_seg"):
                        ds_TE = self.te_seg.ds[-1] / self.main_seg.smax
                    else:
                        print("No TE so no dTE, setting dTE=-1!")
                        ds_TE = -1
                # recompute LE spacing if some points used on TE (should we keep this?)
                if not dLE and (ni != main_ni):
                    ds_LE = self.leading_edge_dist(main_ni)
            dist = [
                [0.0, ds_TE, 1],
                [self.sLE, ds_LE, (main_ni - 1) // 2 + 1],
                [1.0, ds_TE, main_ni],
            ]
        # redistribute accordingly
        self.main_seg.redistribute(dist=dist, linear=linear)

        # add trailing edge segment if present
        points = self.join_seg_points(segs=[self.main_seg])

        # ensure the curve location of the LE is matching between the main segment and the profile
        # (a very small difference would otherwise persist)
        self.main_seg.sLE = self.sLE
        # reinitialize with new distribution
        self.initialize(points)
        # Outputs
        self.points = points
        self.ni = ni
        # some additional outputs needed for LER generation
        self.main_ni = main_ni
        if "ds_TE" in locals():
            self.ds_TE = ds_TE * self.main_seg.smax
            self.ds_LE = ds_LE * self.main_seg.smax
        else:
            # get mesh spacing info
            self.ds_TE = self.ds[-1]
            self.ds_LE = np.mean(self.ds[self.iLE - 1 : self.iLE + 1])

        return self

    def redistribute_chordwise(self, dist):
        """
        redistribute the airfoil according to a chordwise distribution
        """

        # self.redistribute(self.ni, even=True)
        iLE = np.argmin(self.points[:, 0])
        ni = dist.shape[0]
        dist = np.asarray(dist)
        points = np.zeros((dist.shape[0] * 2 - 1, self.points.shape[1]))

        # interpolate pressure side coordinates
        yps = self._splcls(
            self.points[: iLE + 1, 0][::-1], self.points[: iLE + 1, 1][::-1]
        )
        ps = yps(dist)
        # interpolate suction side coordinates
        yss = self._splcls(self.points[iLE:, 0], self.points[iLE:, 1])
        ss = yss(dist)
        points[: ni - 1, 0] = dist[::-1][:-1]
        points[ni - 1 :, 0] = dist
        points[:, 1] = np.append(ps[::-1][:-1], ss, axis=0)
        return AirfoilShape(points)

    def s_to_11(self, s):
        """
        Transform the s coordinates from AirfoilShape format:

        * s=0 at TE pressure side (lower surface)
        * s=1 at TE suction side (upper surface)

        to the s coordinates from the input definition:

        * s=0 at LE
        * s=1 at TE suction side (upper surface)
        * s=-1 at TE pressure side (lower surface)
        """

        if s > self.sLE:
            return (s - self.sLE) / (1.0 - self.sLE)
        else:
            return -1.0 + s / self.sLE

    def s_to_01(self, s):
        """
        Transform the s coordinates from the input definition:

        * s=0 at LE
        * s=1 at TE suction side (upper surface)
        * s=-1 at TE pressure side (lower surface)

        to the backend defintion compatible with AirfoilShape():

        * s=0 at TE pressure side (lower surface)
        * s=1 at TE suction side (upper surface)
        """
        if s >= 0.0:
            return s * (1.0 - self.sLE) + self.sLE
        else:
            return (1.0 + s) * self.sLE

    def gurneyflap(self, gf_height, gf_length_factor):
        """add a Gurney flap shaped using a tanh function"""

        if gf_height == 0.0:
            return
        # if the length is not specified it is set to 3 x gf_height
        gf_length = gf_length_factor * gf_height

        # identify starting point of the gf along the chord
        x_gf = 1.0 - gf_length
        id1 = (np.abs(x_gf - self.points[0 : self.ni // 2, 0])).argmin() + 1
        s = np.linspace(x_gf, self.points[0, 0], 100)
        smax = s[-1] - s[0]
        h = np.zeros(100)
        for i in range(100):
            h[i] = (
                min(
                    0.90 * gf_height,
                    gf_height * (-np.tanh((s[i] - s[0]) / smax * 3) + 1.0),
                )
            ) / 0.90
        h = h[::-1]
        self.gfs = s
        self.gfh = h

        # add the gf shape to the airfoil
        points = self.points.copy()
        for i in range(0, id1):
            points[i, 1] = points[i, 1] - np.interp(points[i, 0], s, h)

        return AirfoilShape(points)

    def flap(self, length, blendf, hingef, alpha):
        """
        Add a trailing edge flap. Computed by blending of the original airfoil and the rotated geometry around a hinge point.

        * length: normalized chordwise length of the flap
        * blendf: range where the partial blending between the original and flapped geometries will take place. Normalized by chord length
        * hingef: factor to locate the hinge point in the flapwise direction (0.0: suction side, 1.0: pressure side)
        * alpha: actuation angle (in degrees, positive when flapping up)
        """

        if length == 0.0:
            return

        pointsout = self.points.copy()
        arad = (alpha * np.pi) / 180.0

        # identify starting point of the flap along the chord
        position = 1.0 - length

        # find the location where chordwise blending should start/end
        #   x<xref1: original geometry
        #   xref1<x<xref2: partial blending
        #   x>xref2: flapped geometry
        xref1 = position - 0.5 * blendf
        xref2 = position + 0.5 * blendf

        # find hinge point
        h_p = np.interp(
            position,
            self.points[0 : int(self.ni / 2.0), 0][::-1],
            self.points[0 : int(self.ni / 2.0), 1][::-1],
        )
        h_s = np.interp(
            position,
            self.points[int(self.ni / 2.0) : self.ni, 0],
            self.points[int(self.ni / 2.0) : self.ni, 1],
        )
        h_h = (1.0 - hingef) * h_s + hingef * h_p

        # rotate the flap around hinge point
        rotx = (
            position
            + np.cos(arad) * (self.points[:, 0] - position)
            - np.sin(arad) * (self.points[:, 1] - h_h)
        )
        roty = (
            h_h
            + np.sin(arad) * (self.points[:, 0] - position)
            + np.cos(arad) * (self.points[:, 1] - h_h)
        )

        # apply blending function (original with rotated geometry)
        sred = (self.points[:, 0] - xref1) / (xref2 - xref1)
        bfact = 0.5 * (np.tanh(4.0 * (sred - 0.7) / (1.0 - 0.7)) + 1.0)
        pointsout[:, 0] = (1.0 - bfact) * self.points[:, 0] + bfact * rotx
        pointsout[:, 1] = (1.0 - bfact) * self.points[:, 1] + bfact * roty

        return AirfoilShape(pointsout)

    def open_trailing_edge(self, t):
        """
        add thickness to airfoil
        """

        t0 = np.abs(self.points[-1, 1] - self.points[0, 1])
        dt = (t - t0) / 2.0
        # linearly add thickness from LE to TE
        iLE = np.argmin(self.points[:, 0])
        xLE = self.points[iLE, 0]
        tlin = np.array(
            [np.linspace(xLE, self.TE[0], 100), np.linspace(0.0, dt, 100)]
        ).T

        tspline = self._splcls(tlin[:, 0], tlin[:, 1])

        ys = tspline(self.points[iLE:, 0]) + self.points[iLE:, 1]
        yp = -tspline(self.points[:iLE, 0][::-1])[::-1] + self.points[:iLE, 1]

        self.points[iLE:, 1] = ys
        self.points[:iLE, 1] = yp
        self.initialize(self.points)

    def interp_x(self, x, side):
        """
        interpolate s(x) for lower or upper side
        """
        if self.LE[0] < self.TE[0]:
            iLE = np.argmin(self.points[:, 0])
            iTEl = np.argmax(self.points[:iLE, 0])
            iTEu = np.argmax(self.points[iLE:, 0]) + iLE
            if x < self.points[iLE, 0]:
                return self.points[iLE, 1]
            elif x > self.TE[0]:
                if side == "lower":
                    return 0.0
                if side == "upper":
                    return 1.0
        else:
            iLE = np.argmax(self.points[:, 0])
            iTEl = np.argmin(self.points[:iLE, 0])
            iTEu = np.argmin(self.points[iLE:, 0]) + iLE
            if x > self.points[iLE, 0]:
                return self.sLE
            elif x < self.TE[0]:
                if side == "lower":
                    return 0.0
                if side == "upper":
                    return 1.0

        if side == "lower":
            # interpolate pressure side coordinates
            s = self.points[iTEl:iLE, 0]
            if s[0] > s[-1]:
                s = s[::-1]
                y = self.s[iTEl:iLE][::-1]
            else:
                y = self.s[iTEl:iLE]
            ix = np.where(np.diff(s) > 0)[0]
            spl = self._splcls(s[ix], y[ix])
            return spl(x)

        if side == "upper":
            # interpolate pressure side coordinates
            s = self.points[iLE:iTEu, 0]
            if s[0] > s[-1]:
                s = s[::-1]
                y = self.s[iLE:iTEu][::-1]
            else:
                y = self.s[iLE:iTEu]
            ix = np.where(np.diff(s) > 0)[0]
            spl = self._splcls(s[ix], y[ix])
            return spl(x)

    def add_LE_topography(
        self,
        x_topo,
        h_topo,
        ni_total,
        ni_topo,
        topo_spline_type="akima",
        edge_smooth=None,
    ):
        """
        Wraps topography around existing aerofoil. The topology is resplined and rediscretised
        following the topo curve lenght according to the number of points specifed (ni_topo).

        x_topo: 1D-array(float)
            in-plane coordinate of topography to be added. The topography is wrapped around the
            existing aerofoil, where the LE is defined as the origin and the curve length is
            +ve increasing towards the suction side (clockwise definition). The start and end
            points of the topology along the aerofoils curve length are defined by x_topo,
            ie s_start=x_topo[0] and s_end=x_topo[-1].
        h_topo: 1D-array(float)
            out-of-plane coordinate of topography to be added, specifies height of damage
            at x coordinates specified
        ni_total: integer [-] multiple of 8
            grid cells to be used along the aerofoil including the cells used on the topology
        ni_topo: integer [-] multiple of 8
            grid cells to be used along topology
        topo_spline_type: string
            spline type to be used to spline the topology, use PGL curve spline types
        edge_smooth: float
            smoothing lenght scale (not normalised) to be used over the edges of the topo
            to ensure smooth connection to the base aerofoil. Uses a hyperbolic tangent
            to activate/deactivate topo region within the edge_smooth length.
        """
        # ---- topology coordinates
        # determine how much of the LE should be covered
        ni_h = len(h_topo)
        # resolution of input roughness patch
        L_topo = np.ptp(x_topo)
        dx_topo = L_topo / (ni_h - 1)
        # approx. resolution in surface mesh
        ds_topo = L_topo / (ni_topo - 1)
        # start and end positions
        s_start = x_topo[0]
        s_end = x_topo[-1]

        # ---- topology segment
        # smooth towards edges to match original grid
        if edge_smooth is not None:
            l_smooth = edge_smooth
            h_smooth = h_topo * act_tanh(
                x_topo, l_smooth, x_topo[0] + l_smooth, switch="on"
            )
            h_smooth = h_smooth * act_tanh(
                x_topo, l_smooth, x_topo[-1], switch="off"
            )
        else:
            h_smooth = h_topo.copy()
        # use original spline if not specified, however watch out for overshoots in higher order methods
        if topo_spline_type is None:
            topo_spline_type = self.spline_type
        # make topology spline, curvilinear
        topo_seg = Curve(
            points=np.c_[x_topo, h_smooth],
            spline=topo_spline_type,
            compute_dp=False,
        )
        topo_seg.redistribute(ni=ni_topo)
        # start and end of the erosion in main_seg coordinate system
        self.s_start = self.main_seg.sLE + s_start / self.main_seg.smax
        self.s_end = self.main_seg.sLE + s_end / self.main_seg.smax
        # no. of points on main body
        if hasattr(self, "te_seg"):
            ni_main = (ni_total - 1) - (self.ni_TE - 1) + 1
        else:
            ni_main = (ni_total - 1) + 1
        ni_uneroded = (ni_main - 1) - (ni_topo - 1) + 1
        # half points on the pressure and the other on the suction side (python indexing!)
        i_start = (ni_uneroded - 1) // 2
        i_end = i_start + (ni_topo - 1)

        # ---- initial redistribution to make sure start and end are in the right place
        # the region over the LE is a dummy region as the topo is meshed following curvilinear coords,
        # at the connection to the main body it is set to an average mesh size, which should be fine towards
        # the edges as there is little out-of-plane movement there
        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [self.s_start, ds_topo / self.main_seg.smax, i_start + 1],
            [self.s_end, ds_topo / self.main_seg.smax, i_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, ni_main],
        ]
        # keep a copy of the original definition
        main_seg = copy.deepcopy(self.main_seg)
        main_seg._compute_dp_flag = True
        main_seg.redistribute(dist=dist)
        # redefine the point distribution along the surface according to topo distribution so we
        # can apply the normal perturbation in the right locations. For that we construct a curve
        # for the clean aerofoil and then redistribute the points according to the projected location
        # along the curve.
        eroded_seg = Curve(
            points=main_seg.points[i_start : i_end + 1],
            spline=topo_spline_type,
            compute_dp=True,
        )
        self._eroded_seg_info = [
            i_start,
            i_end,
            copy.deepcopy(eroded_seg),
            topo_spline_type,
        ]
        x2s_topo = (topo_seg.points[:, 0] - topo_seg.points[0, 0]) / (
            topo_seg.points[-1, 0] - topo_seg.points[0, 0]
        )
        eroded_seg.redistribute(s=x2s_topo)
        # nomal vector pointing outwards
        normals = np.array([-eroded_seg.dp[:, 1], eroded_seg.dp[:, 0]]).T
        # apply LE topo, now at the correct locations along the curve
        erosion = eroded_seg.points.copy()
        erosion += topo_seg.points[:, 1][:, na] * normals
        # copy clean aerofoil and spline in eroded segment
        eroded_main = main_seg.points.copy()
        eroded_main[i_start : i_end + 1] = erosion
        # finally compute segment that contains erosion
        self.clean_main_seg = main_seg
        self.eroded_main_seg = Curve(
            points=eroded_main, spline=topo_spline_type, compute_dp=True
        )
        # aerofoil points
        points = self.join_seg_points(segs=[self.eroded_main_seg])
        clean_points = self.join_seg_points(segs=[self.clean_main_seg])
        # add TE if selected
        if hasattr(self, "te_seg"):
            for i in range(2):
                self._eroded_seg_info[i] += self.te_isplit
        self.points = points
        self.clean_points = clean_points
        self.initialize(self.points)

    def bistep(
        self,
        s_start,
        s_end,
        ni,
        h_step,
        ds_step,
        ni_step,
        ni_rat=[0.25, 0.75],
        bsize=None,
    ):
        """
        Add or remove material from the airfoil. This creates steps at the
        end of the perturbed region. The difference between step and slot
        lies in the positioning of the defect.

        s_start: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_end: float [m]
            curve location where perturbation ends. Defined from LE.
            +ve increasing towards suction side.
        h: float [m]
            size of material addition (+ve) or removal (-ve)
        ds_h: float [m]
            grid size over h
        ni_step: int [-]
            additional grid cells to resolve perturbed region
        """
        # translate into normalised coordinates
        smax = self.main_seg.smax
        self.s_start = self.main_seg.sLE + s_start / smax
        self.s_end = self.main_seg.sLE + s_end / smax
        # additional cells used over aerofoil
        ni_aero = ni - np.sum(ni_step)
        # find airfoil points closest to start and end
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        # add points accordingly
        ni_rat /= np.sum(ni_rat)
        i_start += int(ni_rat[0] * ni)
        i_end += int(ni_rat[1] * ni)
        if bsize is not None:
            nTE2 = (self.ni_TE - 1) / 2.0
            i_start = int(np.round((i_start - nTE2) / bsize) * bsize - nTE2)
            i_end = int(np.round((i_end - nTE2) / bsize) * bsize - nTE2)
            print("### istart, iend ", i_start, i_end)
        # standard is half the no. of points are used at the LE
        i_LE = self.main_ni // 2 + 1
        # determine position of LE relative to step locations and add points if needed
        reloc = (self.main_seg.sLE - self.s_start) / (
            self.s_end - self.s_start
        )
        # no extra points if LE in front of steps
        if reloc > 0.0:
            # if afer steps at all points
            if reloc >= 1.0:
                i_LE += ni
            # otherwise add fraction
            else:
                i_LE += int(reloc * np.ptp(ni_rat) + ni_rat[0])
        # point distribution
        dist = [
            [0.0, self.ds_TE / smax, 1],
            [self.s_start, ds_step[0][0] / smax, i_start + 1],
            [self.main_seg.sLE, self.ds_LE / smax, i_LE],
            [self.s_end, ds_step[1][-1] / smax, i_end + 1],
            [1.0, self.ds_TE / smax, self.main_ni + ni_aero],
        ]
        # sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        # get updated aerofoil points
        main_seg = copy.deepcopy(self.main_seg)
        main_seg._compute_dp_flag = True
        main_seg.redistribute(dist=dist)
        # get step points and normals
        step_normals = (np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T)[
            [i_start, i_end], :
        ]
        step_locs = main_seg.points[[i_start, i_end], :]
        # create steps by creating orthogonal lines
        perps = []
        for i in [0, -1]:
            # follow curve direction
            if i == 0:
                p0 = step_locs[i]
                p1 = step_locs[i] + h_step[i] * step_normals[i]
            else:
                p0 = step_locs[i] + h_step[i] * step_normals[i]
                p1 = step_locs[i]
            ll = Line(p0, p1, ni_step[i] + 1)
            dist = [
                [0.0, ds_step[i][0] / ll.smax, 1],
                [1.0, ds_step[i][1] / ll.smax, ni_step[i] + 1],
            ]
            ll.redistribute(dist=dist)
            perps.append(ll)
        # segment between steps
        step_seg = Curve(points=main_seg.points[i_start : i_end + 1, :])
        step_seg.redistribute(
            dist=[
                [0.0, ds_step[0][1] / step_seg.smax, 1],
                [1.0, ds_step[1][0] / step_seg.smax, step_seg.ni],
            ]
        )
        # displace points according to step size
        normals = np.array([-step_seg.dp[:, 1], step_seg.dp[:, 0]]).T
        step_points = (
            step_seg.points
            + (step_seg.s * (h_step[1] - h_step[0]) + h_step[0])[:, na]
            * normals
        )

        # assemble all regions
        points = self.join_points(
            segs=[
                main_seg.points[:i_start],
                perps[0].points,
                step_points[1:-1],
                perps[1].points,
                main_seg.points[i_end + 1 :],
            ]
        )

        self.perps = perps
        self.points = points
        self.initialize(self.points)

        return self

    # Implementation of different LER types
    def bite(self, bite):
        """
        Create over- (bite > 0) and underbite (bite < 0)

        bite: float [m]
            size of over or underbite
        """
        if bite > 0.0:
            self.overbite(bite)
        else:
            self.underbite(abs(bite))

    def overbite(self, overbite):
        """
        Create overbite by moving the pressure side downstream

        overbite: float [m]
            size of overbite
        """
        iLE = np.argmin(self.main_seg.points[:, 0])
        points_lower = self.main_seg.points[: iLE + 1, :].copy()
        points_upper = self.main_seg.points[iLE:, :].copy()
        # Determine the no. of points needed on the overbite
        ni_over = max(4, int(np.ceil(abs(overbite) / self.ds_LE) / 2)) + 2
        if ni_over % 2 != 0:
            ni_over += 1
        ni_upper = points_lower.shape[0] - ni_over / 2
        ni_lower = points_upper.shape[0] - ni_over / 2
        ni_over += 1
        self.ni_over = ni_over
        # Move lower part of airfoil streamwise
        points_lower[:, 0] += overbite
        low = Curve(
            points=points_lower, spline=self.spline_type, compute_dp=False
        )
        up = Curve(
            points=points_upper, spline=self.spline_type, compute_dp=False
        )
        # Find the TE of the shifted airfoil
        yorig_TE = self.main_seg.points[0, 1]
        xorig_TE = self.main_seg.points[0, 0]
        yrot_TE = 1.0
        ylim = 1e-5
        dth = ylim / 100.0 * 180.0 / np.pi
        th = 0.0

        # Rotate the spline about the LE
        while abs(yorig_TE - yrot_TE) > ylim:
            low.rotate_z(-th, center=points_lower[-1, :])
            self.fit = self._splcls(low.points[::-1, 0], low.points[::-1, 1])
            yrot_TE = self.fit(xorig_TE)
            th += dth
        # Find the s location for that x position
        fit = self._splcls(low.points[::-1, 0], low.s[::-1])
        srot_TE = fit(xorig_TE)

        # Change the point distribution to fit the new curve length
        # The first part is only a dummy section which will be removed later
        ni_dum = 10

        ds = min(self.ds_LE, abs(overbite) / ni_over)

        dist = [
            [0.0, self.ds_TE / low.smax, 1],
            [srot_TE, self.ds_TE / low.smax, 1 + ni_dum],
            [1.0, ds / low.smax, ni_lower + ni_dum],
        ]
        low.redistribute(dist=dist)
        dist = [[0, ds / up.smax, 1], [1.0, self.ds_TE / up.smax, ni_upper]]
        up.redistribute(dist=dist)
        # Create trailing edge
        self.te_seg = Line(
            up.points[-1, :], low.points[ni_dum, :], self.ni_TE + 2
        )

        # Create overhang
        self.over_seg = Line(low.points[-1, :], up.points[0, :], ni_dum)
        self.over_seg.redistribute(
            dist=[
                [0.0, ds / self.over_seg.smax, 1],
                [1.0, ds / self.over_seg.smax, ni_over],
            ]
        )

        self.points_lower = points_lower
        self.points_lower_rot = low.points
        self.low = low
        self.points_upper = up.points

        # Assemble mdofied profile
        points = np.append(
            self.te_seg.points[self.te_isplit :],
            low.points[1 + ni_dum :],
            axis=0,
        )
        points = np.append(points, self.over_seg.points[1:], axis=0)
        points = np.append(points, up.points[1:], axis=0)
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.points = points
        self.initialize(self.points)

        return self

    def underbite(self, underbite):
        """
        Create underbite by moving the suction side downstream

        underbite: float [m]
            size of underbite
        """
        iLE = np.argmin(self.main_seg.points[:, 0])
        points_lower = self.main_seg.points[: iLE + 1, :].copy()
        points_upper = self.main_seg.points[iLE:, :].copy()
        # Determine the no. of points needed on the overbite
        ni_over = max(4, int(np.ceil(abs(underbite) / self.ds_LE) / 2)) + 2
        if ni_over % 2 != 0:
            ni_over += 1
        ni_upper = int(points_lower.shape[0] - ni_over / 2)
        ni_lower = int(points_upper.shape[0] - ni_over / 2)
        ni_over += 1
        self.ni_over = ni_over
        # Move lower part of airfoil streamwise
        points_upper[:, 0] += underbite
        low = Curve(
            points=points_lower, spline=self.spline_type, compute_dp=False
        )
        up = Curve(
            points=points_upper, spline=self.spline_type, compute_dp=False
        )
        self.low = low
        self.up = up

        # Find the TE of the shifted airfoil
        yorig_TE = self.main_seg.points[-1, 1]
        xorig_TE = self.main_seg.points[-1, 0]
        yrot_TE = 1.0
        ylim = 1e-5
        dth = ylim / 100.0 * 180.0 / np.pi
        th = 0.0
        # Rotate the spline about the LE
        while abs(yorig_TE - yrot_TE) > ylim:
            up.rotate_z(-th, center=points_upper[0, :])
            self.fit = self._splcls(up.points[:, 0], up.points[:, 1])
            yrot_TE = self.fit(xorig_TE)
            th += dth
        # Find the s location for that x position
        fit = self._splcls(up.points[:, 0], up.s)
        srot_TE = fit(xorig_TE)
        self.up2 = up

        # Change the point distribution to fit the new curve length
        # The first part is only a dummy section which will be removed later
        ni_dum = 10

        ds = min(self.ds_LE, abs(underbite) / ni_over)

        dist = [[0, self.ds_TE / low.smax, 1], [1.0, ds / low.smax, ni_lower]]
        low.redistribute(dist=dist)
        dist = [
            [0, ds / up.smax, 1],
            [srot_TE, self.ds_TE / up.smax, ni_upper],
            [1.0, self.ds_TE / up.smax, ni_upper + ni_dum],
        ]
        up.redistribute(dist=dist)

        # Create trailing edge
        self.te_seg = Line(
            up.points[ni_upper - 1, :], low.points[0, :], self.ni_TE + 2
        )

        # Create overhang
        self.over_seg = Line(low.points[-1, :], up.points[0, :], ni_dum)

        self.over_seg.redistribute(
            dist=[
                [0.0, ds / self.over_seg.smax, 1],
                [1.0, ds / self.over_seg.smax, ni_over],
            ]
        )

        self.points_upper = points_upper
        self.points_upper_rot = up.points
        self.low = low
        self.points_lower = low.points
        self.ni_upper = ni_upper

        # Assemble mdofied profile
        points = np.append(
            self.te_seg.points[self.te_isplit :], low.points[1:], axis=0
        )
        points = np.append(points, self.over_seg.points[1:], axis=0)
        points = np.append(points, up.points[1:ni_upper], axis=0)
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )
        self.points = points
        self.initialize(self.points)

        return self

    def wavy(self, s_start, s_end, act_len, amp, lam, ni):
        """
        Create sinusoidal variations in airfoil surface.
        Variation oscillates around the original shape.

        s_start: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_end: float [m]
            curve location where perturbation ends. Defined from LE.
            +ve increasing towards suction side.
        act_len: float [m]
            transition length between undisturbed and disturbed region.
        amp: float [m]
            amplitude of oscillation
        lam: float [m]
            wave length of oscillation
        ni: integer [-] multiple of 8
            additional grid cells to resolve perturbed region
        """
        self.s_start = self.main_seg.sLE + s_start / self.main_seg.smax
        self.s_end = self.main_seg.sLE + s_end / self.main_seg.smax
        slen = self.s_end - self.s_start
        # Change point distribution
        main_ni = self.main_ni
        main_seg = self.main_seg.copy()
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        i_LE = main_ni // 2 + 1
        # Extra points are mostly concentrated in the oscillating area,
        # but two eigth are placed outside the region as well
        ni_o = ni // 8
        # Depending where the region is, some points need to be added
        # at the LE sto leave the intial point distribution unaffected.
        if self.s_start < self.main_seg.sLE:
            i_LE += 4 * ni_o
        if self.s_end < self.main_seg.sLE:
            i_LE += 4 * ni_o
        main_ni = main_ni + ni
        i_start += ni_o
        i_end += 7 * ni_o
        ds = slen / ni
        # Increase resolution in perturbed area
        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [self.s_start, ds / self.main_seg.smax, i_start + 1],
            [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE + 1],
            [self.s_end, ds / self.main_seg.smax, i_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, main_ni],
        ]
        # Sort dist by the curve length
        dist = sorted(dist, key=lambda x: x[0])
        self.dist = dist
        self.ds = ds * self.main_seg.smax

        main_seg._compute_dp_flag = True
        main_seg.redistribute(dist=dist)
        # Scaling
        lam /= main_seg.smax
        act_len /= main_seg.smax
        s = main_seg.s
        # Perturbation in the curve normal direction
        dn = amp / 2 * np.sin(2 * np.pi * s / lam)
        # print(dn)
        # Activation function
        tanc = 1.0 / act_len
        activ = (np.tanh(4 * tanc * (s - self.s_start)) + 1) / 2 - (
            np.tanh(4 * tanc * (s - self.s_end)) + 1
        ) / 2
        # Final perturbation
        dn *= activ
        normals = np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T

        wavy = np.zeros(normals.shape[:])
        for i in range(dn.shape[0]):
            # print('normals[i,:]*dn[i]',normals[i,:]*dn[i])
            wavy[i, :] = normals[i, :] * dn[i] + main_seg.points[i, :]
        self.wavy = wavy
        # Assemble profile
        points = np.append(
            self.te_seg.points[self.te_isplit :], wavy[1:], axis=0
        )
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )
        self.points = points
        self.initialize(self.points)

        return self

    def step(self, s_start, s_end, h, ds_h, ni_step):
        """
        Add or remove material from the airfoil. This creates steps at the
        end of the perturbed region. The difference between step and slot
        lies in the positioning of the defect.

        s_start: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_end: float [m]
            curve location where perturbation ends. Defined from LE.
            +ve increasing towards suction side.
        h: float [m]
            size of material addition (+ve) or removal (-ve)
        ds_h: float [m]
            grid size over h
        ni_step: int [-]
            additional grid cells to resolve perturbed region
        """
        # Translate into normalised coordinates
        self.s_step_start = self.main_seg.sLE + s_start / self.main_seg.smax
        self.s_step_end = self.main_seg.sLE + s_end / self.main_seg.smax
        # Find the number of grid points per step
        self.ni_h = (
            int(max(np.round(abs(h) / ds_h), np.round(abs(h) / self.ds_LE)))
            + 1
        )
        self.ds_h = ds_h
        # Additional points not used in the step are used over the airfoil
        # (Make sure there are enough points to allow this)
        ni_step = ni_step - 2 * (self.ni_h - 1)
        # Find airfoil points closest to start and end
        i_step_start = np.argmin(abs(self.s_step_start - self.main_seg.s))
        i_step_end = np.argmin(abs(self.s_step_end - self.main_seg.s))
        # Point ratio
        ni_rat = np.array(
            [
                i_step_start,
                i_step_end - i_step_start,
                self.main_ni - i_step_end,
            ]
        )
        ni_rat = ni_rat / self.main_ni
        # Weight the point ratio (giving most weight to perturbed area)
        ni_step_rat = np.array([1, 8, 1]) * ni_rat
        ni_step_rat /= sum(ni_step_rat)
        ni_step_rat = np.round(ni_step * ni_step_rat)
        # Ensure total no. of points does not exceed the no. specified
        ni_step_rat[1] += ni_step - sum(ni_step_rat)
        # New no. of points
        main_ni = self.main_ni + ni_step
        main_seg = self.main_seg.copy()
        # New point defintion
        i_step_start = int(i_step_start + ni_step_rat[0])
        i_step_end = int(i_step_end + sum(ni_step_rat[0:2]))

        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [
                self.s_step_start,
                self.ds_h / self.main_seg.smax,
                i_step_start + 1,
            ],
            [
                self.main_seg.sLE,
                self.ds_LE / self.main_seg.smax,
                main_ni // 2 + 1,
            ],
            [self.s_step_end, self.ds_h / self.main_seg.smax, i_step_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, main_ni],
        ]
        # Sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        main_seg.redistribute(dist=dist)
        self.step = main_seg

        # Apply disturbance normal to curve
        main_seg._compute_dp()
        normals = np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T
        step_points = (
            main_seg.points[i_step_start : i_step_end + 1, :]
            + h * normals[i_step_start : i_step_end + 1, :]
        )
        # Create the normal lines marching from original curve
        step1 = np.zeros((self.ni_h, 2))
        step2 = np.zeros((self.ni_h, 2))
        for i in range(self.ni_h):
            step1[i, :] = (
                np.sign(h) * i * self.ds_h * normals[i_step_start, :]
                + main_seg.points[i_step_start, :]
            )
        for i in range(self.ni_h):
            step2[i, :] = (
                np.sign(h) * i * self.ds_h * normals[i_step_end, :]
                + main_seg.points[i_step_end, :]
            )
        # Assemble pertubed region
        step_points = np.append(step1, step_points[1:], axis=0)
        step_points = np.append(step_points[:-1], step2[::-1], axis=0)
        step_points = np.append(
            main_seg.points[:i_step_start], step_points, axis=0
        )
        step_points = np.append(
            step_points, main_seg.points[i_step_end + 1 :], axis=0
        )
        # Assemble profile
        points = np.append(
            self.te_seg.points[self.te_isplit :], step_points[1:], axis=0
        )
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )
        self.i_step_start = i_step_start
        self.i_step_end = i_step_end
        self.points = points
        self.initialize(self.points)

        return self

    def moveLE(self, x_start, dy):
        """
        Moves the LE up (dy > 0) or down (dy < 0) in the y direction

        x_start: float [m]
            x location where to start movement of LE
        dy: float [m]
            movement of LE in the y direction
        """
        points = self.points.copy()
        x = x_start - points[:, 0]
        # Range of x
        dx = np.amax(x)
        x /= dx
        # Leave y value untouched downstream of x location
        x[x < 0] = 0
        # cubic y perturbation growth towards LE
        dypoints = x**2
        dypoints *= dy
        self.dypoints = dypoints
        self.x = x

        # Final perturbed airfoil
        points[:, 1] += dypoints
        self.points = points
        self.initialize(self.points)

        return self

    def flatsanding(self, s_mid, s_len, ni):
        """
        Introduces a flat region on airfoil

        s_mid: float [m]
            curve location in middle of perturbation. Defined from LE.
            +ve increasing towards suction side.
        s_len: float [m]
            length of flat region
        ni: int [-] (multiple of 4)
            additional no. of cells resolving feature
        """
        # Normalised start and end of flat region
        self.s_start = (
            self.main_seg.sLE + (s_mid - s_len / 2) / self.main_seg.smax
        )
        self.s_end = (
            self.main_seg.sLE + (s_mid + s_len / 2) / self.main_seg.smax
        )
        main_ni = self.main_ni
        main_seg = self.main_seg.copy()
        # Point no. at feature ends
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        # Distribute additional points around the feature ends
        i_LE = main_ni // 2 + 1
        ni_q = ni // 4
        # Adjust the no. of points at the LE
        if self.s_start < self.main_seg.sLE:
            i_LE += 2 * ni_q
        if self.s_end < self.main_seg.sLE:
            i_LE += 2 * ni_q
        # Add additional points to the original
        main_ni = main_ni + ni
        i_start += ni_q
        i_end += 3 * ni_q
        # Grid size at the ends of the feature (either the same as at LE or evenly spaced)
        ds = min(self.ds_LE, s_len / ni)
        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [self.s_start, ds / self.main_seg.smax, i_start + 1],
            [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE],
            [self.s_end, ds / self.main_seg.smax, i_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, main_ni],
        ]
        # Sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        self.dist = dist
        main_seg.redistribute(dist=dist)
        # Flat region
        flat = Line(
            main_seg.points[i_start, :],
            main_seg.points[i_end, :],
            i_end - i_start + 1,
        )
        dist = [[0.0, ds / flat.smax, 1], [1, ds / flat.smax, flat.ni]]
        flat.redistribute(dist=dist)

        # Assemble airfoil with TE closure
        points = np.append(
            self.te_seg.points[self.te_isplit :],
            main_seg.points[1 : i_start + 1],
            axis=0,
        )
        points = np.append(points, flat.points[1:], axis=0)
        points = np.append(points, main_seg.points[i_end + 1 :], axis=0)
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.flat = flat
        self.points = points
        self.initialize(self.points)

        return self

    def rough_paras(self, s_len, ks):
        """
        Computes the inputs to the roughness box for input.dat, for
        symmetric roughness about the LE. It returns the edge points of the
        roughness box in a np.array self.box and the roughness length as
        self.rough_len.

        s_len: float [m]
            length of roughness on each side of the LE
        ks: float [m]
            Nikuradse equivalent sand grain roughness
        """
        self.s_start = self.main_seg.sLE - s_len / self.main_seg.smax
        self.s_end = self.main_seg.sLE + s_len / self.main_seg.smax
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        points = self.main_seg.points.copy()
        self.i = np.array([i_start, i_end])
        xmax = (points[i_start, 0] + points[i_end, 0]) / 2.0
        c = points[:, 0].max() - points[:, 0].min()
        xmin = points[:, 0].min()
        ymin = points[:, 1].min()
        ymax = points[:, 1].max()
        buf = 0.05 * c
        self.box = np.array([xmin - buf, xmax, ymin - buf, ymax + buf])
        # In Knopp's roughness model the roughness is given by
        d0 = 0.03 * ks
        self.rough_len = d0

        return self

    def roughpatch_paras(self, s_step, s_len, ks, enforce_dir=True):
        """
        Similar to rough_paras but now the start location of the roughness can be
        set anywhere along the airfoil. Returns self.box_up and self.box_low
        instead of a single box for each side of the airfoil. If the roughness does
        not cross the LE (always True if enforce_dir=True) then box_low=box_up.

        s_step: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_len: float [m]
            length of roughness patch
        ks: float [m]
            Nikuradse equivalent sand grain roughness
        enforce_dir: bool
            If "True" the end point of the roughpatch is always placed towards the TE i.e.
            roughness will not cross the LE. This is not the case when "False" then s_len
            is just added to the start location and if s_step sufficiently close to the LE
            and s_len long enough the LE is crossed by the patch. This is also why the output
            of this function is an upper and lower roughness box, one for the suction and the
            other for the pressure side. If the LE is not crossed both boxes are identical.

        """
        # Intialize roughness box such that they do not influence the airfoil
        self.box_up = np.array([5.0, 5.1, 5.0, 5.1])
        self.box_low = np.array([5.0, 5.1, 5.0, 5.1])

        # Translate into normalised coordinates
        sstart = self.main_seg.sLE + s_step / self.main_seg.smax
        if enforce_dir:
            # place end point towards TE
            send = (
                self.main_seg.sLE
                + (s_step + np.sign(s_step) * s_len) / self.main_seg.smax
            )
        else:
            send = self.main_seg.sLE + (s_step + s_len) / self.main_seg.smax
        if sstart < send:
            self.s_start = sstart
            self.s_end = send
        else:
            self.s_start = send
            self.s_end = sstart
        # Point no. at feature ends
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        self.i = np.array([i_start, i_end])
        i_LE = self.main_ni // 2 + 1
        points = self.main_seg.points.copy()
        c = points[:, 0].max() - points[:, 0].min()
        xs = points[[i_start, i_end], 0]
        ys = points[[i_start, i_end], 1]
        # Determine the coordinates of the roughness boxes
        # Patch on upper surface ony
        if self.s_start >= self.main_seg.sLE:
            self.box_up = np.array([xs.min(), xs.max(), ys.min(), ys.max()])
            self.box_low = self.box_up
        elif self.s_end <= self.main_seg.sLE:
            self.box_low = np.array([xs.min(), xs.max(), ys.min(), ys.max()])
            self.box_up = self.box_low
        else:
            self.box_up = np.array(
                [
                    points[:, 0].min() - 0.01 * c,
                    points[i_end, 0],
                    points[i_LE, 1],
                    points[i_start:i_end, 1].max(),
                ]
            )

            self.box_low = np.array(
                [
                    points[:, 0].min() - 0.01 * c,
                    points[i_start, 0],
                    points[i_start:i_LE, 1].min(),
                    points[i_LE, 1],
                ]
            )
            # self.box_up = np.array([points[:, 0].min() - 0.01 * c, points[i_end, 0],
            #                         points[i_LE, 1], points[i_end, 1]])

            # self.box_low = np.array([points[:, 0].min() - 0.01 * c, points[i_start, 0],
            #                          points[i_start, 1], points[i_LE, 1]])
        # In Knopp's roughness model the roughness is given by
        d0 = 0.03 * ks
        self.rough_len = d0

        return self

    def smoothbite(self, bite_size):
        """
        Create over- (bite > 0) and underbite (bite < 0), which is then filled up
        again, modelling the effect of filling any imperfections at the LE.

        bite: float [m]
            size of over or underbite
        """
        self.bite(bite_size)
        i_LE = np.argmin(self.points[:, 0])
        i_ymax = np.argmax(self.points[:, 1])
        i_ymin = np.argmin(self.points[:, 1])
        pLE = self.points[i_LE]
        # Vertical point abvoe/below LE point
        pvLE = np.array([pLE[0], pLE[1] - 2 * bite_size])

        ang_p = np.arctan2(
            self.points[:, 1] - pvLE[1], self.points[:, 0] - pvLE[0]
        )
        if bite_size < 0:
            ang_c = np.arctan2(self.dp[:, 1], self.dp[:, 0])
            ang_diff = abs(ang_c[i_LE:i_ymax] - ang_p[i_LE:i_ymax])
            i_tangent = np.argmin(ang_diff) + i_LE
        else:
            ang_c = np.arctan2(-self.dp[:, 1], -self.dp[:, 0])
            ang_diff = abs(ang_c[i_ymin:i_LE] - ang_p[i_ymin:i_LE])
            i_tangent = np.argmin(ang_diff) + i_ymin

        self.i_LE = i_LE
        self.i_tangent = i_tangent
        self.pvLE = pvLE

        # The filler surface is assumed to follow a Bezier Curve
        c = BezierCurve()
        c.ni = 100
        c.add_control_point(np.array([pLE[0], pLE[1], 0]))
        c.add_control_point(np.array([pvLE[0], pvLE[1], 0]))
        c.add_control_point(
            np.array([self.points[i_tangent, 0], self.points[i_tangent, 1], 0])
        )
        c.update()
        self.c = c
        # Depending on the bite sign,the curve needs to be build differently.
        # The TE is excluded, as aftrwards the point distribution needs to be chnaged again
        if bite_size < 0:
            points = np.append(
                self.points[(self.ni_TE + 1) // 2 : i_LE],
                c.points[1:, :2],
                axis=0,
            )
            points = np.append(
                points,
                self.points[i_tangent + 1 : -(self.ni_TE + 1) // 2],
                axis=0,
            )
        else:
            points = np.append(
                self.points[(self.ni_TE + 1) // 2 : i_tangent],
                c.points[-2::-1, :2],
                axis=0,
            )
            points = np.append(
                points, self.points[i_LE + 1 : -(self.ni_TE + 1) // 2], axis=0
            )

        self.over_points = self.points
        self.points = points
        self.redistribute(self.ni - 1, close_te=True)
        self.initialize(self.points)

        return self

    def slot(self, s_step, s_len, h, ds_h, ni_step):
        """
        Add or remove material from the airfoil over a certain region.

        s_step: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_len: float [m]
            length of perturbation
        h: float [m]
            size of material addition (+ve) or removal (-ve)
        ds_h: float [m]
            grid size over h
        ni_step: int [-]
            additional cells to resolve perturbed region
        """
        # Translate into normalised coordinates
        sstart = self.main_seg.sLE + s_step / self.main_seg.smax
        # Always place end point towards TE
        send = (
            self.main_seg.sLE
            + (s_step + np.sign(s_step) * s_len) / self.main_seg.smax
        )
        if sstart < send:
            self.s_step_start = sstart
            self.s_step_end = send
        else:
            self.s_step_start = send
            self.s_step_end = sstart

        # Find the number of grid points per step
        self.ni_h = (
            int(max(np.round(abs(h) / ds_h), np.round(abs(h) / self.ds_LE)))
            + 1
        )
        self.ds_h = ds_h
        # Additional points not used in the step are used over the airfoil
        # (Make sure there are enough points to allow this)
        ni_step = ni_step - 2 * (self.ni_h - 1)
        # Find airfoil points closest to start and end
        i_step_start = np.argmin(abs(self.s_step_start - self.main_seg.s))
        i_step_end = np.argmin(abs(self.s_step_end - self.main_seg.s))
        main_seg = self.main_seg.copy()
        # Make sure all extra points are used on feature
        i_step_start += ni_step // 2
        i_step_end += ni_step
        i_LE = self.main_ni // 2 + 1
        if self.s_step_end < self.main_seg.sLE:
            i_LE += ni_step

        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [
                self.s_step_start,
                self.ds_h / self.main_seg.smax,
                i_step_start + 1,
            ],
            [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE],
            [self.s_step_end, self.ds_h / self.main_seg.smax, i_step_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, self.main_ni + ni_step],
        ]
        # Sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        main_seg.redistribute(dist=dist)
        self.step = main_seg.points.copy()

        # Apply disturbance normal to curve
        main_seg._compute_dp()
        normals = np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T
        step_points = (
            main_seg.points[i_step_start : i_step_end + 1, :]
            + h * normals[i_step_start : i_step_end + 1, :]
        )
        # Create the normal lines marching from original curve
        step1 = np.zeros((self.ni_h, 2))
        step2 = np.zeros((self.ni_h, 2))
        for i in range(self.ni_h):
            step1[i, :] = (
                np.sign(h) * i * self.ds_h * normals[i_step_start, :]
                + main_seg.points[i_step_start, :]
            )
        for i in range(self.ni_h):
            step2[i, :] = (
                np.sign(h) * i * self.ds_h * normals[i_step_end, :]
                + main_seg.points[i_step_end, :]
            )
        # Assemble pertubed region
        step_points = np.append(step1, step_points[1:], axis=0)
        step_points = np.append(step_points[:-1], step2[::-1], axis=0)
        step_points = np.append(
            main_seg.points[:i_step_start], step_points, axis=0
        )
        step_points = np.append(
            step_points, main_seg.points[i_step_end + 1 :], axis=0
        )
        # Assemble profile
        points = np.append(
            self.te_seg.points[self.te_isplit :], step_points[1:], axis=0
        )
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.i_step_start = i_step_start
        self.i_step_end = i_step_end
        self.points = points
        self.initialize(self.points)

        return self

    def smoothslot_start(self, s_step, s_len, h, ds_h, ni_step):
        """
        Remove/add material with step at the start of the perturbation.

        s_step: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_len: float [m]
            length of perturbation
        h: float [m]
            size of material addition (+ve) or removal (-ve)
        ds_h: float [m]
            grid size over h
        ni_step: int [-]
            additional cells to resolve perturbed region
        """
        # A dditional class hosting all the LE modifications
        # Translate into normalised coordinates
        self.s_step_start = self.main_seg.sLE + s_step / self.main_seg.smax
        # Always place end point towards TE
        self.s_step_end = (
            self.main_seg.sLE
            + (s_step + np.sign(s_step) * s_len) / self.main_seg.smax
        )
        # Find the number of grid points per step
        self.ni_h = (
            int(max(np.round(abs(h) / ds_h), np.round(abs(h) / self.ds_LE)))
            + 1
        )
        self.ds_h = ds_h
        # Additional points not used in the step are used over the airfoil
        # (Make sure there are enough points to allow this)
        ni_step = ni_step - (self.ni_h - 1)
        # Find airfoil points closest to start and end
        i_step_start = np.argmin(abs(self.s_step_start - self.main_seg.s))
        i_step_end = np.argmin(abs(self.s_step_end - self.main_seg.s))

        if self.s_step_end < self.s_step_start:
            i_step_end += ni_step // 2
            i_step_start += ni_step
        else:
            i_step_start += ni_step // 2
            i_step_end += ni_step
        # New no. of points
        main_ni = self.main_ni
        main_seg = self.main_seg.copy()
        # If the slot is before the LE than add some points to the LE
        i_LE = main_ni // 2 + 1
        if self.s_step_start < self.main_seg.sLE:
            i_LE += ni_step
        # Coarsen towards the end of the step
        ds_end = s_len / abs(h) * self.ds_h / self.main_seg.smax

        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [
                self.s_step_start,
                self.ds_h / self.main_seg.smax,
                i_step_start + 1,
            ],
            [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE],
            [self.s_step_end, ds_end, i_step_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, main_ni + ni_step],
        ]
        # Sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        main_seg.redistribute(dist=dist)
        self.step = main_seg.points.copy()

        # Apply disturbance normal to curve
        main_seg._compute_dp()
        normals = np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T
        # Create the normal lines marching from original curve
        step = np.zeros((self.ni_h, 2))
        for i in range(self.ni_h):
            step[i, :] = (
                np.sign(h) * i * self.ds_h * normals[i_step_start, :]
                + main_seg.points[i_step_start, :]
            )
        slen = s_len / self.main_seg.smax
        if self.s_step_start < self.s_step_end:
            step_reg = main_seg.points[i_step_start : i_step_end + 1, :]
            step_s = main_seg.s[i_step_start : i_step_end + 1]
            step_reg[:, 0] += (
                ((step_s - self.s_step_end) / slen) ** 2
                * h
                * normals[i_step_start : i_step_end + 1, 0]
            )
            step_reg[:, 1] += (
                ((step_s - self.s_step_end) / slen) ** 2
                * h
                * normals[i_step_start : i_step_end + 1, 1]
            )
            step_points = np.append(step, step_reg[1:, :], axis=0)
            step_points = np.append(
                main_seg.points[:i_step_start], step_points, axis=0
            )
            step_points = np.append(
                step_points, main_seg.points[i_step_end + 1 :], axis=0
            )
        else:
            step_reg = main_seg.points[i_step_end : i_step_start + 1, :]
            step_s = main_seg.s[i_step_end : i_step_start + 1]
            step_reg[:, 0] += (
                ((step_s - self.s_step_end) / slen) ** 2
                * h
                * normals[i_step_end : i_step_start + 1, 0]
            )
            step_reg[:, 1] += (
                ((step_s - self.s_step_end) / slen) ** 2
                * h
                * normals[i_step_end : i_step_start + 1, 1]
            )
            step_points = np.append(step_reg[:-1], step[::-1, :], axis=0)
            step_points = np.append(
                main_seg.points[:i_step_end], step_points, axis=0
            )
            step_points = np.append(
                step_points, main_seg.points[i_step_start + 1 :], axis=0
            )

        # Assemble profile
        points = np.append(
            self.te_seg.points[self.te_isplit :], step_points[1:], axis=0
        )
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.i_step_start = i_step_start
        self.i_step_end = i_step_end
        self.points = points
        self.initialize(self.points)

        return self

    def smoothslot_end(self, s_step, s_len, h, ds_h, ni_step):
        """
        Remove/add material with step at the end of the perturbation.

        s_step: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_len: float [m]
            length of perturbation
        h: float [m]
            size of material addition (+ve) or removal (-ve)
        ds_h: float [m]
            grid size over h
        ni_step: int [-]
            additional cells to resolve perturbed region
        """
        # Additional class hosting all the LE modifications
        # Always place end point towards TE
        self.s_step_end = self.main_seg.sLE + s_step / self.main_seg.smax
        # Translate into normalised coordinates
        self.s_step_start = (
            self.main_seg.sLE
            + (s_step - np.sign(s_step) * s_len) / self.main_seg.smax
        )
        # Find the number of grid points per step
        self.ni_h = (
            int(max(np.round(abs(h) / ds_h), np.round(abs(h) / self.ds_LE)))
            + 1
        )
        self.ds_h = ds_h
        # Additional points not used in the step are used over the airfoil
        # (Make sure there are enough points to allow this)
        ni_step = ni_step - (self.ni_h - 1)
        # Find airfoil points closest to start and end
        i_step_start = np.argmin(abs(self.s_step_start - self.main_seg.s))
        i_step_end = np.argmin(abs(self.s_step_end - self.main_seg.s))
        ds_orig = self.ds[i_step_start]
        if self.s_step_end < self.s_step_start:
            i_step_end += ni_step // 2
            i_step_start += ni_step
        else:
            i_step_start += ni_step // 2
            i_step_end += ni_step
        # New no. of points
        main_ni = self.main_ni
        main_seg = self.main_seg.copy()
        # If the slot is before the LE than add some points to the LE
        i_LE = main_ni // 2 + 1

        if self.s_step_start < self.main_seg.sLE:
            i_LE += ni_step // 2
        if self.s_step_end < self.main_seg.sLE:
            i_LE += ni_step // 2
        # Coarsen towards the end of the step
        ds_end = s_len / abs(h) * self.ds_h / self.main_seg.smax
        ds_end = min(ds_orig, ds_end)
        d = np.array(
            [
                self.s_step_start - self.main_seg.sLE,
                self.s_step_end - self.main_seg.sLE,
            ]
        )
        if (np.sign(d[0]) == np.sign(d[1])) or (d[0] == 0) or (d[1] == 0):
            dist = [
                [0.0, self.ds_TE / self.main_seg.smax, 1],
                [
                    self.s_step_start,
                    0.66 * self.ds_LE / self.main_seg.smax,
                    i_step_start + 1,
                ],
                [
                    self.s_step_end,
                    self.ds_h / self.main_seg.smax,
                    i_step_end + 1,
                ],
                [1.0, self.ds_TE / self.main_seg.smax, main_ni + ni_step],
            ]
        else:
            dist = [
                [0.0, self.ds_TE / self.main_seg.smax, 1],
                [self.s_step_start, ds_end, i_step_start + 1],
                [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE],
                [
                    self.s_step_end,
                    self.ds_h / self.main_seg.smax,
                    i_step_end + 1,
                ],
                [1.0, self.ds_TE / self.main_seg.smax, main_ni + ni_step],
            ]
        # Sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        self.dist = dist
        main_seg.redistribute(dist=dist)
        self.step = main_seg.points.copy()

        # Apply disturbance normal to curve
        main_seg._compute_dp()
        normals = np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T
        # Create the normal lines marching from original curve
        step = np.zeros((self.ni_h, 2))
        for i in range(self.ni_h):
            step[i, :] = (
                np.sign(h) * i * self.ds_h * normals[i_step_end, :]
                + main_seg.points[i_step_end, :]
            )
        slen = s_len / self.main_seg.smax
        if self.s_step_start < self.s_step_end:
            step_reg = main_seg.points[i_step_start : i_step_end + 1, :]
            step_s = main_seg.s[i_step_start : i_step_end + 1]
            step_reg[:, 0] += (
                ((step_s - self.s_step_start) / slen) ** 2
                * h
                * normals[i_step_start : i_step_end + 1, 0]
            )
            step_reg[:, 1] += (
                ((step_s - self.s_step_start) / slen) ** 2
                * h
                * normals[i_step_start : i_step_end + 1, 1]
            )
            step_points = np.append(step_reg[:-1, :], step[::-1, :], axis=0)
            step_points = np.append(
                main_seg.points[:i_step_start], step_points, axis=0
            )
            step_points = np.append(
                step_points, main_seg.points[i_step_end + 1 :], axis=0
            )
        else:
            step_reg = main_seg.points[i_step_end : i_step_start + 1, :]
            step_s = main_seg.s[i_step_end : i_step_start + 1]
            step_reg[:, 0] += (
                ((step_s - self.s_step_start) / slen) ** 2
                * h
                * normals[i_step_end : i_step_start + 1, 0]
            )
            step_reg[:, 1] += (
                ((step_s - self.s_step_start) / slen) ** 2
                * h
                * normals[i_step_end : i_step_start + 1, 1]
            )
            step_points = np.append(step[:-1, :], step_reg, axis=0)
            step_points = np.append(
                main_seg.points[:i_step_end], step_points, axis=0
            )
            step_points = np.append(
                step_points, main_seg.points[i_step_start + 1 :], axis=0
            )

        # Assemble profile
        points = np.append(
            self.te_seg.points[self.te_isplit :], step_points[1:], axis=0
        )
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.i_step_start = i_step_start
        self.i_step_end = i_step_end
        self.points = points
        self.initialize(self.points)

        return self

    def stallstrip(self, s_strip, h, ni, ds, ang):
        """
        Creates a triangular stallstrip with max height at s_strip.

        s_strip: float [m]
            curve location of strip. Defined from LE.
            +ve increasing towards suction side.
        h: float [m]
            height of stall strip
        ni: int [-] (multiple of 4)
            additional no. of cells resolving feature
        ds: float [m]
            grid size over step
        ang: float [deg]
            angle in tip corner
        """
        # The stall strip has triangular shape with equal side lenghts
        L = h / np.cos(np.deg2rad(ang / 2))
        L_base = 2 * h * np.tan(np.deg2rad(ang / 2))
        # Normalised start and end of flat region
        self.s_start = (
            self.main_seg.sLE + (s_strip - L_base / 2) / self.main_seg.smax
        )
        self.s_mid = self.main_seg.sLE + s_strip / self.main_seg.smax
        self.s_end = (
            self.main_seg.sLE + (s_strip + L_base / 2) / self.main_seg.smax
        )
        main_ni = self.main_ni
        main_seg = self.main_seg.copy()
        # Point no. at feature ends
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_mid = np.argmin(abs(self.s_mid - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        # Distribute additional points around the feature ends
        i_LE = main_ni // 2 + 1
        # Grid step on strip
        ds_tr = min(self.ds_LE, ds)
        # Number of points per side of triangle
        ni_L = 2 * (np.round(2 * L / ds_tr) // 4)
        # Ensure not too many points will be used
        if ni_L > 2 * (ni // 6):
            ni_L = 2 * (ni // 6)
            ds_tr = min(L / ni_L, self.ds_LE)
        # Determine no. of points used around stall strip
        ni_extra = (ni - 2.0 * ni_L) // 2
        ni_L = int(ni_L)
        ni_extra = int(ni_extra)
        ni_extra += ni - 2 * ni_extra - 2 * ni_L
        # Adjust the no. of points at the LE
        if self.s_start < self.main_seg.sLE:
            i_add = int(
                ni_extra
                * min(
                    (self.main_seg.sLE - self.s_start)
                    * self.main_seg.smax
                    / (4 * L),
                    1.0,
                )
            )
            i_LE += i_add + ni_L // 2
        if self.s_mid < self.main_seg.sLE:
            i_LE += ni_L
        if self.s_end < self.main_seg.sLE:
            i_add = int(
                ni_extra
                * min(
                    (self.main_seg.sLE - self.s_start)
                    * self.main_seg.smax
                    / (4 * L),
                    1.0,
                )
            )
            i_LE += ni_L // 2 + i_add
        # Add additional points to the original
        main_ni = main_ni + ni
        i_start += ni_extra
        i_mid = i_start + ni_L
        i_end = i_mid + ni_L

        if np.sqrt(
            (self.s_mid - self.main_seg.sLE) ** 2
        ) * self.main_seg.smax < (10 * L):
            dist = [
                [0.0, self.ds_TE / self.main_seg.smax, 1],
                [self.s_start, ds_tr / self.main_seg.smax, i_start + 1],
                [self.s_mid, ds_tr / self.main_seg.smax, i_mid + 1],
                [self.s_end, ds_tr / self.main_seg.smax, i_end + 1],
                [1.0, self.ds_TE / self.main_seg.smax, main_ni],
            ]
        else:
            dist = [
                [0.0, self.ds_TE / self.main_seg.smax, 1],
                [self.s_start, ds_tr / self.main_seg.smax, i_start + 1],
                [self.s_mid, ds_tr / self.main_seg.smax, i_mid + 1],
                [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE],
                [self.s_end, ds_tr / self.main_seg.smax, i_end + 1],
                [1.0, self.ds_TE / self.main_seg.smax, main_ni],
            ]
        # Sort by curve length
        dist = sorted(dist, key=lambda x: x[0])
        main_seg.redistribute(dist=dist)

        # Find the position of the tip of the trip strip
        main_seg._compute_dp()
        normal = np.array([-main_seg.dp[i_mid, 1], main_seg.dp[i_mid, 0]]).T
        tip_xy = normal * h + main_seg.points[i_mid, :]

        l1 = Line(main_seg.points[i_start, :], tip_xy, i_mid - i_start + 1)
        l2 = Line(tip_xy, main_seg.points[i_end, :], i_end - i_mid + 1)
        l1.redistribute(
            dist=[
                [0.0, ds_tr / l1.smax, 1],
                [1.0, ds_tr / l1.smax, i_mid - i_start + 1],
            ]
        )
        l2.redistribute(
            dist=[
                [0.0, ds_tr / l2.smax, 1],
                [1.0, ds_tr / l2.smax, i_end - i_mid + 1],
            ]
        )
        tr = np.append(l1.points[1:], l2.points[1:], axis=0)

        # Assemble airfoil with TE closure
        points = np.append(
            self.te_seg.points[self.te_isplit :],
            main_seg.points[1 : i_start + 1],
            axis=0,
        )
        points = np.append(points, tr, axis=0)
        points = np.append(points, main_seg.points[i_end + 1 :], axis=0)
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.tr = tr
        self.points = points
        self.initialize(self.points)

        return self

    def spectralLER(
        self,
        s_start,
        s_end,
        ni=128,
        ds_fac=2.0,
        patch=None,
        store_patch=True,
        patch_outfilename=None,
        domega=2 * np.pi / 203.7447e-3,
        fac_dxy_domega=2,
        Lx_in=203.7447e-3,
        stdev=0.2023e-3,
        lambda0=2.3023e-3,
        mu=-0.4693e-3,
        damage_limits=[-1.5e-3, 0.0],
        Nomega=281,
        Ndirs=40,
        A=0.175,
        B=0.290,
        seed=0,
        avgfit_c0=0.4021,
        avgfit_c1=1.5361,
        stdfit_c0=0.3968,
        stdfit_c1=1.4084,
        edge_smooth=0.1,
        patch_slice=0.0,
        step=False,
        s_len_step=40e-3,
        h_step=-1.5e-3,
        h_ni_min=5,
    ):
        """
        Creates eroded leading edge. Erosion is modelled as superposition of
        waves over the leading edge. Waves are generated from a spectrum that
        is also used in wave theory. This method was developed by Mac Gaunaa
        and Anders Olsen from DTU Wind. Also a pregenerated erosion patch
        can be loaded by giving the erosion patch name to be loaded as
        patch=<name of erosion patch file>.

        s_start: float [m]
            curve location where perturbation starts. Defined from LE.
            +ve increasing towards suction side.
        s_end: float [m]
            curve location where perturbation ends. Defined from LE.
            +ve increasing towards suction side.
        ni: int [-] (multiple of 4)
            additional no. of cells resolving erosion feature
        ds_fac: int [-]
            a factor multiplying the grid size at the grid control points at
            the start and end of the erosion area, increasing the clustering
            towards the centre of the erosion area if ds_fac > 1.
        patch: None or patch directory [-]
            if None a new erosion patch is simulated otherwise input a
            directory holding all needed patch data.
        store_patch: bool
            indicate whether the erosion patch should be stored in the object
        patch_outfilename: string or None [-]
            if not None the erosion patch is saved as a pickle file.
            Load file by:
            import pickle
            a_file = open(patch_name + '.pkl', "rb")
            patch = pickle.load(a_file)
        domega : float [rad/m]
            resolution of the angular wave frequencies
        fac_dxy_domega : int
            the ration between the spatial resolution of the patch and the
            resolution of the wave angular frequencies. Should be at least
            2, otherwise the resolution is not sufficient to capture the
            highest frequency. So one could think of it as the sampling
            frequency, which by Nyquist sould be at least 2*fmax.
            dxy = 2pi/(fac_dxy_domega*domega*Nomega)
        Lx_in : float [m]
            erosion patch length along main wave propagation direction. For
            a wind turbine blade this corresponds to the spanwise direction.
            Note that Lx_in is modified such that it is always divisible by
            dxy.
        stdev : float [m]
            LER specific standard deviation of surface perturbations
        lambda0 : float [m]
            LER specific 0-upcrossing wave length
        mu : float [m]
            mean value of perturbations
        damage_limits : list(float) or None
            lower and upper limit to surface perturbations. All values exceeding
            these limits are set to respective limit value.
        Nomega : int
            no. of angular frequency bins to simulate
        Ndirs : int
            only used if wavedir=='2D'. No. of wave directions to simulate.
            Discretizes directional space from -pi/2 to pi/2.
            If not uneven it will be made uneven such that the main wave
            direction is resolved ie theta=0.
        A : float
            universal spectral shape coefficient for high wave frequencies
        B : float
            universal spectral shape coefficient for low wave frequencies
        seed : int
            turbulent seed used in random number generation
        avgfit_c0
            super-gauss constant for mean erosion level scaling
        avgfit_c1
            super-gauss constant for mean erosion level scaling
        stdfit_c0
            super-gauss constant for erosion level standard deviation scaling
        stdfit_c1
            super-gauss constant for erosion level standard deviation scaling
        edge_smooth
            fraction of Ly over which edge smoothing is applied, only active
            with scaling enabled. Towards each edge in y a hyperbolic tangent
            scaling function ensures that the erosion is going smoothly
            towards 0. It is active for abs(y) > (Ly/2 - edge_smooth*Ly).
        patch_slice: float (0.0 <-> 1.0) [-]
            fraction of Lx_in (spanwise erosion length) at which to extract the
            erosion profile
        step: bool
            activate the addition of a step on the suction side, which is meant
            to mimick chipping of the gel coat
        s_len: float [m]
            length over which to apply the chipping
        h_step: float [m]
            depth of chipping, note that the damage limits are still applied,
            for h_step < 0 part of the surface is removed
        h_ni_min: int [-]
            minimum no. of points discretizing the step
        """
        # ===== Generate surface point distribution =====
        # This part is a copy of the wavy perturbation
        self.s_start = self.main_seg.sLE + s_start / self.main_seg.smax
        self.s_end = self.main_seg.sLE + s_end / self.main_seg.smax
        slen = self.s_end - self.s_start
        smid = self.s_start + slen / 2.0
        # Change point distribution
        main_ni = self.main_ni
        main_seg = self.main_seg.copy()
        i_start = np.argmin(abs(self.s_start - self.main_seg.s))
        i_end = np.argmin(abs(self.s_end - self.main_seg.s))
        i_LE = main_ni // 2 + 1
        # Introducing a step requires some more points that discretize
        # the step, which is removed from the additional points that
        # can be used over the airfoil. Other parameters needed to
        # calculate the step are also added.
        ds = slen / ni
        if step:
            self.s_step_end = self.s_end
            # Translate into normalised coordinates
            self.s_step_start = (
                self.s_step_end - s_len_step / self.main_seg.smax
            )
            # Find the number of grid points per step
            self.ni_h_step = (
                int(max(h_ni_min - 1, np.round(abs(h_step) / ds))) + 1
            )
            ds_h_step = h_step / (self.ni_h_step - 1)
            self.ds_h_step = ds_h_step
            self.h_step = h_step
            ni = ni - (self.ni_h_step - 1)
        # Extra points are mostly concentrated in the oscillating area,
        # but two eigth are placed outside the region as well
        ni_o = ni // 8
        # Depending where the region is, some points need to be added
        # at the LE sto leave the intial point distribution unaffected.
        if self.s_start < self.main_seg.sLE:
            i_LE += 4 * ni_o
        if self.s_end < self.main_seg.sLE:
            i_LE += 4 * ni_o
        if step and (self.s_step_end > self.main_seg.sLE):
            i_LE += self.ni_h_step
        # update point numbers
        main_ni = main_ni + ni
        i_start += ni_o
        i_end += 7 * ni_o
        ds = slen / ni
        # Increase resolution in perturbed area, the control point at the
        # LE was removed as it was constraining the mesh generation too strongly,
        # instead ds_fac is used to decrease the resolution at the boudaries of the
        # eroded region
        dist = [
            [0.0, self.ds_TE / self.main_seg.smax, 1],
            [self.s_start, ds_fac * ds / self.main_seg.smax, i_start + 1],
            # [self.main_seg.sLE, self.ds_LE / self.main_seg.smax, i_LE + 1],
            [self.s_end, ds_fac * ds / self.main_seg.smax, i_end + 1],
            [1.0, self.ds_TE / self.main_seg.smax, main_ni],
        ]
        if step:
            # change the grid spacing at the s_end to be the same as across
            # the step itself
            i_step_end = i_end.copy()
            dist[2][1] = self.ds_h_step / self.main_seg.smax
        # Sort dist by the curve length
        dist = sorted(dist, key=lambda x: x[0])
        self.dist = dist
        self.ds = ds * self.main_seg.smax
        # Need to compute
        main_seg._compute_dp_flag = True
        main_seg.redistribute(dist=dist)
        s = main_seg.s.copy()

        # length of erosion patch in chordwise
        Ly_in = slen * self.main_seg.smax
        # ===== Generate spectral erosion pattern =====
        if patch is None:
            patch = ocean_erosion(
                domega=domega,
                fac_dxy_domega=fac_dxy_domega,
                Lx_in=Lx_in,
                Ly_in=Ly_in,
                Nomega=Nomega,
                Ndirs=Ndirs,
                stdev=stdev,
                lambda0=lambda0,
                mu=mu,
                damage_limits=damage_limits,
                A=A,
                B=B,
                seed=seed,
                wavedir="2D",
                scale=True,
                avgfit_c0=avgfit_c0,
                avgfit_c1=avgfit_c1,
                stdfit_c0=stdfit_c0,
                stdfit_c1=stdfit_c1,
                edge_smooth=edge_smooth,
            )

        # extract a single chordwise slice from the erosion patch
        islice = int(patch_slice * (len(patch["x"]) - 1))
        dn_raw = patch["dn"][:, islice]
        sp = (s[i_start : i_end + 1] - smid) * self.main_seg.smax
        spdiff = abs(np.diff(sp))
        self.dsminmax_dxy = (
            np.array([spdiff.min(), spdiff.max()]) / patch["dxy"]
        )

        dn = np.interp(sp, patch["y"], dn_raw)
        self.sp_dn = np.c_[sp, dn]
        self.y_dn = np.c_[patch["y"], dn_raw]

        # ===== Compute normal vector =====
        # nomal vector pointing outwards
        normals = np.array([-main_seg.dp[:, 1], main_seg.dp[:, 0]]).T

        # ===== Add erosion =====
        # nomal vector pointing outwards
        erosion = main_seg.points.copy()
        for i in range(len(dn)):
            ii = i_start + i
            erosion[ii, :] += normals[ii, :] * dn[i]
        self.dn = dn
        if store_patch:
            self.patch = patch
        if patch_outfilename is not None:
            a_file = open(patch_outfilename + ".pkl", "wb")
            pickle.dump(patch, a_file)
            a_file.close()
        self.erosion = erosion.copy()

        # ===== Create step
        if step:
            # airfoil portion with LE perturbation
            ss = s[i_start : i_end + 1]
            # find the location where the step should be placed, it should be identical
            # to what was specified in dist, but there could be a slight numerical offset
            i_step_end = np.argmin(abs(self.s_step_end - main_seg.s))
            # get the curve location of step
            self.s_step_end = main_seg.s[i_step_end]
            # cubic growth of chipping
            srel = (
                (ss - self.s_step_start)
                / (self.s_step_end - self.s_step_start)
            ) ** 2
            # find the portion of the blade over which the chipping should take place
            Is = np.where((ss >= self.s_step_start) & (ss <= self.s_step_end))[
                0
            ]
            # init step perturbation
            dn_h = np.zeros_like(ss)
            # step perturbation
            dn_h[Is] = srel[Is] * h_step
            # create a combination of the eroded surface and the chipping
            dn_comb = dn.copy()
            # the first idea was to replace the eroded surface with the chipped surface
            # wherever the chipping was more severe, however this lead to a very smooth
            # lead-up to the step, so instead the step is superimposed
            dn_comb += dn_h
            dn_comb[dn_comb < damage_limits[0]] = damage_limits[0]
            # init with original unperturbed surface
            erosion_step = main_seg.points.copy()
            # apply surface perturbation
            for i in range(len(dn_comb)):
                ii = i_start + i
                erosion_step[ii, :] += normals[ii, :] * dn_comb[i]
            # Create normal step without any erosion downstream, so that the speficied
            # step is also realized
            wall = Line(
                erosion_step[i_step_end, :],
                main_seg.points[i_step_end, :],
                self.ni_h_step,
            )
            erosion = np.append(
                erosion_step[:i_step_end, :], wall.points, axis=0
            )
            erosion = np.append(
                erosion, main_seg.points[i_step_end + 1 :], axis=0
            )
            # erosion + chipping towards the suction side
            self.erosion_step = erosion

        # final eroded surface
        points = np.append(
            self.te_seg.points[self.te_isplit :], erosion[1:], axis=0
        )
        points = np.append(
            points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )
        # base surface
        base_points = np.append(
            self.te_seg.points[self.te_isplit :], main_seg.points[1:], axis=0
        )
        base_points = np.append(
            base_points, self.te_seg.points[1 : self.te_isplit + 1], axis=0
        )

        self.points = points
        self.base_points = base_points
        self.initialize(self.points)

        return


class BlendAirfoilShapes(object):
    """
    Blend input airfoil shape family based on a user defined scalar.

    The blended airfoil shape is interpolated using a cubic interpolator
    of the airfoil shapes.
    Three interpolators are implemented:\n
    ``scipy.interpolate.pchip``: has some unappealing characteristics at the bounds\n
    ``fusedwind.lib.cubicspline``: can overshoot significantly with large spacing in
    thickness\n
    ``scipy.interpolate.Akima1DInterpolator``: good compromise, overshoots less
    than a natural cubic spline\n

    The default spline is scipy.interpolate.Akima1DInterpolator.

    Parameters
    ----------
    ni: int
        number of redistributed points on airfoils

    airfoil_list: list
        List of normalized airfoils with size ((ni, 2)).

    blend_var: list
        weight factors for each airfoil in the list, only relevant if tc is not specified.

    spline: str
        spline type, either ('pchip', 'cubic', 'akima')

    allow_extrapolation: bool
        the splines allow for limited extrapolation, set to True if you feel lucky
    """

    def __init__(self, **kwargs):
        self.airfoil_list = []
        self.ni = 600
        self.blend_var = None
        self.spline = "pchip"
        self.allow_extrapolation = False

        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def initialize(self):
        if self.spline == "linear":
            self._spline = interp1d
        elif self.spline == "pchip":
            self._spline = pchip
        elif self.spline == "cubic":
            self._spline = CubicSpline
        elif self.spline == "ncubic":
            self._spline = NaturalCubicSpline
        elif self.spline == "akima":
            self._spline = Akima1DInterpolator

        self.blend_var = np.asarray(self.blend_var)

        afs = []
        for af in self.airfoil_list:
            a = AirfoilShape(af)
            aa = a.redistribute(ni=self.ni, even=True)
            afs.append(aa.points)
        self.airfoil_list = afs

        self.nj = len(self.airfoil_list)
        self.nk = 3

        self.x = np.zeros([self.ni, self.nj, self.nk])
        if self.airfoil_list[0].shape[1] == 2:
            for j, points in enumerate(self.airfoil_list):
                self.x[:, j, :2] = points[:, :2]
                self.x[:, j, 2] = self.blend_var[j]
        else:
            for j, points in enumerate(self.airfoil_list):
                self.x[:, j, :] = points[:, :]

        self.f = [[], [], []]
        for k in range(3):
            for i in range(self.ni):
                self.f[k].append(self._spline(self.blend_var, self.x[i, :, k]))

    def __call__(self, tc):
        """
        interpolate airfoil family at a given thickness

        Parameters
        ----------
        tc : float
            The relative thickness of the wanted airfoil.

        Returns
        -------
        airfoil: array
            interpolated airfoil shape of size ((ni, 2))
        """

        # check for out of bounds
        if not self.allow_extrapolation:
            if tc < np.min(self.blend_var):
                tc = self.blend_var.min()
            if tc > np.max(self.blend_var):
                tc = self.blend_var.max()

        points = np.zeros((self.ni, 3))
        for k in range(3):
            for i in range(self.ni):
                points[i, k] = self.f[k][i](tc)

        return points


class BezierAirfoilShape(object):
    """
    Class for fitting a composite Bezier curve
    to an airfoil shape.
    """

    def __init__(self):
        self.spline_CPs = np.array([])
        self.CPu = np.array([])
        self.CPl = np.array([])
        self.CPle = 0.0
        self.CPte = 0.0

        self.afIn = AirfoilShape()

        self.afOut = AirfoilShape()

        self.ni = 0
        self.fix_x = True
        self.symmLE = True
        self.symmTE = True
        self.fd_form = "fd"

    def update(self):
        self.spline_eval()
        if self.ni > 0:
            self.afOut.redistribute(ni=self.ni)

    def fit(self):
        iLE = np.argmin(self.afIn.points[:, 0])

        # lower side
        curve_in = Curve(points=self.afIn.points[: iLE + 1, :][::-1])
        CPs = np.array(self.spline_CPs)
        for n in range(1, curve_in.points.shape[1]):
            CPs = np.append(CPs, np.zeros(self.spline_CPs.shape[0]))

        CPs = CPs.reshape(
            curve_in.points.shape[1], CPs.shape[0] // curve_in.points.shape[1]
        ).T
        CPs[1:-1, 1] = -0.1

        constraints = np.ones(
            (self.spline_CPs.shape[0], self.afIn.points.shape[1])
        )
        constraints[1, 0] = 0

        fit = FitBezier(curve_in, CPs, constraints)
        fit.fix_x = self.fix_x
        fit.execute()
        self.fit0 = copy.deepcopy(fit)

        self.spline_ps = copy.deepcopy(fit.curve_out)

        # upper side
        curve_in = Curve(points=self.afIn.points[iLE:, :])
        CPs = np.array(self.spline_CPs)
        for n in range(1, curve_in.points.shape[1]):
            CPs = np.append(CPs, np.zeros(self.spline_CPs.shape[0]))

        CPs = CPs.reshape(
            curve_in.points.shape[1], CPs.shape[0] // curve_in.points.shape[1]
        ).T
        CPs[1:-1, 1] = 0.1
        constraints = np.ones(
            (self.spline_CPs.shape[0], self.afIn.points.shape[1])
        )
        constraints[1, 0] = 0.0
        fit = FitBezier(curve_in, CPs, constraints)
        fit.fix_x = self.fix_x
        fit.execute()
        self.fit1 = copy.deepcopy(fit)
        self.spline_ss = copy.deepcopy(fit.curve_out)

        self.CPl = self.spline_ps.CPs.copy()
        self.CPu = self.spline_ss.CPs.copy()
        self.nCPs = self.CPl.shape[0] + self.CPu.shape[0]
        self.CPle = 0.5 * (self.CPu[1, 1] - self.CPl[1, 1])
        self.CPte = 0.5 * (self.CPu[-1, 1] - self.CPl[-1, 1])
        if self.fd_form == "complex_step":
            self.CPl = np.array(self.CPl, dtype=np.complex128)
            self.CPu = np.array(self.CPu, dtype=np.complex128)
            self.CPle = np.complex128(self.CPle)
            self.CPte = np.complex128(self.CPte)
        self.spline_eval()

    def spline_eval(self):
        """
        compute the Bezier spline shape given control points in CPs.
        CPs has the shape ((2 * spline_CPs.shape[0], 2)).
        """

        nd = self.CPl.shape[1]
        self.spline_ps.CPs = self.CPl
        if self.symmLE:
            self.spline_ps.CPs[1, 1] = -self.CPle
        if self.symmTE:
            self.spline_ps.CPs[-1, 1] = -self.CPte
        self.spline_ps.CPs[0] = np.zeros(nd)
        self.spline_ps.update()
        self.spline_ss.CPs = self.CPu
        if self.symmLE:
            self.spline_ss.CPs[1, 1] = self.CPle
        if self.symmTE:
            self.spline_ss.CPs[-1, 1] = self.CPte
        self.spline_ss.CPs[0] = np.zeros(nd)
        self.spline_ss.update()
        points = self.spline_ps.points[::-1]
        points = np.append(points, self.spline_ss.points[1:])
        points = points.reshape(points.shape[0] // nd, nd)
        self.afOut.initialize(points)


def compute_airfoil_props(points, ndiv, x_sec):
    """
    method for computing geometric properties of
    an airfoil.

    parameters
    ----------
    points: array
        airfoil coordinates defined from TE pressure side
        to LE to TE suction side.
    ndiv: int
        number of chordwise points on resplined airfoil
    x_sec: array
        chordwise locations at which to compute
        thicknesses which can more easily be used
        for constraints.

    returns
    -------
    props: dict
        dictionary of properties containing

        | x: (array) chordwise coordinates from LE to TE

        | ys: (array) y-coordinates of suction side

        | yp: (array) y-coordinates of pressure side

        | t: (array) thickness distribution

        | mean: (array) mean line of airfoil

        | mean_angle: (array) angle of mean line

        | curv_s: (array) curvature of suction side

        | curv_p: (array) curvature of pressure side

        | tmax: (float) maximimum thickness

        | tmin: (float) minimum thickness

        | tmax_s: (float) maximum thickness of suction side

        | tmax_p: (float) maximum thickness of pressure side

        | x_tmax: (float) chordwise position of maximimum thickness

        | x_tmax_s: (float) chordwise position of suction side maximimum thickness

        | x_tmax_p: (float) chordwise position of pressure side maximimum thickness

        | t_skew: (float) chordwise offset between position of suction and pressure side maximum thickness

        | mean_max: (float) minimum value of mean line

        | mean_min: (float) maximum value of mean line
    """

    props = {}

    iLE = np.argmin(points[:, 0])
    TE = np.max(points[:, 0])
    LE = np.min(points[:, 0])

    # equally spaced point distribution along chord
    props["x"] = np.linspace(LE, TE, ndiv, dtype=points.dtype)

    # interpolate pressure side coordinates
    yps = NaturalCubicSpline(
        points[: iLE + 1, 0][::-1], points[: iLE + 1, 1][::-1]
    )
    props["yp"] = np.asarray(yps(props["x"]))
    # interpolate suction side coordinates
    yss = NaturalCubicSpline(points[iLE:, 0], points[iLE:, 1])
    props["ys"] = np.asarray(yss(props["x"]))

    # airfoil thickness distribution
    props["t"] = props["ys"] - props["yp"]
    props["tmin"] = props["t"].min()

    tspline = NaturalCubicSpline(props["x"], props["t"])

    # chordwise position of tmax
    s = calculate_length(np.array([props["x"], props["t"]]).T)
    tspline_s = NaturalCubicSpline(s, props["t"])

    def tspline_real(x):
        return -tspline_s(x).real

    res = minimize(
        tspline_real, (0.3), method="SLSQP", tol=1.0e-16, bounds=[(0, 1)]
    )
    xspline_ts = NaturalCubicSpline(s, props["x"])
    props["x_tmax"] = xspline_ts(res["x"][0])
    props["tmax"] = tspline(props["x_tmax"])
    props["t_sec"] = tspline(x_sec)

    # chordwise position of tmax @ pressure side
    # x = yps()
    s = calculate_length(np.array([props["x"], props["yp"]]).T)
    tspline_ps = NaturalCubicSpline(s, props["yp"])

    def tspline_ps_real(x):
        return tspline_ps(x).real

    res = minimize(
        tspline_ps_real, (0.3), method="SLSQP", tol=1.0e-16, bounds=[(0, 1)]
    )
    xspline_ps = NaturalCubicSpline(s, props["x"])
    props["x_tmax_p"] = xspline_ps(res["x"][0])
    props["tmax_p"] = -yps(props["x_tmax_p"])

    # chordwise position of tmax @ suction side
    s = calculate_length(np.array([props["x"], props["ys"]]).T)
    tspline_ss = NaturalCubicSpline(s, props["ys"])

    def tspline_ss_real(x):
        return -tspline_ss(x).real

    res = minimize(
        tspline_ss_real, (0.3), method="SLSQP", tol=1.0e-16, bounds=[(0, 1)]
    )
    xspline_ss = NaturalCubicSpline(s, props["x"])
    props["x_tmax_s"] = xspline_ss(res["x"][0])
    props["tmax_s"] = yss(props["x_tmax_s"])

    # airfoil skewness
    props["t_skew"] = props["x_tmax_s"] - props["x_tmax_p"]

    # airfoil mean line
    props["mean"] = 0.5 * (props["yp"] + props["ys"])
    props["mean_max"] = props["mean"].max()
    props["mean_min"] = props["mean"].min()
    # airfoil mean line angle
    grad = np.gradient(np.array([props["x"], props["mean"]]).T)[0]
    dydx = grad[:, 1] / grad[:, 0]
    props["mean_angle"] = np.zeros(ndiv, dtype=props["x"].dtype)
    if props["x"].dtype == np.complex128:
        for i in range(dydx.shape[0]):
            props["mean_angle"][i] = (
                (np.math.atan(dydx[i].real) + dydx[i].imag * 1j)
                / (1.0 + dydx[i].real ** 2)
                * 180.0
                / np.pi
            )
    else:
        for i in range(dydx.shape[0]):
            props["mean_angle"][i] = np.math.atan(dydx[i]) * 180.0 / np.pi

    # suction and pressure side curvature
    curv = curvature(points)
    curv_p = NaturalCubicSpline(
        points[: iLE + 1, 0][::-1], curv[: iLE + 1][::-1]
    )
    curv_s = NaturalCubicSpline(points[iLE:, 0], curv[iLE:])

    props["curv_p"] = curv_p(props["x"])
    props["curv_s"] = curv_s(props["x"])

    return props
