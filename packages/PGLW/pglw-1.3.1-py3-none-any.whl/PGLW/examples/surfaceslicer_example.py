import numpy as np

from PGLW.main.loftedblade import LoftedBladeSurface
from PGLW.main.planform import read_blade_planform, redistribute_planform
from PGLW.main.surfaceslicer import SlicedLoftedSurface

pf = read_blade_planform("data/DTU_10MW_RWT_blade_axis_prebend.dat")

dist = [[0, 0.01, 1], [0.05, 0.01, 8], [0.98, 0.001, 119], [1.0, 0.0005, 140]]

pf = redistribute_planform(pf, dist=dist)

d = LoftedBladeSurface()
d.pf = pf
d.redistribute_flag = True
# d.minTE = 0.0

d.blend_var = [0.241, 0.301, 0.36, 1.0]
for f in [
    "data/ffaw3241.dat",
    "data/ffaw3301.dat",
    "data/ffaw3360.dat",
    "data/cylinder.dat",
]:
    d.base_airfoils.append(np.loadtxt(f))

d.update()
# d.domain.write_plot3d('exampleblade_lofted.xyz')

# =============================================================================
# ===========surface_slicer implementation begins here=========================
# =============================================================================
# create an object of the surface slicer class
m = SlicedLoftedSurface()
m.verbose = True

# input the generated lofted surface using loftedblade.py
# alternatively a surface of shape: (Nchord, Nspan ,3) can be inputed manually
m.surface = d.surface

# set the number of span sections: <=d.ni_span
m.ni_span = d.ni_span

# set the number of points on the slice: <= d.ni_chord
m.ni_slice = d.ni_chord

# flag for including tip: default value = True
m.include_tip = True

# set the blade length that it should be scaled with: default value = 1.0
m.blade_length = 1.0

# -------------- set the spanwise distribution------------------------------
# It is recommended that Option 1 and Option 2, both have same discretization
# as the LoftedSurface
# Option 1: dist (refer to docs for explanation).
# m.dist = dist

# Option 2: s (spanwise distribution of blade curve length)
# m.s = pf['s']

# Option 3: Not setting a specific the above two, proceeds with linear distribution
# -----------------------------------------------------------------------------
# set the residual tolerance according to the blade length. Unit is in [m]
# default value = 1.e-5
m.tol = 1e-3

# generate the surface
m.update()

# final surface in parallel Z= c planes
surface = m.sliced_surface

# uncomment to save the file
# filename = 'test'
# np.save(filename,surface)

# uncomment the code shown below to produce a .xyz file for visualizaion
# m.domain.write_plot3d('exampleblade_sliced.xyz')
