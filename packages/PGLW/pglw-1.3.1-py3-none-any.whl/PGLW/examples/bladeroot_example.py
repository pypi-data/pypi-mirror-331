from builtins import range

import numpy as np

from PGLW.main.bladeroot import CoonsBladeRoot
from PGLW.main.curve import Curve

# this curve will genererally be extracted from the main blade section surface
# but in this example we generate it manually
root_radius = 0.03
ni = 257
tip_con = np.zeros([ni, 3])
tip_con[:, 2] = 0.05
for i in range(257):
    tip_con[i, 0] = -root_radius * np.cos(360.0 * i / (ni - 1) * np.pi / 180.0)
    tip_con[i, 1] = -root_radius * np.sin(360.0 * i / (ni - 1) * np.pi / 180.0)

tip_con = Curve(tip_con)
tip_con.rotate_z(14.5)

root = CoonsBladeRoot()
root.tip_con = tip_con.points
root.nblades = 3  # Number of blades
root.ds_root_start = 0.006  # spanwise distribution at root start
root.ds_root_end = 0.003  # spanwise distribution at root end
root.s_root_start = 0.0  # spanwise position of root start
root.s_root_end = 0.05  # spanwise position of root end
root.ni_root = 8  # number of spanwise points
root.root_diameter = 0.06

root.update()
