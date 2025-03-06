import numpy as np

from PGLW.main.airfoil import AirfoilShape, BlendAirfoilShapes
from PGLW.main.bladetip import CoonsBladeTip
from PGLW.main.coonsblade import CoonsBlade
from PGLW.main.curve import Curve

# make an airfoil interpolator to reproduce the DTU 10MW RWT
interpolator = BlendAirfoilShapes()
interpolator.ni = 257
interpolator.spline = "pchip"
interpolator.blend_var = [0.241, 0.301, 0.36, 1.0]
for f in [
    "data/ffaw3241.dat",
    "data/ffaw3301.dat",
    "data/ffaw3360.dat",
    "data/cylinder.dat",
]:
    interpolator.airfoil_list.append(np.loadtxt(f))
interpolator.initialize()

pf = np.loadtxt("data/DTU_10MW_RWT_blade_axis_prebend.dat")

s = [0.0, 0.05, 0.2, 0.3, 0.4, 0.6, 0.8, 0.97, 1.0]
rthick = np.interp(s, pf[:, 2] / 86.366, pf[:, 7] / 100.0)
chord = np.interp(s, pf[:, 2] / 86.366, pf[:, 6] / 100.0)
twist = np.interp(s, pf[:, 2] / 86.366, pf[:, 5])
p_le = np.interp(s, pf[:, 2] / 86.366, pf[:, 8])

# chord[[0, 1]] = 4.5/86.366
# chord[-1] = 0.001

bl = CoonsBlade()

bl.np = 4
bl.chord_ni = 257

dp = ["z", "z", -1, -1, -1, -1, -1, -1, -1]
fWs = [0.5] * 9
fWs[-2] = 0.25
fWs[-1] = 0.01

for i, s in enumerate(s):
    bl.add_cross_section(
        interpolator(rthick[i]),
        pos=np.array([0, 0, s]),
        rot=np.array([0, 0, twist[i]]),
        chord=chord[i],
        p_le=p_le[i],
        dp=dp[i],
        fWs=fWs[i],
    )


bl.update()

# --- 1

tip = CoonsBladeTip()

tip.main_section = bl.domain.blocks["main_section"]._block2arr()[:, :, 0, :]

tip.fLE1 = 0.5  # Leading edge connector control in spanwise direction.
# 'pointy tip 0 <= fLE1 => 1 square tip.
tip.fLE2 = 0.5  # Leading edge connector control in chordwise direction.
# 'pointy tip 0 <= fLE1 => 1 square tip.
tip.fTE1 = 0.5  # Trailing edge connector control in spanwise direction.
# 'pointy tip 0 <= fLE1 => 1 square tip.
tip.fTE2 = 0.5  # Trailing edge connector control in chordwise direction.
# 'pointy tip 0 <= fLE1 => 1 square tip.
tip.fM1 = 1.0  # Control of connector from mid-surface to tip.
# 'straight line 0 <= fM1 => orthogonal to starting point.
tip.fM2 = 1.0  # Control of connector from mid-surface to tip.
# 'straight line 0 <= fM2 => orthogonal to end point.
tip.fM3 = 0.3  # Controls thickness of tip.
# 'Zero thickness 0 <= fM3 => 1 same thick as tip airfoil.

tip.dist_cLE = 0.0001  # Cell size at tip leading edge starting point.
tip.dist_cTE = 0.0001  # Cell size at tip trailing edge starting point.
tip.dist_tip = 0.00025  # Cell size of LE and TE connectors at tip.
tip.dist_mid0 = 0.00025  # Cell size of mid chord connector start.
tip.dist_mid1 = 0.00004  # Cell size of mid chord connector at tip.

tip.s_tip = 0.995  # Cell size at tip mid chord connector end.
tip.s_tip_start = 0.98  # Cell size at tip mid chord connector end.
tip.c0_angle = 30.0  # Angle of connector from mid chord to LE/TE
tip.ds_tip_start = 0.001  # Cell size in spanwise direction at tip domain start

tip.ni_tip = (
    20  # Index along main axis where the tip domains replace the blade_section
)
tip.nj_LE = 20  # Index along mid-airfoil connector used as starting point for tip connector

tip.Ptip = np.array([0.0, 0.0, 1.0])

tip.update()

# --- 2

# # changing the position of the tip
# tip.Ptip = np.array([0.00, 0.002, 1.])
#
# tip.fM1 = 0.25
# tip.fM2 = 0.25
# tip.update()
