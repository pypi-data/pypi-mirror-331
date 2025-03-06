import unittest

import numpy as np

from PGLW.main.blademesher import BladeMesher


def setup_mesher():
    m = BladeMesher()

    # path to the planform
    m.planform_filename = "data/DTU_10MW_RWT_blade_axis_prebend.dat"

    # spanwise and chordwise number of vertices
    m.ni_span = 129
    m.ni_chord = 257

    # redistribute points chordwise
    m.redistribute_flag = True
    # number of points on blunt TE
    m.chord_nte = 9

    # airfoil family - can also be supplied directly as arrays
    m.blend_var = [0.241, 0.301, 0.36, 0.48, 1.0]
    m.base_airfoils_path = [
        "data/ffaw3241.dat",
        "data/ffaw3301.dat",
        "data/ffaw3360.dat",
        "data/ffaw3480.dat",
        "data/cylinder.dat",
    ]

    # number of vertices and cell sizes in root region
    m.root_type = "cylinder"
    m.ni_root = 8
    m.s_root_start = 0.0
    m.s_root_end = 0.05
    m.ds_root_start = 0.008
    m.ds_root_end = 0.005

    # inputs to the tip component
    # note that most of these don't need to be changed
    m.ni_tip = 11
    m.s_tip_start = 0.99
    m.s_tip = 0.995
    m.ds_tip_start = 0.001
    m.ds_tip = 0.00005

    m.tip_fLE1 = 0.5  # Leading edge connector control in spanwise direction.
    m.tip_fLE2 = 0.5  # Leading edge connector control in chordwise direction.
    m.tip_fTE1 = 0.5  # Trailing edge connector control in spanwise direction.
    m.tip_fTE2 = 0.5  # Trailing edge connector control in chordwise direction.
    m.tip_fM1 = 1.0  # Control of connector from mid-surface to tip.
    m.tip_fM2 = 1.0  # Control of connector from mid-surface to tip.
    m.tip_fM3 = 0.2  # Controls thickness of tip.

    m.tip_dist_cLE = 0.0001  # Cell size at tip leading edge starting point.
    m.tip_dist_cTE = 0.0001  # Cell size at tip trailing edge starting point.
    m.tip_dist_tip = 0.00025  # Cell size of LE and TE connectors at tip.
    m.tip_dist_mid0 = 0.00025  # Cell size of mid chord connector start.
    m.tip_dist_mid1 = 0.00004  # Cell size of mid chord connector at tip.

    m.tip_c0_angle = 40.0  # Angle of connector from mid chord to LE/TE

    m.tip_nj_LE = 20  # Index along mid-airfoil connector used as starting point for tip connector

    # generate the mesh
    m.update()

    # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
    m.domain.rotate_x(-90)
    m.domain.rotate_y(180)

    # copy blade 1 to blade 2 and 3 and rotate
    m.domain.add_group("blade1", list(m.domain.blocks.keys()))
    m.domain.rotate_z(-120, groups=["blade1"], copy=True)
    m.domain.rotate_z(120, groups=["blade1"], copy=True)

    m = BladeMesher()

    # path to the planform
    m.planform_filename = "data/DTU_10MW_RWT_blade_axis_prebend.dat"

    # spanwise and chordwise number of vertices
    m.ni_span = 129
    m.ni_chord = 257

    # redistribute points chordwise
    m.redistribute_flag = True
    # number of points on blunt TE
    m.chord_nte = 9

    # airfoil family - can also be supplied directly as arrays
    m.blend_var = [0.241, 0.301, 0.36, 0.48, 1.0]
    m.base_airfoils_path = [
        "data/ffaw3241.dat",
        "data/ffaw3301.dat",
        "data/ffaw3360.dat",
        "data/ffaw3480.dat",
        "data/cylinder.dat",
    ]

    # number of vertices and cell sizes in root region
    m.root_type = "cylinder"
    m.ni_root = 8
    m.s_root_start = 0.0
    m.s_root_end = 0.05
    m.ds_root_start = 0.008
    m.ds_root_end = 0.005

    # inputs to the tip component
    # note that most of these don't need to be changed
    m.ni_tip = 11
    m.s_tip_start = 0.99
    m.s_tip = 0.995
    m.ds_tip_start = 0.001
    m.ds_tip = 0.00005

    m.tip_fLE1 = 0.5  # Leading edge connector control in spanwise direction.
    m.tip_fLE2 = 0.5  # Leading edge connector control in chordwise direction.
    m.tip_fTE1 = 0.5  # Trailing edge connector control in spanwise direction.
    m.tip_fTE2 = 0.5  # Trailing edge connector control in chordwise direction.
    m.tip_fM1 = 1.0  # Control of connector from mid-surface to tip.
    m.tip_fM2 = 1.0  # Control of connector from mid-surface to tip.
    m.tip_fM3 = 0.2  # Controls thickness of tip.

    m.tip_dist_cLE = 0.0001  # Cell size at tip leading edge starting point.
    m.tip_dist_cTE = 0.0001  # Cell size at tip trailing edge starting point.
    m.tip_dist_tip = 0.00025  # Cell size of LE and TE connectors at tip.
    m.tip_dist_mid0 = 0.00025  # Cell size of mid chord connector start.
    m.tip_dist_mid1 = 0.00004  # Cell size of mid chord connector at tip.

    m.tip_c0_angle = 40.0  # Angle of connector from mid chord to LE/TE

    m.tip_nj_LE = 20  # Index along mid-airfoil connector used as starting point for tip connector

    # generate the mesh
    m.update()

    # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
    m.domain.rotate_x(-90)
    m.domain.rotate_y(180)

    # copy blade 1 to blade 2 and 3 and rotate
    m.domain.add_group("blade1", list(m.domain.blocks.keys()))
    m.domain.rotate_z(-120, groups=["blade1"], copy=True)
    m.domain.rotate_z(120, groups=["blade1"], copy=True)

    return m


