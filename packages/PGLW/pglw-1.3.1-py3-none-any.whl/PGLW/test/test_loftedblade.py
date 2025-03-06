import os
import unittest

import numpy as np

from PGLW.main.domain import read_plot3d
from PGLW.main.loftedblade import LoftedBladeSurface
from PGLW.main.planform import read_blade_planform, redistribute_planform


class LoftedBladeTests(unittest.TestCase):
    # Only making a lofted blade once if muliple tests are made (opposed to setUp which is run before every test)
    @classmethod
    def setUpClass(cls):
        # Reading planform data
        pf = read_blade_planform(
            os.path.join("data", "DTU_10MW_RWT_blade_axis_prebend.dat")
        )

        # Redistibution points
        dist = [
            [0, 0.01, 1],
            [0.05, 0.01, 8],
            [0.98, 0.001, 119],
            [1.0, 0.0005, 140],
        ]

        # Redistibution of planform
        pf = redistribute_planform(pf, dist=dist)

        # Initilizing lofted blade instance
        cls.d = LoftedBladeSurface()
        cls.d.pf = pf  # Adding planform data
        cls.d.redistribute_flag = True
        # d.minTE = 0.0002

        # Adding airfoil shaps
        cls.d.blend_var = [
            0.241,
            0.301,
            0.36,
            1.0,
        ]  # Blending variables (airfoil thickness ratio)
        for f in [
            os.path.join("data", "ffaw3241.dat"),
            os.path.join("data", "ffaw3301.dat"),
            os.path.join("data", "ffaw3360.dat"),
            os.path.join("data", "cylinder.dat"),
        ]:
            cls.d.base_airfoils.append(np.loadtxt(f))

        cls.d.update()

    def test_loftedblade_coordinates(self):
        """Testing blade shape from lofted blade"""

        # Loading data
        x_base, y_base, z_base = np.load(
            os.path.join("data", "lofted_blade_test_data.npy")
        ).T

        # Getting computed data
        x = self.d.domain.blocks["block-0000"].x.flatten()
        y = self.d.domain.blocks["block-0000"].y.flatten()
        z = self.d.domain.blocks["block-0000"].z.flatten()

        # # gerenate test data
        # xyz = np.array([x,y,z]).T
        # np.save("data/lofted_blade_test_data.npy", xyz)

        # Testing
        np.testing.assert_array_almost_equal(x, x_base, 5)
        np.testing.assert_array_almost_equal(y, y_base, 5)
        np.testing.assert_array_almost_equal(z, z_base, 5)

    def test_domain_write_and_read(self):
        filename = "test.xyz"

        # Writing out an xyz file
        self.d.domain.write_plot3d(filename)

        # Reading xyz file
        domain_in = read_plot3d(filename)
        # Testing domain points
        for b_name, data in self.d.domain.blocks.items():
            block_read = domain_in.blocks[b_name]
            self.assertEqual(
                np.testing.assert_almost_equal(data.x, block_read.x, 6), None
            )
            self.assertEqual(
                np.testing.assert_almost_equal(data.y, block_read.y, 6), None
            )
            self.assertEqual(
                np.testing.assert_almost_equal(data.z, block_read.z, 6), None
            )

        # Deleting xyz file
        os.remove(filename)
        os.remove(filename + ".fvbnd")


if __name__ == "__main__":
    unittest.main()
