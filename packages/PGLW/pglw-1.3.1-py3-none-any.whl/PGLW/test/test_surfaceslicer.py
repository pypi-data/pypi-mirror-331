#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 13:30:24 2018

@author: antariksh
"""
import unittest

import numpy as np

from PGLW.main.loftedblade import LoftedBladeSurface
from PGLW.main.planform import read_blade_planform, redistribute_planform
from PGLW.main.surfaceslicer import SlicedLoftedSurface


class SurfaceSlicerTests(unittest.TestCase):
    """
    Tests for components.surfaceslicer.py

    """

    def setUp(self):
        unittest.TestCase.setUp(self)

        # initialize the loftedbladesurface and generate it
        pf = read_blade_planform("data/DTU_10MW_RWT_blade_axis_prebend.dat")
        dist = [
            [0, 0.01, 1],
            [0.05, 0.01, 8],
            [0.98, 0.001, 119],
            [1.0, 0.0005, 140],
        ]

        pf = redistribute_planform(pf, dist=dist)
        self.d = LoftedBladeSurface()
        self.d.pf = pf
        self.d.redistribute_flag = True
        # self.d.minTE = 0.0
        self.d.blend_var = [0.241, 0.301, 0.36, 1.0]
        for f in [
            "data/ffaw3241.dat",
            "data/ffaw3301.dat",
            "data/ffaw3360.dat",
            "data/cylinder.dat",
        ]:
            self.d.base_airfoils.append(np.loadtxt(f))

        self.d.update()

        # run surface slicer
        self.m = SlicedLoftedSurface()
        self.m.verbose = False
        self.m.surface = self.d.surface
        self.m.ni_span = 5
        self.m.ni_slice = 5
        self.m.update()

        # load the solved data
        self.solved_surface = np.load("data/sliced_surface_s5_c5.npy")

    def test_sliced_surface(self):
        """
        Tests if the generated sliced surface is equal to a known slice

        """

        self.assertEqual(
            np.testing.assert_allclose(
                self.solved_surface, self.m.sliced_surface, atol=1e-3
            ),
            None,
        )


if __name__ == "__main__":
    unittest.main()
