import numpy as np

from PGLW.main.airfoil import AirfoilShape, BlendAirfoilShapes
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
