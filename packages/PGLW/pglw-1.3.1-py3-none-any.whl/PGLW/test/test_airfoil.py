import unittest

import numpy as np

from PGLW.main.airfoil import AirfoilShape


class AirfoilShapeTests(unittest.TestCase):
    """Tests for components.airfoil.py"""

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.af = AirfoilShape()
        self.af.initialize(points=np.loadtxt("data/cylinder.dat"))
        # self.af.initialize(points=np.loadtxt('data/ffaw3480.dat'))
        self.dps_s01 = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

    def test_s_to_11_10(self):
        dps_s11 = np.array([self.af.s_to_11(s) for s in self.dps_s01])
        dps_s01n = np.array([self.af.s_to_01(s) for s in dps_s11])

        self.assertEqual(
            np.testing.assert_allclose(dps_s01n, self.dps_s01, 1e-06), None
        )

    def test_s_to_11_10_rotate(self):
        afi = self.af.copy()
        afi.rotate_z(-45.0)
        dps_s11 = np.array([afi.s_to_11(s) for s in self.dps_s01])
        afii = self.af.copy()
        afii.rotate_z(+45.0)
        dps_s01n = np.array([afii.s_to_01(s) for s in dps_s11])

        self.assertEqual(
            np.testing.assert_allclose(dps_s01n, self.dps_s01, 1e-06), None
        )

    def test_s_to_11_10_scale_equal(self):
        afi = self.af.copy()
        afi.scale(1.5)
        points = afi.points
        dps_s11 = np.array([afi.s_to_11(s) for s in self.dps_s01])
        afii = self.af.copy()
        afii.scale(1.5)
        pointsn = afii.points
        dps_s01n = np.array([afii.s_to_01(s) for s in dps_s11])

        self.assertEqual(
            np.testing.assert_allclose(dps_s01n, self.dps_s01, 1e-06), None
        )
        self.assertEqual(
            np.testing.assert_allclose(pointsn, points, 1e-06), None
        )

    def test_s_to_11_10_scale_not_equal(self):
        afi = self.af.copy()
        afi.scale(1.1)
        # points = afi.points
        dps_s11 = np.array([afi.s_to_11(s) for s in self.dps_s01])
        afii = self.af.copy()
        afii.scale(1.5)
        # pointsn = afii.points
        dps_s01n = np.array([afii.s_to_01(s) for s in dps_s11])

        self.assertEqual(
            np.testing.assert_allclose(dps_s01n, self.dps_s01, 1e-06), None
        )
        # self.assertEqual(np.testing.assert_allclose(pointsn, points, 1E-06), None)


