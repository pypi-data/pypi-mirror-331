import math
import time

import numpy as np

from PGLW.main.airfoil import AirfoilShape
from PGLW.main.coons_extrusion import CoonsExtrusion
from PGLW.main.curve import Curve
from PGLW.main.domain import Block, Domain
from PGLW.main.geom_tools import calculate_rotation_matrix, dotX


class CoonsBladeRoot(object):
    """
    Generates a cylindrical root section with an angled junction

    Parameters
    ----------
    nblades: int
        Number of blades
    ds_root_start: float
        spanwise distribution at root start
    ds_root_end: float
        spanwise distribution at root end
    s_root_start: float
        spanwise position of root start
    s_root_end: float
        spanwise position of root start
    ni_root: int
        number of spanwise points
    root_diameter: float
        root diameter
    tip_con: array
        blade connector
    """

    def __init__(self, **kwargs):
        self.nblades = 3
        self.ds_root_start = 0.006
        self.ds_root_end = 0.003
        self.s_root_start = 0.0
        self.s_root_end = 0.05
        self.ni_root = 8
        self.root_diameter = 0.05
        self.tip_con = np.array([])
        self.root_con = np.array([])
        self.root_con_shape = "cylinder"
        self.root_fW0 = 0.5
        self.root_fW1 = 0.25
        self.axis = None

        self.pitch_setting = 0.0
        self.c2d_flag = False
        self.s_start_c2d = 0.0

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

        self.domain = Domain()

    def update(self):
        t0 = time.time()

        self.root_radius = self.root_diameter / 2.0

        self.ni = self.tip_con.shape[0]
        self.nblock = 4
        bsize = (self.ni - 1) // 4

        root_con = np.zeros([self.ni, 3])
        root_con[:, 2] = self.s_root_start
        if self.root_con_shape == "cylinder":
            for i in range(self.ni):
                root_con[i, 0] = -self.root_radius * math.cos(
                    360.0 * i / (self.ni - 1) * np.pi / 180.0
                )
                root_con[i, 1] = -self.root_radius * math.sin(
                    360.0 * i / (self.ni - 1) * np.pi / 180.0
                )
        elif self.root_con_shape == "naca":
            x, y = compute_naca4digit(0.4, 1.0, self.ni)
            root_con = compute_root_con(x, y, self.ni)
            root_con *= self.root_radius
        elif self.root_con_shape == "user_defined":
            root_con = compute_root_con(
                self.root_con[:, 0], self.root_con[:, 1], self.ni
            )
            root_con *= self.root_radius

        self.base_con = root_con.copy()

        if self.nblades == 3:
            self.root_angle = np.tan(-np.pi / 6.0)
            if self.root_con_shape in ["cylinder"]:
                root_con[: bsize + 1, 2] = (
                    root_con[: bsize + 1, 0] * self.root_angle
                )
                root_con[bsize : 2 * bsize + 1, 2] = (
                    -root_con[bsize : 2 * bsize + 1, 0] * self.root_angle
                )
                root_con[bsize * 2 : bsize * 3 + 1, 2] = (
                    -root_con[2 * bsize : 3 * bsize + 1, 0] * self.root_angle
                )
                root_con[bsize * 3 : bsize * 4 + 1, 2] = (
                    root_con[3 * bsize : 4 * bsize + 1, 0] * self.root_angle
                )
            elif self.root_con_shape in ["naca", "user_defined"]:
                root_con[: bsize + 1, 2] = (
                    root_con[: bsize + 1, 0] * self.root_angle
                )
                root_con[bsize : 2 * bsize + 1, 2] = (
                    root_con[bsize : 2 * bsize + 1, 0] * self.root_angle
                )
                root_con[bsize * 2 : bsize * 3 + 1, 2] = (
                    -root_con[2 * bsize : 3 * bsize + 1, 0] * self.root_angle
                )
                root_con[bsize * 3 : bsize * 4 + 1, 2] = (
                    -root_con[3 * bsize : 4 * bsize + 1, 0] * self.root_angle
                )
        elif self.nblades == 4:
            self.root_angle = np.tan(-np.pi / 4.0)
            root_con[: bsize + 1, 2] = (
                root_con[: bsize + 1, 0] * self.root_angle
            )
            root_con[bsize : 2 * bsize + 1, 2] = (
                -root_con[bsize : 2 * bsize + 1, 0] * self.root_angle
            )
            root_con[bsize * 2 : bsize * 3 + 1, 2] = (
                -root_con[2 * bsize : 3 * bsize + 1, 0] * self.root_angle
            )
            root_con[bsize * 3 : bsize * 4 + 1, 2] = (
                root_con[3 * bsize : 4 * bsize + 1, 0] * self.root_angle
            )
        self.root_con = root_con
        if self.pitch_setting != 0.0:
            tcon = Curve(points=self.tip_con)
            # tcon.rotate_z(self.pitch_setting)
            self.tip_con = tcon.points
            nroll = 0
            if self.pitch_setting <= 0.0 and self.pitch_setting > -30.0:
                nroll = 0
            elif self.pitch_setting <= -30.0 and self.pitch_setting > -60.0:
                nroll = bsize // 2
            elif self.pitch_setting <= -60.0:
                nroll = bsize
            if nroll > 0:
                rcon = root_con[:-1, :]
                rcon2 = np.zeros(root_con.shape)
                rcon2[:-1, :] = np.roll(rcon, nroll, axis=0)
                rcon2[-1, :] = rcon2[0, :]
                self.root_con = rcon2

        # create surface mesh using the CoonsBladeSection class
        self.surf = CoonsExtrusion(self.root_con, self.tip_con)
        self.surf.interpolant = "linear"
        self.surf.np = 8
        self.surf.fW0 = self.root_fW0
        self.surf.fW1 = self.root_fW1
        self.surf.ni = self.ni_root
        self.surf.ds0 = self.ds_root_start / (
            self.s_root_end - self.s_root_start
        )
        self.surf.ds1 = self.ds_root_end / (
            self.s_root_end - self.s_root_start
        )

        self.surf.create_section()
        self.surf.setZero(0, "z")
        self.surf.setZero(1, "z")
        self.surf.update_patches()
        if self.root_con_shape in ["naca", "user_defined"]:
            dom = self.surf.domain.blocks["coons"]._block2arr()[:-1, :, :, :]
            nj = dom.shape[1]
            for i in range(nj - 3):
                nr = -int(float((nj - 3) - i) / (nj - 3) * (bsize))
                dom[:, i, :, :] = np.roll(dom[:, i, :, :], nr, axis=0)
            dom2 = np.zeros(
                (dom.shape[0] + 1, dom.shape[1], dom.shape[2], dom.shape[3])
            )
            dom2[:-1, :, :, :] = dom
            dom2[-1, :, :, :] = dom[0, :, :, :]
            self.domain = Domain()
            self.domain.add_blocks(
                Block(dom2[:, :, :, 0], dom2[:, :, :, 1], dom2[:, :, :, 2])
            )
            self.domain.rename_block("block-0000", "root")
        else:
            self.domain = self.surf.domain
            self.domain.rename_block("coons", "root")

        if self.c2d_flag:
            self.compute_c2d()
        # self.domain.split_blocks(33)
        print("root done ...", time.time() - t0)

    def compute_c2d(self):
        if isinstance(self.axis, type(None)):
            axis = np.zeros((self.main_section.shape[1], 3))
            for j in range(self.main_section.shape[1]):
                for nd in range(3):
                    axis[j, nd] = np.mean(self.main_section[:, j, nd])
            self.axis = Curve(points=axis)

        # find normal of base airfoil
        normal = self.axis.dp[0]
        rot = calculate_rotation_matrix(normal)
        for name, block in self.domain.blocks.items():
            c2d = np.zeros((block.ni, block.nj, 3))
            points = (block._block2arr()).reshape(block.ni * block.nj, 3)
            points_rot = dotX(rot, points)
            c2d[:, :, 0] = points_rot[:, 2].reshape(block.ni, block.nj)
            c2d[:, :, 0] = (c2d[:, :, 0] - self.s_start_c2d) / (
                1.0 - self.s_start_c2d
            )
            self.domain.blocks[name].add_scalar(
                "c2d0", np.atleast_3d(c2d[:, :, 0])
            )
            self.domain.blocks[name].add_scalar(
                "c2d1", np.atleast_3d(c2d[:, :, 1])
            )
            self.domain.blocks[name].add_scalar(
                "c2d2", np.atleast_3d(c2d[:, :, 2])
            )
            for j in range(block.nj):
                for i in range(block.ni):
                    if c2d[i, j, 0] <= self.s_start_c2d:
                        self.domain.blocks[name].scalars["c2d2"][
                            i, j, 0
                        ] = -1.0


