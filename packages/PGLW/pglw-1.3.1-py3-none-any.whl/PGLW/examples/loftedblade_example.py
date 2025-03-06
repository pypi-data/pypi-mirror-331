import numpy as np

from PGLW.main.loftedblade import LoftedBladeSurface
from PGLW.main.planform import read_blade_planform, redistribute_planform

pf = read_blade_planform("data/DTU_10MW_RWT_blade_axis_prebend.dat")

dist = [[0, 0.01, 1], [0.05, 0.01, 8], [0.98, 0.001, 119], [1.0, 0.0005, 140]]

pf = redistribute_planform(pf, dist=dist)

d = LoftedBladeSurface()
d.pf = pf
d.redistribute_flag = True
# d.minTE = 0.0002

d.blend_var = [0.241, 0.301, 0.36, 1.0]
for f in [
    "data/ffaw3241.dat",
    "data/ffaw3301.dat",
    "data/ffaw3360.dat",
    "data/cylinder.dat",
]:
    d.base_airfoils.append(np.loadtxt(f))

d.update()
