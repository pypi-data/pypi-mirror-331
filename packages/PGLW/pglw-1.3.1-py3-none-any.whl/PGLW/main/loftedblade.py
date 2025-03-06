import time

import numpy as np
from scipy.interpolate import pchip

from PGLW.main.airfoil import AirfoilShape, BlendAirfoilShapes
from PGLW.main.curve import Curve
from PGLW.main.domain import Block, Domain
from PGLW.main.geom_tools import RotMat, transformation_matrix


class LoftedBladeSurface(object):
    """
    Generates a lofted blade surface based on an airfoil family and
    a planform definition.

    If the axis defined in the planform is out of plane,
    this is taken into account in the positioning and rotation of
    the cross sections.

    The spanwise distribution is dictated by the planform points
    distribution.

    Parameters
    ----------
    pf: dict
        dictionary containing planform:
        s: normalized running length of blade
        x: x-coordinates of blade axis
        y: y-coordinates of blade axis
        z: z-coordinates of blade axis
        rot_x: x-rotation of blade axis
        rot_y: y-rotation of blade axis
        rot_z: z-rotation of blade axis
        chord: chord distribution
        rthick: relative thickness distribution
        p_le: pitch axis aft leading edge distribution
        dy: vertical offset of cross-section
    base_airfoils: list of arrays
        airfoil family
    user_surface: array
        optional lofted surface which will override the use of the planform
        definition and only use carry out a spanwise redistribution
    user_surface_file: str
        path to previously processed surface saved as a flattened array.
    user_surface_shape: tuple
        shape of user surface i.e. (257,  150, 3)
    interp_type: str
        airfoil interpolation blending variable: rthick or span
    blend_var: array
        airfoil interpolation blending factors, which will typically
        be the relative thicknesses of the airfoils in base_airfoils.
    ni_chord: int
        number of points in the chordwise direction
    redistribute_flag: bool
        flag for switching on chordwise redistribution of points along the span,
        defaults to True if close_te = True.
    dist_LE: array
        2D array containing LE cell size as function of normalized span.
        If empty, LE cell size will be set according to LE curvature.
    dist_chord: dict
        optional dictionary of additional control points defining the discretization
        in the chordwise direction, for several span locations:
        dict[n0]=func0, dict[n1]=func1 ..., dict[n<n>]=func<n>,
        where:\n
        n<n> is the cell count in the chordwise direction (so that each entry
        represents a spanwise grid line),\n
        func<n> is a list containing the corresponding list of control points:
        [[l0, s0, ds0], [l1, s1, ds1], ... [l<m>, s<m>, ds<m>]]
        where\n
        l<m> is a normalized span location,\n
        s<m> is the corresponding normalized curve fraction in the chordwise direction,
        ds<m> is the corresponding normalized cell size in the chordwise direction,
        note: if a single -l- is given for a certain control point, a uniform
        distribution in the spanwise direction will be assumed.\n
        note: this variable is ignored if redistribute_flag is set to False.
    minTE: float
        minimum trailing edge thickness.
    surface_spline: str
        spline type used to interpolate airfoil family
    chord_nte: int
        number of points on trailing edge
    gf_heights: array
        array containing s, gf_height, gf_length factor
    flaps: array
        array containing s, flap_length_factor, blend_length_factor,
        hinge_height_fact, flap_alpha_deg
    flag_twist_corr: str
        Options: (PGL, HAWC2), Use original twist correction implemented in PGL
        or the one implemented in HAWC2
    """

    def __init__(self, **kwargs):
        # planform
        self.pf = {
            "s": np.array([]),
            "x": np.array([]),
            "y": np.array([]),
            "z": np.array([]),
            "rot_x": np.array([]),
            "rot_y": np.array([]),
            "rot_z": np.array([]),
            "chord": np.array([]),
            "rthick": np.array([]),
            "p_le": np.array([]),
            "dy": np.array([]),
        }

        self.base_airfoils = []
        self.airfoil_spline = "cubic"
        self.blend_var = np.array([])
        self.user_surface = np.array([])
        self.user_surface_file = ""
        self.user_surface_shape = ()
        self.ni_chord = 257
        self.chord_nte = 11
        self.dTE = "dTE"
        self.redistribute_flag = False
        self.dist_chord = {}
        self.x_chordwise = np.array([])
        self.minTE = 0.0
        self.interp_type = "rthick"
        self.surface_spline = "pchip"
        self.dist_LE = np.array([])
        self.gf_heights = np.array([])
        self.flaps = np.array([])
        self.shear_sweep = False
        self.rotorder_sweep = True
        self.analytic_grad = True
        self.X_bar_unit = np.array([])
        self.Y_bar_unit = np.array([])
        self.Z_bar_unit = np.array([])
        self.profile = np.array([])
        self.c2d = np.array([])
        self.c2d_flag = False
        self.s_start_c2d = 0.0

        self.rot_order = np.array([2, 1, 0])  # twist, sweep, prebend
        self.flag_twist_corr = "PGL"

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

        self.domain = Domain()
        self.surface = np.array([])

    def update(self):
        """
        generate the surface
        """

        t0 = time.time()

        if self.user_surface_file:
            print("reading user surface from file", self.user_surface_file)
            x = np.loadtxt(self.user_surface_file).reshape(
                self.user_surface_shape
            )
            self.surface = x
            self.domain = Domain()
            self.domain.add_blocks(Block(x[:, :, 0], x[:, :, 1], x[:, :, 2]))

        elif self.user_surface.shape[0] > 0:
            self.redistribute_surface()

        else:
            self.initialize_interpolator()
            self.build_blade()

        print("lofted surface done ...", time.time() - t0)

    def initialize_interpolator(self):
        self.interpolator = BlendAirfoilShapes()
        self.interpolator.ni = self.ni_chord
        self.interpolator.spline = self.surface_spline
        self.interpolator.blend_var = self.blend_var
        self.interpolator.airfoil_list = self.base_airfoils
        self.interpolator.initialize()

    def build_blade(self):
        self.s = self.pf["s"]
        self.x = self.pf["x"]
        self.y = self.pf["y"]
        self.z = self.pf["z"]
        self.rot_x = self.pf["rot_x"]
        self.rot_y = self.pf["rot_y"]
        self.rot_z = self.pf["rot_z"]
        self.chord = self.pf["chord"]
        self.rthick = self.pf["rthick"]
        self.p_le = self.pf["p_le"]
        self.dy = self.pf["dy"]

        self.ni_span = self.s.shape[0]
        x = np.zeros((self.ni_chord, self.ni_span, 3))
        profile = np.zeros((self.ni_chord, self.ni_span, 3), dtype=float)
        self.c2d = c2d = np.zeros(
            (self.ni_chord, self.ni_span, 3), dtype=float
        )

        if self.gf_heights.shape[0] > 0:
            self.gf_height = pchip(
                self.gf_heights[:, 0], self.gf_heights[:, 1]
            )
            self.gf_length_factor = pchip(
                self.gf_heights[:, 0], self.gf_heights[:, 2]
            )
        if self.flaps.shape[0] > 0:
            self.flap_length_factor = pchip(self.flaps[:, 0], self.flaps[:, 1])
            self.blend_length_factor = pchip(
                self.flaps[:, 0], self.flaps[:, 2]
            )
            self.hinge_height_fact = pchip(self.flaps[:, 0], self.flaps[:, 3])
            self.flap_alpha_deg = pchip(self.flaps[:, 0], self.flaps[:, 4])

        self.LE = np.zeros((self.ni_span, 3))
        self.TE = np.zeros((self.ni_span, 3))

        # we prepare the interpolation of the chordwise distribution
        interpfunc = self._interpolate_chordwise_dist(self.z)

        for i in range(self.ni_span):
            s = self.s[i]
            pos_z = self.z[i]
            chord = self.chord[i]
            p_le = self.p_le[i]
            dy = self.dy[i]

            # generate the blended airfoil shape
            if self.interp_type == "rthick":
                rthick = self.rthick[i]
                points = self.interpolator(rthick)
            else:
                points = self.interpolator(s)

            af = AirfoilShape(points=points, spline="cubic")
            af = self._open_trailing_edge(af, i)

            af, eta = self._redistribute(af, pos_z, i, interpfunc[pos_z])
            points = af.points
            points *= chord

            points[:, 0] -= chord * p_le
            points[:, 1] += dy

            # profile sections in the local non-rotated co-ordinate systems
            profile[:, i, :] = np.c_[
                -points[:, 0], points[:, 1], np.zeros(self.ni_chord)
            ]

            # x-coordinate needs to be inverted for clockwise rotating blades
            x[:, i, :] = np.c_[
                -points[:, 0], points[:, 1], np.ones_like(points[:, 0]) * pos_z
            ]
            c2d[:, i, 0] = (s - self.s_start_c2d) / (1.0 - self.s_start_c2d)
            c2d[:, i, 1] = eta

        # save blade without sweep and prebend
        x_norm = x.copy()
        # save the profile
        self.profile = profile
        # apply prebend, sweep and twist
        x = self._rotate(profile)
        self.c2d = c2d

        for i in range(self.s.shape[0]):
            if self.s[i] <= self.s_start_c2d:
                c2d[:, i, 2] = -1.0
        self.surfnorot = x_norm
        self.surface = x
        self.domain = Domain()
        block = Block(x[:, :, 0], x[:, :, 1], x[:, :, 2])
        if self.c2d_flag:
            block.add_scalar("c2d0", np.atleast_3d(self.c2d[:, :, 0]))
            block.add_scalar("c2d1", np.atleast_3d(self.c2d[:, :, 1]))
            block.add_scalar("c2d2", np.atleast_3d(self.c2d[:, :, 2]))
        # import ipdb; ipdb.set_trace()
        self.domain.add_blocks(block)

    def redistribute_surface(self):
        self.s = self.pf["s"]

        self.interpolator = BlendAirfoilShapes()
        self.interpolator.ni = self.ni_chord
        self.interpolator.spline = self.surface_spline
        if self.blend_var.shape[0] == 0:
            self.interpolator.blend_var = (
                self.user_surface[0, :, 2] - self.user_surface[0, 0, 2]
            ) / self.user_surface[0, -1, 2]
        else:
            self.interpolator.blend_var = self.blend_var
        self.interpolator.airfoil_list = [
            self.user_surface[:, i, :]
            for i in range(self.user_surface.shape[1])
        ]
        self.interpolator.initialize()

        self.ni_span = self.s.shape[0]
        self.c2d = c2d = np.zeros(
            (self.ni_chord, self.ni_span, 3), dtype=float
        )
        x = np.zeros((self.ni_chord, self.ni_span, 3))
        self.LE = np.zeros((self.ni_span, 3))
        self.TE = np.zeros((self.ni_span, 3))

        # we prepare the interpolation of the chordwise distribution
        interpfunc = self._interpolate_chordwise_dist(self.s)

        for i in range(self.ni_span):
            pos_z = self.s[i]
            points = self.interpolator(pos_z)

            af = AirfoilShape(points=points, spline="cubic")
            af = self._open_trailing_edge(af, i)
            af, eta = self._redistribute(af, pos_z, i, dist=interpfunc[pos_z])

            points = af.points

            # points = self._open_trailing_edge(points, i)

            # points, s = self._redistribute(points, pos_z, i, interpfunc[pos_z])

            # x-coordinate needs to be inverted for clockwise rotating blades
            x[:, i, :] = points
            c2d[:, i, 0] = (pos_z - self.s_start_c2d) / (
                1.0 - self.s_start_c2d
            )
            c2d[:, i, 1] = eta

        self.surface = x
        self.c2d = c2d
        self.domain = Domain()
        self.domain.add_blocks(Block(x[:, :, 0], x[:, :, 1], x[:, :, 2]))

    def rotate_surface_z(self, angle):
        self.domain.rotate_z(angle)
        self.surface = self.domain.blocks["block"]._block2arr()[:, :, 0, :]
        self.main_axis.rotate_z(angle)

    def rotate_surface_x(self, angle):
        self.domain.rotate_x(angle)
        self.surface = self.domain.blocks["block"]._block2arr()[:, :, 0, :]
        self.main_axis.rotate_x(angle)

    def _rotate(self, x):
        """Produces the lofted rotated blade using tait-bryan angles"""

        # calculate the rotation matrix
        # rot_x: prebend, rot_y: sweep, rot_z: twist
        # Intrinsic Tait-bryan where Yaw(prebend)-pitch(sweep)-roll(twist)
        # The rotation matrix will be: R = Rx.Ry.Rz

        # final X
        X = np.zeros((self.ni_chord, self.ni_span, 3), dtype=float)
        # create the curve and get the main axis points in body CS
        axis = Curve(
            points=np.array([self.x, self.y, self.z]).T, spline="pchip"
        )

        # get gradient
        if self.analytic_grad:
            self.grad = self._analytic_gradient(axis)
        else:
            self.grad = axis.dp

        # create the rotation matrix based on order
        # rot_order is in the order of actual transformation
        # ex: Prebend-Sweep-Twist will have the rotation order:[2, 1, 0]
        rot_order = self.rot_order
        # specify rotation order with either prebend first or sweep first
        if self.rotorder_sweep:
            # get V_theta_direction
            Vtheta_unit = self._rotation_direction()
            # make rot_order=[2, 0, 1]: twist, prebend, sweep
            rot_order[2] = 1
            rot_order[1] = 0
            # obtain angles:
            # prebend
            rot_x = np.arcsin(-self.grad[:, 1])
            # sweep
            rot_y = np.arctan2(self.grad[:, 0], self.grad[:, 2] + 1.0e-20)

            # shear-sweep
            if self.shear_sweep:
                rot_y[:] = 0

        else:
            # prebend
            rot_x = np.arctan2(-self.grad[:, 1], self.grad[:, 2] + 1.0e-20)
            # sweep
            rot_y = np.arcsin(self.grad[:, 0])

            # shear-sweep ie local x is parallel to global X before twisting
            if self.shear_sweep:
                rot_y[:] = 0

        # twist
        rot_z = self.rot_z * np.pi / 180.0
        # axis for rotation
        rot_axis = np.zeros((3, 3), dtype=int)
        rot_axis[0, 0] = 1  # X-axis
        rot_axis[1, 1] = 1  # Y-axis
        rot_axis[2, 2] = 1  # Z-axis
        # Initializing the rotation matrices store
        Rot = np.zeros((3, 3, 3), dtype=float)  # 3-D based on order
        # define the axes from the rotation matrix per section
        X_bar_unit = np.zeros((self.ni_span, 3), dtype=float)
        Y_bar_unit = np.zeros((self.ni_span, 3), dtype=float)
        Z_bar_unit = np.zeros((self.ni_span, 3), dtype=float)
        # Points for each cross-section
        Pb = np.zeros((self.ni_chord, 3), dtype=float)
        # vector of the profile in format xi,yi,zi where i belongs to [0, Nc)
        p = np.zeros(3 * self.ni_chord, dtype=float)
        # construct the profile array
        ind_p = np.arange(0, 3 * self.ni_chord, step=3, dtype=int)
        #
        twist = np.zeros((self.ni_span), dtype=float)

        for i in range(self.ni_span):
            # Rx: prebend
            Rot[0, :, :] = RotMat(rot_axis[0, :], rot_x[i])
            # Ry: sweep
            Rot[1, :, :] = RotMat(rot_axis[1, :], rot_y[i])
            # Rz: twist
            # Rotation matrix
            R = np.dot(Rot[rot_order[2], :, :], Rot[rot_order[1], :, :])
            #
            if self.rotorder_sweep:
                if self.flag_twist_corr == "PGL":
                    twist_corr = self._twist_correction(R, Vtheta_unit[i])
                elif self.flag_twist_corr == "HAWC2":
                    twist_corr = np.arctan2(R[0, 1], R[0, 0])
                # Rotation matrix after applying twist correction
                Rot[2, :, :] = RotMat(rot_axis[2, :], twist_corr)

                # corect the twist
                twist[i] = rot_z[i] + twist_corr

            else:
                twist[i] = rot_z[i]

            # Rz:
            Rot[2, :, :] = RotMat(rot_axis[2, :], twist[i])
            # Rotation matrix final
            R = np.dot(R, Rot[rot_order[0], :, :])

            # store the local X, Y and Z axes
            X_bar_unit[i, :] = R[:, 0]
            Y_bar_unit[i, :] = R[:, 1]
            Z_bar_unit[i, :] = R[:, 2]

            # construct the transformation matrix for the cross-section
            T = transformation_matrix(
                X_bar_unit[i, :],
                Y_bar_unit[i, :],
                Z_bar_unit[i, :],
                self.ni_chord,
            )
            #
            # construct the vector for cross-section
            p[ind_p] = x[:, i, 0]
            p[ind_p + 1] = x[:, i, 1]
            p[ind_p + 2] = x[:, i, 2]
            # multiply and obtain the cross-section in body cs
            P = np.dot(T.toarray(), p)

            # store the vector in Nsx3 format
            Pb[:, 0] = P[ind_p]
            Pb[:, 1] = P[ind_p + 1]
            Pb[:, 2] = P[ind_p + 2]

            # build the surface by vectorially adding the locations of sections
            X[:, i, 0] = Pb[:, 0] + self.x[i]
            X[:, i, 1] = Pb[:, 1] + self.y[i]
            X[:, i, 2] = Pb[:, 2] + self.z[i]

        # save the twist_correction
        self.twist_corrected = twist
        # save the local cross-sectional axes
        self.X_bar_unit = X_bar_unit
        self.Y_bar_unit = Y_bar_unit
        self.Z_bar_unit = Z_bar_unit

        return X

    def _twist_correction(self, R, Vtheta_unit):
        """
        Returns the angles by which the twist has to be corrected.

        """
        # V_theta in local co-ordinates = inv(R)*V_theta_unit
        Vtheta_local = np.linalg.solve(R, Vtheta_unit)

        # twist correction angle
        twist_corr = np.arctan2(Vtheta_local[1], Vtheta_local[0])

        return twist_corr

    def _rotation_direction(self):
        """
        Returns the direction of the local velocity vector tangential to the
        rotor undergoing pure rotation without external inflow.

        """
        # position vectors
        P = np.array([self.x, self.y, self.z]).T
        P[0, :] += 1.0e-20
        # unit vectors
        P_unit = np.zeros((P.shape), dtype=float)
        P_norm = np.linalg.norm(P, axis=1)
        P_unit[:, 0] = np.divide(P[:, 0], P_norm)  # x
        P_unit[:, 1] = np.divide(P[:, 1], P_norm)  # y
        P_unit[:, 2] = np.divide(P[:, 2], P_norm)  # z
        # Rotation vector
        R_unit = np.zeros((P.shape), dtype=float)
        R_unit[:, 1] = 1.0

        # direction of V_theta
        Vtheta = np.cross(R_unit, P_unit, axisa=1, axisb=1)
        # Vtheta_unit vector
        Vtheta_unit = np.zeros((Vtheta.shape), dtype=float)
        Vtheta_norm = np.linalg.norm(Vtheta, axis=1)
        Vtheta_unit[:, 0] = np.divide(Vtheta[:, 0], Vtheta_norm)  # x
        Vtheta_unit[:, 1] = np.divide(Vtheta[:, 1], Vtheta_norm)  # y
        Vtheta_unit[:, 2] = np.divide(Vtheta[:, 2], Vtheta_norm)  # z

        return Vtheta_unit

    def _analytic_gradient(self, axis):
        """
        Peforms a pchip interpolation and rturns the uit direction vector

        """
        s = axis.s
        points = axis.points
        splx = axis._splines[0]  # store pchip spline function for x = f(s)
        sply = axis._splines[1]  # store pchip spline function for y = f(s)
        splz = axis._splines[2]  # store pchip spline function for z = f(s)
        #
        grad = np.zeros((points.shape), dtype=float)
        grad_unit = np.zeros((points.shape), dtype=float)
        #
        grad[:, 0] = splx(s, nu=1)
        grad[:, 1] = sply(s, nu=1)
        grad[:, 2] = splz(s, nu=1)
        # calculate norm for each span section
        grad_norm = np.linalg.norm(grad, axis=1)
        # obtain the unit direction vector
        grad_unit[:, 0] = np.divide(grad[:, 0], grad_norm)
        grad_unit[:, 1] = np.divide(grad[:, 1], grad_norm)
        grad_unit[:, 2] = np.divide(grad[:, 2], grad_norm)

        return grad_unit

    def _redistribute(self, af, pos_z, i, dist=None):
        if self.redistribute_flag is False:
            return af, None

        # airfoil = AirfoilShape(points=points, spline='cubic')
        try:
            dist_LE = np.interp(pos_z, self.dist_LE[:, 0], self.dist_LE[:, 1])
        except IndexError:
            dist_LE = None
        # pass airfoil to user defined routine to allow for additional configuration
        # airfoil = self._set_airfoil(af, pos_z)
        if self.x_chordwise.shape[0] > 0:
            af = af.redistribute_chordwise(self.x_chordwise)
        else:
            dTE = self.dTE
            if self.dTE == "empirical":
                dTE = af.smax / self.ni_chord / 10.0
            af = af.redistribute(
                ni=self.ni_chord,
                dLE=dist_LE,
                dTE=dTE,
                dist=dist,
                close_te=self.chord_nte,
            )
        self.LE[i] = np.array([af.LE[0], af.LE[1], pos_z])
        self.TE[i] = np.array([af.TE[0], af.TE[1], pos_z])
        return af, af.s

    def _open_trailing_edge(self, af, i):
        """
        Ensure that airfoil training edge thickness > minTE
        """
        if self.minTE == 0.0:
            return af

        if i == 0:
            return af
        # af = AirfoilShape(points=points)
        t = np.abs(af.points[-1, 1] - af.points[0, 1]) * self.chord[i]
        if t < self.minTE:
            af.open_trailing_edge(self.minTE / self.chord[i])

        return af

    def _set_airfoil(self, airfoil, pos_z):
        if hasattr(self, "gf_height"):
            height = self.gf_height(pos_z)
            length_factor = self.gf_length_factor(pos_z)
            print("gf", pos_z, height, length_factor)
            if height > 0.0:
                airfoil = airfoil.gurneyflap(height, length_factor)
        if hasattr(self, "flap_length_factor"):
            length = self.flap_length_factor(pos_z)
            blendf = self.blend_length_factor(pos_z)
            hingef = self.hinge_height_fact(pos_z)
            alpha = self.flap_alpha_deg(pos_z)
            print("flap", pos_z, length, blendf, hingef, alpha)
            if length > 0.0:
                airfoil = airfoil.flap(length, blendf, hingef, alpha)

        return airfoil

    def _interpolate_chordwise_dist(self, zarray):
        """
        based on the information provided by dist_chord,
        prepares the corresponding set of chordwise
        distribution functions for every span.
        Those will be passed as an input to the airfoil class.
        """

        # distionary with normalized span as keys, and list of control points as values
        interpdistch = {}

        if self.dist_chord == {}:
            # if not activated by the user, give a None distribution
            # for every span location
            for zval in zarray:
                interpdistch[zval] = None
        else:
            # initialization of the dist functions for every mesh span
            for zval in zarray:
                interpdistch[zval] = []
            for indnow in list(self.dist_chord.keys()):
                # access the data and sort it by span
                data = self.dist_chord[indnow]
                data.sort(key=lambda x: float(x[0]))
                # proceed with the interpolation, or give an homogeneous distribution
                splst = [row[0] for row in data]
                chordlst = [row[1] for row in data]
                sizelst = [row[2] for row in data]
                #
                if len(splst) == 1:
                    for zval in zarray:
                        interpdistch[zval].append(
                            [chordlst[0], sizelst[0], indnow]
                        )
                else:
                    # We assume that outside of the interpolation limits we have the
                    # values of the extremes. Another idea could be to 'relax'
                    # the control point outside of the
                    # defined span limits. But this is very cumbersome since the
                    # sections are understood as independent
                    # here, and no spanwise smoothing is applied (leading to high mesh
                    # torsion in most of the cases).
                    for zval in zarray:
                        if zval < splst[0]:
                            splst = [zval] + splst
                            chordlst = [chordlst[0]] + chordlst
                            sizelst = [sizelst[0]] + sizelst
                        if zval > splst[-1]:
                            splst.append(zval)
                            chordlst.append(chordlst[-1])
                            sizelst.append(sizelst[-1])
                    # we perform the interpolation
                    sizeintp = pchip(splst, sizelst)
                    chordintp = pchip(splst, chordlst)
                    for zval in zarray:
                        interpdistch[zval].append(
                            [
                                float(chordintp(zval)),
                                float(sizeintp(zval)),
                                indnow,
                            ]
                        )
        # printing out the resulting set of dist functions (set to True for debugging)
        isprint = False
        if isprint is True:
            for zval in zarray:
                print(
                    "additional dist funct for span %s\n\t%s"
                    % (zval, interpdistch[zval])
                )
        return interpdistch
