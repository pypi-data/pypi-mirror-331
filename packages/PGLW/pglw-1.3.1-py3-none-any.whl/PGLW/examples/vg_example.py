from PGLW.main.vgmesher import VGMesher

v = VGMesher()

# airfoil shape
v.airfoil_filename = "data/ffaw3301.dat"

# VG geometry
v.h = 0.01
v.len = 0.02
v.w = 0.00015
v.delta1 = 0.045
v.delta2 = 0.04
v.beta = 15.0

# chordwise position of VG
v.xc_vg = 0.2

# base plate length and radius of fillet between plate and VG
v.l_base = 3.0
v.dr_base = 0.06

# number of vertices on airfoi in the
# chordwise direction (excluding the VG)
v.nte = 7
v.ni = 257

# distribution of cells on VG
v.ni_base = 7
v.ni_cap = 50
v.ni_edge = 7
v.ni_mid = 20

# parameters controlling connector placement
v.fLE0 = 0.3
v.fLE1 = 0.0
v.fTE0 = 0.4
v.fTE1 = 0.4
v.fLEcap = 0.6
v.CPb0 = 0.45
v.wCap = 0.45

# run it
v.update()

# split blocks to have size 33
v.domain.split_blocks(33)

# write domain to a plot3d file
v.domain.write_plot3d("vg.xyz")

# write the domain to HypGrid2D x2d format
from PGLW.main.domain import write_x2d

v.domain.get_minmax()
# the zmin / zmax arguments sets the BCs on lateral edges to 103
write_x2d(v.domain, zmin=v.domain.zmin + 1.0e-4, zmax=v.domain.zmax - 1.0e-4)