class AirfoilShapeTests2(unittest.TestCase):
    """Tests for components.airfoil.py"""

    def test_redistribute_linear(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        ds = np.array(
            [
                0.11712651,
                0.117116,
                0.11720435,
                0.11725923,
                0.11719773,
                0.11713939,
                0.11709662,
                0.11696592,
                0.11212361,
                0.02098937,
                0.02108704,
                0.02109582,
                0.02110256,
                0.0211067,
                0.02110718,
                0.02110731,
                0.02110809,
                0.02110783,
                0.02110793,
                0.08436049,
                0.08439066,
                0.08441201,
                0.0844209,
                0.08442478,
                0.08442662,
                0.08442745,
                0.08442748,
                0.08442729,
                0.08442751,
            ]
        )
        af.redistribute(
            ni=30,
            dist=[
                [0, 0.01, 1],
                [0.5, 0.01, 10],
                [0.6, 0.01, 20],
                [1, 0.01, 30],
            ],
            linear=True,
        )
        self.assertEqual(np.testing.assert_allclose(af.ds, ds, 1e-06), None)

    def test_redistribute_distfunc(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        ds = np.array(
            [
                0.03187173,
                0.0662534,
                0.1239282,
                0.19230617,
                0.22543051,
                0.19175545,
                0.1237126,
                0.06599569,
                0.03104575,
                0.02098937,
                0.02108704,
                0.02109582,
                0.02110256,
                0.0211067,
                0.02110718,
                0.02110731,
                0.02110809,
                0.02110783,
                0.02110793,
                0.02879817,
                0.05032088,
                0.0816139,
                0.1176486,
                0.1436471,
                0.1436658,
                0.11769158,
                0.0816484,
                0.05033041,
                0.02879825,
            ]
        )
        af.redistribute(
            ni=30,
            dist=[
                [0, 0.01, 1],
                [0.5, 0.01, 10],
                [0.6, 0.01, 20],
                [1, 0.01, 30],
            ],
        )
        self.assertEqual(np.testing.assert_allclose(af.ds, ds, 1e-06), None)

    def test_redistribute_closete(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=0)
        self.assertAlmostEqual(
            np.linalg.norm(af.points[0] - af.points[-1]), 0.00751, places=5
        )

        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=7)
        self.assertAlmostEqual(
            np.linalg.norm(af.points[0] - af.points[-1]), 0.0, places=10
        )
        self.assertEqual(af.te_seg.points.shape[0], 7)

        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=True)
        self.assertAlmostEqual(
            np.linalg.norm(af.points[0] - af.points[-1]), 0.0, places=10
        )
        self.assertEqual(af.te_seg.points.shape[0], 5)

        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=True, dTE="dTE")
        self.assertAlmostEqual(np.sum(af.s), 64.18207164749155, places=5)
        self.assertAlmostEqual(
            np.linalg.norm(af.points[0] - af.points[-1]), 0.0, places=10
        )
        self.assertEqual(af.te_seg.points.shape[0], 5)

        # test whether PGL catches that cannot close this one and does not use dTE
        af = AirfoilShape(points=np.loadtxt("data/FFA-W3-211.dat"))
        af.redistribute(128, close_te=True, dTE="dTE")
        self.assertAlmostEqual(np.sum(af.s), 63.86139334861197, places=5)

    def test_open_te(self):
        af = AirfoilShape(points=np.loadtxt("data/FFA-W3-211.dat"))
        af.redistribute(128)
        af.open_trailing_edge(0.01)
        self.assertAlmostEqual(
            np.linalg.norm(af.points[0] - af.points[-1]), 0.01, places=10
        )

    def test_interp_x(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        s = af.interp_x(0.3, "upper")
        self.assertAlmostEqual(s, 0.662865208113911, places=5)
        ps = np.loadtxt("data/ffaw3241.dat")
        ps[:, 0] *= -1.0
        af = AirfoilShape(points=ps)
        s = af.interp_x(0.3, "upper")
        self.assertAlmostEqual(s, 0.49896127212155866, places=5)

    def test_flap(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af = af.flap(0.2, 0.05, 0.5, 20.0)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 1.4383385915722116, places=5)

    def test_gurney(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af = af.gurneyflap(0.03, 3.0)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 0.6714187425159088, places=5)

    def test_wavy(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=True, dTE="dTE")
        af.wavy(-100e-3, 100e-3, 40e-3, 0.5e-3, 20e-3, 128)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 1.035372735973529, places=5)

    def test_bite(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=True, dTE="dTE")
        af.bite(-20e-3)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 0.7488518697269764, places=5)
        af.bite(20e-3)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 0.676753790993307, places=5)

    def test_step(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=True, dTE="dTE")
        af.step(-100e-3, 100e-3, 1e-3, 0.1e-3 / 3, 128)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 0.999636061492069, places=5)

    def test_moveLE(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.moveLE(0.15, 15e-3)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 1.4250613036049513, places=5)

    def test_flatsanding(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=True, dTE="dTE")
        af.flatsanding(-10e-3, 25e-3, 128)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 0.18943645035430734, places=5)

    def test_rough_paras(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.rough_paras(100e-3, 1e-3)
        box_ref = [-0.050019, 0.065305, -0.165623, 0.175329]
        self.assertEqual(
            np.testing.assert_allclose(af.box, box_ref, 1e-05), None
        )

    def test_roughpatch_paras(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.roughpatch_paras(10e-3, 100e-3, 1e-3)
        box_ref = [0.00099846, 0.06610987, 0.00825168, 0.07490293]
        self.assertEqual(
            np.testing.assert_allclose(af.box_up, box_ref, 1e-06), None
        )

    def test_smoothbite(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.smoothbite(20e-3)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 0.78513469547716544, places=5)

    def test_slot(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.slot(-20e-3, 5e-3, 2e-3, 0.1e-3 / 3, 128)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, -1.5796790341265674, places=5)

    def test_smoothslot_start(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.smoothslot_start(-20e-3, 20e-3, 2e-3, 0.1e-3 / 3, 128)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, -2.9213948655449893, places=5)

    def test_smoothslot_end(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.smoothslot_end(-20e-3, 20e-3, 2e-3, 0.1e-3 / 3, 128)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, -1.8249702427129906, places=5)

    def test_stallstrip(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.stallstrip(0.0, 3e-3, 128, 0.1e-3 / 5, 90.0)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 1.136926483440404, places=5)

    def test_erosion(self):
        af = AirfoilShape(points=np.loadtxt("data/ffaw3241.dat"))
        af.redistribute(128, close_te=3, dTE="dTE")
        af.spectralLER(-40e-4, 35e-3, step=True, Lx_in=203.7447e-3 / 500.0)
        s = np.sum(af.points[:, 1])
        self.assertAlmostEqual(s, 3.2198557760060305, places=5)


if __name__ == "__main__":
    unittest.main()
