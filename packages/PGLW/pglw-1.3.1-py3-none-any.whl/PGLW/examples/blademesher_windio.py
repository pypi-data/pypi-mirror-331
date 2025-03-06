import os
from importlib import resources
import numpy as np
from scipy.interpolate import interp1d

from PGLW.main.blademesher import BladeMesher
from PGLW.main.domain import write_x2d
from PGLW.main.geom_tools import calculate_length
from PGLW.main.windio import WindIOReader

from openmdao.utils.spline_distributions import sine_distribution

data_path = os.path.join(resources.files("PGLW"), "test", "data")
r = WindIOReader(os.path.join(data_path, "IEA-22-280-RWT_v1.0.1.yaml"))

geom_data = r.read_windio()
hub_length = r.get_scaled_hub_length()
blade_length = r.get_blade_length()
root_diameter = r.get_scaled_root_diameter()
cone_angle = r.get_cone()
print("BLADE LENGTH", blade_length)

m = BladeMesher()
m.c2d_flag = True
m.build_rotor = True

# cone is added in EllipSys
m.cone_angle = cone_angle
m.hub_radius = hub_length
m.root_diameter = root_diameter
m.s_start_c2d = m.hub_radius

m.pf = geom_data["pf"]

# spanwise and chordwise number of vertices
m.ni_span = 129
m.ni_chord = 257

m.base_airfoils = geom_data["base_airfoils"]["coords"]
m.blend_var = geom_data["base_airfoils"]["rthick"]

from PGLW.main.airfoil import AirfoilShape

af = AirfoilShape(points=m.base_airfoils[-1][5:-5, :].copy())
af.redistribute(ni=200)
m.base_airfoils[-1] = af.points.copy()


# redistribute points chordwise
m.redistribute_flag = True
m.surface_spline = "cubic"
# number of points on blunt TE
m.chord_nte = 9
# set min TE thickness to 5 mm (scaled)
m.minTE = 3.5211267605633805e-05

# user defined cell size at LE
# when left empty, ds will be determined based on
# LE curvature
m.dist_LE = np.array(
    [np.linspace(0, 1, 10), np.linspace(0.0012, 0.0008, 10)]
).T

m.root_type = "cylinder"
m.ni_root = 5
m.s_root_start = 0.0
m.s_root_end = 0.05
m.ds_root_start = 0.015
m.ds_root_end = 0.015


# inputs to the tip component
# note that most of these don't need to be changed
m.ni_tip = 10
m.s_tip_start = 0.9985
m.s_tip = 0.9991
m.ds_tip_start = 0.0003
m.ds_tip = 0.0001

m.tip_fLE1 = 0.8  # Leading edge connector control in spanwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fLE2 = 0.8  # Leading edge connector control in chordwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fTE1 = 0.8  # Trailing edge connector control in spanwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fTE2 = 0.8  # Trailing edge connector control in chordwise direction.
# pointy tip 0 <= fLE1 => 1 square tip.
m.tip_fM1 = 1.0  # Control of connector from mid-surface to tip.
# straight line 0 <= fM1 => orthogonal to starting point.
m.tip_fM2 = 0.0  # Control of connector from mid-surface to tip.
# straight line 0 <= fM2 => orthogonal to end point.
m.tip_fM3 = 0.02  # Controls thickness of tip.
# 'Zero thickness 0 <= fM3 => 1 same thick as tip airfoil.

m.tip_dist_cLE = 0.000035  # Cell size at tip leading edge starting point.
m.tip_dist_cTE = 0.000035  # Cell size at tip trailing edge starting point.
m.tip_dist_tip = 0.00005  # Cell size of LE and TE connectors at tip.
m.tip_dist_mid0 = 0.00005  # Cell size of mid chord connector start.
m.tip_dist_mid1 = 0.00001  # Cell size of mid chord connector at tip.

m.tip_c0_angle = 30.0  # Angle of connector from mid chord to LE/TE

m.tip_nj_LE = 22  # Index along mid-airfoil connector used as starting point for tip connector


# generate the mesh
m.update()
m.build_rotor_domain()
m.domain.write_plot3d("IEA22MW_surfacemesh.xyz")
from PGLW.main.domain import write_plot3d_f

write_plot3d_f(m.domain, "IEA22MW_surfacemesh.f")
m.main_section.domain.write_plot3d("IEA22MW_surface.xyz")

m.domain.split_blocks(33)

write_x2d(m.domain, "grid.x2d", scale_factor=r.get_rotor_radius())
m.write_c2d()
