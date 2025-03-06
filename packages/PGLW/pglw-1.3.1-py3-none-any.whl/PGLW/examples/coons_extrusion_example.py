import numpy as np

from PGLW.main.airfoil import AirfoilShape
from PGLW.main.coons_extrusion import CoonsExtrusion

l0 = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"), nd=3)
# l0.spline_CPs = np.array([0, 0., 0.1, 0.2, 0.4, 0.7,1])
# l0.fit()
l0.redistribute(ni=129, dLE=True, dTE=0.001)
l0.translate_z(-1)

l1 = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"), nd=3)
# l0.spline_CPs = np.array([0, 0., 0.1, 0.2, 0.4, 0.7,1])
# l0.fit()
l1.redistribute(ni=129, dLE=True, dTE=0.001)

l2 = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat") * 12.0 / 24.0, nd=3)
l2.redistribute(ni=129, dLE=True, dTE=0.001)
l2.scale(0.6)
l2.rotate_x(-90.0)
l2.translate_x(1.25)
l2.translate_z(1)
l2.translate_y(1.5)


d0 = CoonsExtrusion(l0.points, l1.points)
d0.np = 2
# th
d0.fW0 = 0.25
d0.fW1 = 0.25
d0.interpolant = "linear"
d0.create_section()
d0.setZero(0, "z")
d0.setZero(1, -1)
d0.update_patches()

d1 = CoonsExtrusion(l1.points, l2.points)
d1.np = 1
# th
d1.fW0 = 0.8
d1.fW1 = 0.5
# d.interpolant='linear'
d1.create_section()
d1.setZero(0, "z")
#  d1.setZero(1, np.array([-.45, -.9, -.125]))
d1.update_patches()
