import os
from importlib import resources
import unittest
import numpy as np
from PGLW.main.windio import WindIOReader
from PGLW.main.loftedblade import LoftedBladeSurface


class WindIOLoftedBladeTests(unittest.TestCase):
    def test_loftedblade(self):

        data_path = os.path.join(resources.files("PGLW"), "test", "data")
        r = WindIOReader(os.path.join(data_path, "IEA-22-280-RWT_v1.0.1.yaml"))

        geom_data = r.read_windio()

        d = LoftedBladeSurface()
        d.pf = geom_data["pf"]
        d.redistribute_flag = True
        d.blend_var = geom_data["base_airfoils"]["rthick"]
        d.base_airfoils = geom_data["base_airfoils"]["coords"]
        d.update()

        np.testing.assert_almost_equal(
            d.surface[:, :, 0].sum(), -131.81754125854042
        )
        np.testing.assert_almost_equal(
            d.surface[:, :, 1].sum(), -273.3835409291333
        )
        np.testing.assert_almost_equal(
            d.surface[:, :, 2].sum(), 13234.067036222721
        )

        return d

    def test_loftedblade_with_grids(self):

        data_path = os.path.join(resources.files("PGLW"), "test", "data")
        r = WindIOReader(os.path.join(data_path, "IEA-22-280-RWT_v1.0.1.yaml"))

        geom_data = r.read_windio(
            grid=np.linspace(0, 1, 40), grid_chord=np.linspace(0, 1, 100)
        )

        d = LoftedBladeSurface()
        d.pf = geom_data["pf"]
        d.redistribute_flag = True
        d.blend_var = geom_data["base_airfoils"]["rthick"]
        d.base_airfoils = geom_data["base_airfoils"]["coords"]
        d.update()

        np.testing.assert_almost_equal(
            d.surface[:, :, 0].sum(), -53.23908459287562
        )
        np.testing.assert_almost_equal(
            d.surface[:, :, 1].sum(), -105.4209878845965
        )
        np.testing.assert_almost_equal(
            d.surface[:, :, 2].sum(), 5139.94337066421
        )

        return d


if __name__ == "__main__":

    unittest.main()
    # test = WindIOLoftedBladeTests()
    # d = test.test_loftedblade()
