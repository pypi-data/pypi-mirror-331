import numpy as np

from PGLW.main.bladecap import RootCap
from PGLW.main.bladeroot import CoonsBladeRoot
from PGLW.main.bladetip import CoonsBladeTip
from PGLW.main.curve import Curve
from PGLW.main.domain import Block, Domain
from PGLW.main.geom_tools import calculate_length
from PGLW.main.loftedblade import LoftedBladeSurface
from PGLW.main.nacelle import CoonsNacelle
from PGLW.main.planform import RedistributedPlanform, read_blade_planform


class BladeMesher(object):
    """
    Generates a CFD ready structured grid blade surface mesh

    Parameters
    ----------
    pf: dict
        optional dictionary containing planform. If not supplied,
        planform_filename is required. Keys:

        |  s: normalized running length of blade
        |  x: x-coordinates of blade axis
        |  y: y-coordinates of blade axis
        |  z: z-coordinates of blade axis
        |  rot_x: x-rotation of blade axis
        |  rot_y: y-rotation of blade axis
        |  rot_z: z-rotation of blade axis
        |  chord: chord distribution
        |  rthick: relative thickness distribution
        |  p_le: pitch axis aft leading edge distribution
    planform_filename: str
        optional path to planform file. If not supplied, pf is required.
    base_airfoils_path: list
        list of string paths to airfoils
    interp_type: str
        airfoil interpolation blending variable: rthick or span
    blend_var: array
        airfoil interpolation blending factors, which will typically
        be the relative thicknesses of the airfoils in base_airfoils.
    ni_span: int
        number of points in the spanwise direction (including root)
    ni_chord: int
        number of points in the chordwise direction
    chord_nte: int
        number of points on trailing edge
    redistribute_flag: bool
        flag for switching on chordwise redistribution of points along the span,
        defaults to True if close_te = True.
    dist_LE: array
        2D array containing LE cell size as function of normalized span.
        If empty, LE cell size will be set according to LE curvature.
    dist_chord: dict
        dictionary defining a set of control points in the chordwise direction
        as a function of span.
        See the loftedblade class for a full description of this variable.
    minTE: float
        minimum trailing edge thickness.
    surface_spline: str
        spline type used to interpolate airfoil family
    gf_heights: array
        array containing s, gf_height, gf_length factor
    flaps: array
        array containing s, flap_length_factor, blend_length_factor, hinge_height_fact,
        flap_alpha_deg
    tip_fLE1: float
        Leading edge connector control in spanwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    tip_fLE2: float
        Leading edge connector control in chordwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    tip_fTE1: float
        Trailing edge connector control in spanwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    tip_fTE2: float
        Trailing edge connector control in chordwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    tip_fM1: float
        Control of connector from mid-surface to tip.
        straight line 0 <= fM1 => orthogonal to starting point.
    tip_fM2: float
        Control of connector from mid-surface to tip.
        straight line 0 <= fM2 => orthogonal to end point.
    tip_fM3: float
        Controls thickness of tip.
        Zero thickness 0 <= fM3 => 1 same thick as tip airfoil.
    tip_dist_cLE: float
        Cell size at tip leading edge starting point.
    tip_dist_cTE: float
        Cell size at tip trailing edge starting point.
    tip_dist_tip: float
        Cell size of LE and TE connectors at tip.
    tip_dist_mid0: float
        Cell size of mid chord connector start.
    tip_dist_mid1: float
        Cell size of mid chord connector at tip.
    tip_c0_angle: float
        Angle of connector from mid chord to LE/TE
    tip_nj_LE: int
        Index along mid-airfoil connector used as starting point for tip connector
    hub_radius: float
        radial extent of the cylindrical hub used for simplified
        rotor only simulations. Specified as fraction of blade length.
        use only if the planform definition does not contain
        the hub already!
    root_type: str
        options are 'cylinder' or 'nacelle', 'cap' or 'tip' (for 1 bladed turbines)
    hub_length: float
        length of the hub, extending from spinner end to nacelle start
        used only for generating spinner/nacelle mesh
    nacelle_curve: array
        2D nacelle shape curve oriented in x-y with blade root center
        at x=0 and spinner tip at -x
    nacelle_shape_file: str
        file containing 2D cross sectional shape of nacelle
        (only needed if nacelle_curve is not provided)
    ds_nacelle: float
        cell size at nacelle start
    nb_nacelle: int
        number of blocks in the flow direction on nacelle surface
    base_nv: int
        number of points on hub in spanwise direction
        (ni on blade will be ni_root - base_nv)
    cap_Fcap: float
        size of four block patch as a fraction of the root
        diameter, range 0 < Fcap < 1.
    cap_Fblend: float
        factor controlling shape of four block patch.
        | Fblend => 0. takes the shape of tip_con,
        | Fblend => 1. takes the shape of a rectangle.
    cap_direction: float
        Blade direction along z-axis: 1 positive z, -1 negative z
    s_start_c2d: float
        Non-dimensional spanwise distance from the rotor center
        where the c2d spanwise coordinate should start

    Returns
    -------
    domain: object
        PGLW.main.domain.Domain object containing the surface mesh
    """

    def __init__(self, **kwargs):
        super(BladeMesher, self).__init__()

        self.build_rotor = False

        self.hub_radius = 0.0
        self.hub_length = 0.0
        self.s_tip_start = 0.99
        self.s_tip = 0.995
        self.s_root_start = 0.0
        self.s_root_end = 0.05
        self.ds_root_start = 0.008
        self.ds_root_end = 0.005
        self.ds_tip_start = 0.001
        self.ds_tip = 0.00005
        self.ni_span = 129
        self.ni_root = 8
        self.ni_tip = 11
        self.n_refined_tip = 50
        self.dist = np.array([])

        self.refine_tip = False
        self.dist_LE = np.array([])

        self.tip_fLE1 = 0.5
        self.tip_fLE2 = 0.5
        self.tip_fTE1 = 0.5
        self.tip_fTE2 = 0.5
        self.tip_fM1 = 1.0
        self.tip_fM2 = 1.0
        self.tip_fM3 = 0.3
        self.tip_dist_cLE = 0.0002
        self.tip_dist_cTE = 0.0002
        self.tip_dist_tip = 0.0002
        self.tip_dist_mid0 = 0.0002
        self.tip_dist_mid1 = 0.00004
        self.tip_c0_angle = 30.0
        self.tip_nj_LE = 20
        self.Ptip = np.array([])

        self.nblades = 3
        self.root_diameter = 0.0
        self.root_type = "cylinder"
        self.nb_nacelle = 1

        self.pf = {}
        self.planform_filename = ""
        self.planform_spline = "akima"
        self.base_airfoils = []
        self.base_airfoils_path = []
        self.blend_var = np.array([])
        self.ni_chord = 257
        self.ni_span = 129
        self.chord_nte = 11
        self.redistribute_flag = False
        self.minTE = 0.0
        self.interp_type = "rthick"
        self.surface_spline = "pchip"
        self.user_surface_file = ""
        self.user_surface = np.array([])
        self.gf_heights = np.array([])
        self.dist_chord = {}
        self.flaps = np.array([])
        self.rot_order = np.array([2, 1, 0])
        self.cone_angle = 0.0
        self.shear_sweep = False
        self.pitch_setting = 0.0
        self.c2d_flag = False
        self.s_start_c2d = 0.0

        self.connectors = []
        self.domain = Domain()

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

        self._setup_called = False

    def setup(self):
        # redistribute the planform
        if len(self.planform_filename) > 0:
            self.pf = read_blade_planform(self.planform_filename)
        # add hub if specified
        if self.hub_radius > 0:
            if self.hub_radius > 0.1:
                raise RuntimeError(
                    "Hub length has to be specified as a"
                    "fraction of blade length, got %f" % self.hub_radius
                )
            for name in list(self.pf.keys()):
                if not isinstance(self.pf[name], np.ndarray):
                    continue
                arr = np.zeros(self.pf[name].shape[0] + 1)
                arr[1:] = self.pf[name]
                arr[0] = self.pf[name][0]
            scaler = 1.0 / (1.0 + self.hub_radius)
            self.pf["z"] = self.pf["z"] + self.hub_radius
            self.pf["z"] *= scaler
            self.pf["z"][0] = 0.0
            self.pf["chord"] *= scaler
            self.pf["x"] *= scaler
            self.pf["y"] *= scaler
            s = calculate_length(
                np.array([self.pf["x"], self.pf["y"], self.pf["z"]]).T
            )
            self.pf["s"] = s / s[-1]
        self.pf_spline = RedistributedPlanform(**self.__dict__)
        #       if self.user_surface_file or self.user_surface.shape[0] > 0:
        #           self.pf_spline.only_s = True
        self.pf_spline.update()
        self.pf = self.pf_spline.pf_out
        if not self.user_surface_file and not self.user_surface.shape[0] > 0:
            ax = Curve(
                points=np.array([self.pf["x"], self.pf["y"], self.pf["z"]]).T
            )
            # ax.rotate_x(self.cone_angle)
            self.pf["x"] = ax.points[:, 0]
            self.pf["y"] = ax.points[:, 1]
            self.pf["z"] = ax.points[:, 2]

        self.itip_start = self.ni_span - self.ni_tip

        # generate main section
        if len(self.base_airfoils_path) > 0:
            self.base_airfoils = []
        for name in self.base_airfoils_path:
            self.base_airfoils.append(np.loadtxt(name))
        self.main_section = LoftedBladeSurface(**self.__dict__)

        self.axis = Curve(
            points=np.array([self.pf["x"], self.pf["y"], self.pf["z"]]).T
        )

        # generate root
        if self.ni_root > 0:
            if self.root_type == "cylinder":
                self.root = CoonsBladeRoot(**self.__dict__)
            elif self.root_type == "nacelle":
                self.root = CoonsNacelle(**self.__dict__)
            elif self.root_type == "cap":
                self.root = RootCap(**self.__dict__)
            elif self.root_type == "tip":
                self.root = CoonsBladeTip(**self.__dict__)

        # generate tip
        self.tip = CoonsBladeTip(**self.__dict__)
        self.tip.ibase = self.itip_start
        self._setup_called = True

    def update(self):
        if not self._setup_called:
            self.setup()

        self.main_section.update()

        self.tip.main_section = self.main_section.domain.blocks[
            "block-0000"
        ]._block2arr()[:, :, 0, :]
        self.tip.axis = self.axis
        if self.Ptip.shape[0] == 0:
            try:
                self.tip.Ptip = self.axis.points[-1, :]
            except RuntimeError:
                print(
                    "You need to specity the parameter `Ptip`"
                    "since theres no planform provided"
                )
        self.tip.update()

        # assemble mesh and join blocks
        x = self.main_section.domain.blocks["block-0000"]._block2arr()[
            :, :, 0, :
        ]
        self.domain = Domain()

        if self.root_type in ["cylinder", "nacelle", "tip", "cap"]:
            ni_root = self.ni_root
        block = Block(
            x[:, np.maximum(0, ni_root - 1) : self.itip_start + 1, 0],
            x[:, np.maximum(0, ni_root - 1) : self.itip_start + 1, 1],
            x[:, np.maximum(0, ni_root - 1) : self.itip_start + 1, 2],
            name="main_section",
        )
        if self.c2d_flag:
            c2d = self.main_section.c2d
            block.add_scalar(
                "c2d0",
                np.atleast_3d(
                    c2d[:, np.maximum(0, ni_root - 1) : self.itip_start + 1, 0]
                ),
            )
            block.add_scalar(
                "c2d1",
                np.atleast_3d(
                    c2d[:, np.maximum(0, ni_root - 1) : self.itip_start + 1, 1]
                ),
            )
            block.add_scalar(
                "c2d2",
                np.atleast_3d(
                    c2d[:, np.maximum(0, ni_root - 1) : self.itip_start + 1, 2]
                ),
            )
        self.domain.add_blocks(block)

        self.domain.add_domain(self.tip.domain)

        if self.pitch_setting != 0.0:
            self.domain.rotate_z(self.pitch_setting)
            self.axis.rotate_z(self.pitch_setting)
        if self.cone_angle != 0.0:
            self.domain.rotate_x(self.cone_angle)
            self.axis.rotate_x(self.cone_angle)
        if self.root_type == "tip":
            self.root.axis = Curve(points=self.axis.points[::-1])
            self.root.Ptip = np.array(
                [
                    self.domain.blocks["main_section"]
                    ._block2arr()[:, 0, 0, i]
                    .mean()
                    for i in range(3)
                ]
            )
            self.root.main_section = self.domain.blocks[
                "main_section"
            ]._block2arr()[:, ::-1, 0, :]
            self.root.Ptip = self.axis.points[0, :]

        if self.ni_root > 0:
            if self.root_type in ["cylinder", "nacelle", "cap"]:
                self.root.tip_con = self.domain.blocks[
                    "main_section"
                ]._block2arr()[:, 0, 0, :]
                self.root.Proot = self.axis.points[0, :]
            self.root.axis = self.axis
            if self.root_type == "cylinder" and self.root_diameter == 0.0:
                try:
                    self.root.root_diameter = self.pf["chord"][0]
                except RuntimeError:
                    print(
                        "You need to specify the parameter `root_diameter`"
                        "since theres no planform provided"
                    )

            self.root.update()

        self.domain.join_blocks(
            "tip-base", "main_section", newname="main_section"
        )

        if self.ni_root > 0:
            if self.root_type == "tip":
                self.root.domain.blocks["tip_patch_P-split00"].transpose()
                self.root.domain.blocks["tip_patch_P-split01"].transpose()
                self.root.domain.blocks["tip_patch_S-split00"].transpose()
                self.root.domain.blocks["tip_patch_S-split01"].transpose()
                self.domain.add_domain(self.root.domain)
                self.domain.join_blocks(
                    "tip-base", "main_section", newname="main_section"
                )
            else:
                self.domain.add_domain(self.root.domain)
                self.domain.join_blocks(
                    "root", "main_section", newname="main_section"
                )

        self.domain.add_group("blade1", list(self.domain.blocks.keys()))

    def build_rotor_domain(self):
        """
        copy and rotate blade 1 to nblades
        """

        # rotate domain with flow direction in the z+ direction and
        # blade1 in y+ direction
        self.domain.rotate_x(-90)
        self.domain.rotate_y(180)

        # copy blade 1 to blade 2 and 3 and rotate
        self.domain.add_group("blade1", list(self.domain.blocks.keys()))
        for i in range(1, self.nblades):
            b2blocks = self.domain.copy_blocks(
                groups=["blade1"], newnamebase="blade%i" % (i + 1)
            )
            self.domain.add_group("blade%i" % (i + 1), b2blocks)
            rot = (-360.0 / self.nblades) * i
            self.domain.rotate_z(rot, groups=["blade%i" % (i + 1)])

        # assign c2d identifiers to each blade
        if self.c2d_flag:
            for b in range(self.nblades):
                for block in self.domain.groups["blade%i" % (b + 1)]:
                    for j in range(self.domain.blocks[block].nj):
                        for i in range(self.domain.blocks[block].ni):
                            if (
                                self.domain.blocks[block].scalars["c2d2"][
                                    i, j, 0
                                ]
                                == 0
                            ):
                                self.domain.blocks[block].scalars["c2d2"][
                                    i, j, 0
                                ] = (b + 1)

        # split blocks to cubes of size 33^3
        # self.domain.split_blocks(33)

    def add_dist_point(self, s, ds, index):
        """
        Add distribution points to distfunc

        Parameters
        ----------
        s : float
            Curve fraction, where 0 is at the root, and 1 at the tip.
        ds : float
            Normalized distance between points. Total curve length is 1. When
            set to -1 distfunc will figure something out.
        index : int
            Force index number on the added point.
        """

        self.dist = np.asarray(self.dist)

        try:
            if s in self.dist[:, 0]:
                return
        except RuntimeError:
            pass
        try:
            self.dist = np.append(
                self.dist, np.array([[s, ds, index]]), axis=0
            )
        except RuntimeError:
            self.dist = np.array([[s, ds, index]])

        self.dist = self.dist[np.argsort(self.dist[:, 0]), :]

    def write_c2d(self):
        b0 = self.domain.blocks[list(self.domain.blocks.keys())[0]]
        bsize = b0.ni
        nblock = len(self.domain.blocks)
        with open("grid.c2d", "w") as f:
            f.write("%i %i\n" % (bsize, nblock))
            for name, block in sorted(self.domain.blocks.items()):
                c2d0 = block.scalars["c2d0"].flatten(order="F")
                c2d1 = block.scalars["c2d1"].flatten(order="F")
                c2d2 = block.scalars["c2d2"].flatten(order="F")
                for i in range(c2d0.shape[0]):
                    f.write(
                        " %24.18e   %24.18e   %24.18e\n"
                        % (c2d0[i], c2d1[i], c2d2[i])
                    )
