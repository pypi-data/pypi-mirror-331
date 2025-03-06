import numpy as np

from PGLW.main.bezier import BezierCurve
from PGLW.main.blademesher import BladeMesher
from PGLW.main.curve import Curve, SegmentedCurve
from PGLW.main.domain import write_x2d
from PGLW.main.planform import read_blade_planform

m = BladeMesher()

# path to the planform
m.planform_filename = "data/DTU_10MW_RWT_blade_axis_prebend.dat"

# spanwise and chordwise number of vertices
m.ni_span = 129
m.ni_chord = 257

# redistribute points chordwise
m.redistribute_flag = True
# number of points on blunt TE
m.chord_nte = 9
# set min TE thickness (which will open TE using AirfoilShape.open_trailing_edge)
# d.minTE = 0.0002

# user defined cell size at LE
# when left empty, ds will be determined based on
# LE curvature
# m.dist_LE = np.array([])

# airfoil family - can also be supplied directly as arrays
m.blend_var = [0.241, 0.301, 0.36, 0.48, 1.0]
m.base_airfoils_path = [
    "data/ffaw3241.dat",
    "data/ffaw3301.dat",
    "data/ffaw3360.dat",
    "data/ffaw3480.dat",
    "data/cylinder.dat",
]


# tell the mesher to add a nacelle object and generate a nacelle shape
m.root_type = "nacelle"

c = BezierCurve()
CPs = np.array(
    [
        [-6.5, 0],
        [-6.5, 1.5],
        [-4.0, 2.86],
        [-2.0, 3.0],
        [-0.5, 3.25],
        [3.5, 3.5],
    ]
)
CPs[:, 1] *= 4.0 / 3.5
CPs /= 89.166
c.CPs = CPs
c.update()
c1 = Curve(
    points=np.array(
        [np.linspace(3.5, 18.5, 100), np.linspace(4.0, 4.0, 100)]
    ).T
)
c1.points /= 89.166
sc = SegmentedCurve()
sc.add_segment(c)
sc.add_segment(c1)
sc.update()

m.nacelle_curve = sc
m.blade_root_radius = 5.38 / 2 / 89.166
m.hub_length = 6.5 / 89.166
m.dr_junction = 0.075
m.ni_root = 16
m.s_root_end = 0.065
m.ds_root_start = 0.001
m.ds_root_end = 0.005
m.base_nv = 7
m.ds_base = 0.0005
m.nacelle_dr = 0.5 / 89.166
m.ds_nacelle = 0.0012

# add additional dist points to e.g. refine the root
# for placing VGs
# self.pf_spline.add_dist_point(s, ds, index)

# inputs to the tip component
# note that most of these don't need to be changed
m.ni_tip = 11
m.s_tip_start = 0.99
m.s_tip = 0.995
m.ds_tip_start = 0.001
m.ds_tip = 0.00005

m.tip_fLE1 = 0.5  # Leading edge connector control in spanwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fLE2 = 0.5  # Leading edge connector control in chordwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fTE1 = 0.5  # Trailing edge connector control in spanwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fTE2 = 0.5  # Trailing edge connector control in chordwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fM1 = 1.0  # Control of connector from mid-surface to tip.
# straight line 0 <= fM1 => orthogonal to starting point.
m.tip_fM2 = 1.0  # Control of connector from mid-surface to tip.
# straight line 0 <= fM2 => orthogonal to end point.
m.tip_fM3 = 0.2  # Controls thickness of tip.
# 'Zero thickness 0 <= fM3 => 1 same thick as tip airfoil.

m.tip_dist_cLE = 0.0001  # Cell size at tip leading edge starting point.
m.tip_dist_cTE = 0.0001  # Cell size at tip trailing edge starting point.
m.tip_dist_tip = 0.00025  # Cell size of LE and TE connectors at tip.
m.tip_dist_mid0 = 0.00025  # Cell size of mid chord connector start.
m.tip_dist_mid1 = 0.00004  # Cell size of mid chord connector at tip.

m.tip_c0_angle = 40.0  # Angle of connector from mid chord to LE/TE

m.tip_nj_LE = 20  # Index along mid-airfoil connector used as starting point for tip connector


# generate the mesh
m.update()

# rotate domain with flow direction in the z+ direction and blade1 in y+ direction
m.domain.rotate_x(-90)
m.domain.rotate_y(180)

# copy blade 1 to blade 2 and 3 and rotate
m.domain.add_group("blade1", list(m.domain.blocks.keys()))
m.domain.rotate_z(-120, groups=["blade1"], copy=True)
m.domain.rotate_z(120, groups=["blade1"], copy=True)

# We scale back to real size with the total radius
m.domain.scale(89.166)

# split blocks to cubes of size 33^3
m.domain.split_blocks(33)

# Write EllipSys3D ready surface mesh
write_x2d(m.domain)
# Write Plot3D surface mesh
m.domain.write_plot3d("DTU_10MW_RWT_nacelle_mesh.xyz")