def compute_naca4digit(t, c, ni):
    x = np.cos(np.pi * np.linspace(0, 1, (ni - 1) // 2 + 1) / 2.0)[::-1]
    # symmetric naca with closed TE
    y = (
        5.0
        * t
        * (
            0.2969 * x**0.5
            - 0.1260 * x
            - 0.3516 * x**2
            + 0.2843 * x**3
            - 0.1036 * x**4
        )
    )
    return x, y


def compute_root_con(x, y, ni):
    ni2 = x.shape[0]
    ni0 = (x.shape[0] - 1) * 2 + 1
    surf = np.zeros((ni0, 3))
    surf[:ni2, 0] = x[::-1]
    surf[:ni2, 1] = -y[::-1]
    surf[ni2:, 0] = x[1:]
    surf[ni2:, 1] = y[1:]
    surf[0, :] = np.array([1, 0, 0])
    surf[-1, :] = np.array([1, 0, 0])
    af = AirfoilShape(points=surf)
    af.open_trailing_edge(0.08)
    # super(AirfoilShape, af).redistribute(ni, s=np.linspace(0,1,247)
    # construct rounded TE
    af.sLE = 0.5
    af.redistribute(ni, dLE=1.0 / ni, close_te=11)
    ni2 = (af.points.shape[0] - 1) // 2 + 1
    fac = 0.4
    for s in range(50):
        for i in range(20):
            af.points[i + 1, :] = (1.0 - fac) * af.points[i + 1, :] + fac * (
                af.points[i + 2, :] + af.points[i, :]
            ) * 0.5
            af.points[-i - 2, :] = (1.0 - fac) * af.points[-i - 2, :] + fac * (
                af.points[-i - 3, :] + af.points[-i - 1, :]
            ) * 0.5

    af.points[ni2 - 1, :] = np.zeros(3)
    af.points[ni2:, 0] = af.points[: ni2 - 1, 0][::-1]
    af.points[ni2:, 1] = -af.points[: ni2 - 1, 1][::-1]
    af.rotate_z(90.0)
    af.points[:, 0] *= -1.0
    af.translate_y(-0.35)
    return af.points