class BladeMesherTest(unittest.TestCase):
    # Only meshing a rotor once once if muliple tests are made (opposed to setUp which is run before every test)
    @classmethod
    def setUpClass(cls):
        # Assigning as a class variable
        cls.m = setup_mesher()

    def test_blade1(self):
        total = 0.0
        for name, data in list(self.m.domain.blocks.items()):
            if not ("copy" in name):
                for co in ["x", "y", "z"]:
                    total += np.sum(np.abs(getattr(data, co)))

        self.assertAlmostEqual(total, 25994.131835870718, 5)

    def test_blade2(self):
        total = 0.0
        for name, data in list(self.m.domain.blocks.items()):
            if ("copy" in name) and not ("copy-0001" in name):
                for co in ["x", "y", "z"]:
                    total += np.sum(np.abs(getattr(data, co)))

        self.assertAlmostEqual(total, 34549.70322712848, 5)

    def test_blade3(self):
        total = 0.0
        for name, data in list(self.m.domain.blocks.items()):
            if "copy-0001" in name:
                for co in ["x", "y", "z"]:
                    total += np.sum(np.abs(getattr(data, co)))

        self.assertAlmostEqual(total, 34453.45726446717, 5)

    def test_pitch_20(self):
        m = self.m

        m.pitch_setting = m.root.pitch_setting = -20.0

        # generate the mesh
        m.update()

        # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
        m.domain.rotate_x(-90)
        m.domain.rotate_y(180)

        # copy blade 1 to blade 2 and 3 and rotate
        m.domain.add_group("blade1", m.domain.blocks.keys())
        m.domain.rotate_z(-120, groups=["blade1"], copy=True)
        m.domain.rotate_z(120, groups=["blade1"], copy=True)

        total = 0.0
        for name, data in list(m.domain.blocks.items()):
            if "main_section" in name:
                for co in ["x", "y", "z"]:
                    total += np.sum(np.abs(getattr(data, co)))

        self.assertAlmostEqual(total, 78304.97682715146, 5)

    def test_pitch_50(self):
        m = self.m

        m.pitch_setting = m.root.pitch_setting = -50.0

        # generate the mesh
        m.update()

        # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
        m.domain.rotate_x(-90)
        m.domain.rotate_y(180)

        # copy blade 1 to blade 2 and 3 and rotate
        m.domain.add_group("blade1", m.domain.blocks.keys())
        m.domain.rotate_z(-120, groups=["blade1"], copy=True)
        m.domain.rotate_z(120, groups=["blade1"], copy=True)

        total = 0.0
        for name, data in list(m.domain.blocks.items()):
            if "main_section" in name:
                for co in ["x", "y", "z"]:
                    total += np.sum(np.abs(getattr(data, co)))

        self.assertAlmostEqual(total, 78163.32820652444, 5)

    def test_pitch_90(self):
        m = self.m

        m.pitch_setting = m.root.pitch_setting = -90.0

        # generate the mesh
        m.update()

        # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
        m.domain.rotate_x(-90)
        m.domain.rotate_y(180)

        # copy blade 1 to blade 2 and 3 and rotate
        m.domain.add_group("blade1", m.domain.blocks.keys())
        m.domain.rotate_z(-120, groups=["blade1"], copy=True)
        m.domain.rotate_z(120, groups=["blade1"], copy=True)

        total = 0.0
        for name, data in list(m.domain.blocks.items()):
            if "main_section" in name:
                for co in ["x", "y", "z"]:
                    total += np.sum(np.abs(getattr(data, co)))

        self.assertAlmostEqual(total, 77840.77587112828, 5)


if __name__ == "__main__":
    unittest.main()

    # m = setup_mesher()
    # m.pitch_setting = -90.
    #
    # # generate the mesh
    # m.update()
    #
    # # rotate domain with flow direction in the z+ direction and blade1 in y+ direction
    # m.domain.rotate_x(-90)
    # m.domain.rotate_y(180)
    #
    # # copy blade 1 to blade 2 and 3 and rotate
    # m.domain.add_group('blade1', m.domain.blocks.keys())
    # m.domain.rotate_z(-120, groups=['blade1'], copy=True)
    # m.domain.rotate_z(120, groups=['blade1'], copy=True)
