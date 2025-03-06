from builtins import range

import numpy as np

from PGLW.main.bladeroot import CoonsBladeRoot
from PGLW.main.curve import Curve


def test_bladeroot():
    # this curve will genererally be extracted from the main blade section surface
    # but in this example we generate it manually

    root_radius = 0.03
    ni = 257
    tip_con = np.zeros([ni, 3])
    tip_con[:, 2] = 0.05
    for i in range(257):
        tip_con[i, 0] = -root_radius * np.cos(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )
        tip_con[i, 1] = -root_radius * np.sin(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )

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

    total = 0.0
    for name, data in list(root.domain.blocks.items()):
        for co in ["x", "y", "z"]:
            total += np.sum(np.abs(getattr(data, co)))

    np.testing.assert_almost_equal(total, 144.70831713718627, decimal=6)


def test_bladeroot_pitch20():
    # this curve will genererally be extracted from the main blade section surface
    # but in this example we generate it manually

    root_radius = 0.03
    ni = 257
    tip_con = np.zeros([ni, 3])
    tip_con[:, 2] = 0.05
    for i in range(257):
        tip_con[i, 0] = -root_radius * np.cos(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )
        tip_con[i, 1] = -root_radius * np.sin(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )

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
    root.pitch_setting = -20.0

    root.update()

    total = 0.0
    for name, data in list(root.domain.blocks.items()):
        for co in ["x", "y", "z"]:
            total += np.sum(np.abs(getattr(data, co)))

    np.testing.assert_almost_equal(total, 144.70831713718627, decimal=6)


def test_bladeroot_pitch50():
    # this curve will genererally be extracted from the main blade section surface
    # but in this example we generate it manually

    root_radius = 0.03
    ni = 257
    tip_con = np.zeros([ni, 3])
    tip_con[:, 2] = 0.05
    for i in range(257):
        tip_con[i, 0] = -root_radius * np.cos(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )
        tip_con[i, 1] = -root_radius * np.sin(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )

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
    root.pitch_setting = -50.0

    root.update()

    total = 0.0
    for name, data in list(root.domain.blocks.items()):
        for co in ["x", "y", "z"]:
            total += np.sum(np.abs(getattr(data, co)))

    np.testing.assert_almost_equal(total, 141.69920527474363, decimal=6)


def test_bladeroot_pitch90():
    # this curve will genererally be extracted from the main blade section surface
    # but in this example we generate it manually

    root_radius = 0.03
    ni = 257
    tip_con = np.zeros([ni, 3])
    tip_con[:, 2] = 0.05
    for i in range(257):
        tip_con[i, 0] = -root_radius * np.cos(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )
        tip_con[i, 1] = -root_radius * np.sin(
            360.0 * i / (ni - 1) * np.pi / 180.0
        )

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
    root.pitch_setting = -90.0

    root.update()

    total = 0.0
    for name, data in list(root.domain.blocks.items()):
        for co in ["x", "y", "z"]:
            total += np.sum(np.abs(getattr(data, co)))

    np.testing.assert_almost_equal(total, 133.77666080566067, decimal=6)
