import numpy as np

from PGLW.main.bezier import BezierCurve
from PGLW.main.coons import CoonsPatch
from PGLW.main.curve import Curve, Line
from PGLW.main.domain import Domain
from PGLW.main.geom_tools import calculate_rotation_matrix, dotX


class RootCap(object):
    """

    parameters
    ----------
    ni_root: int
        number of vertices in spanwise direction on fillet
    Fcap: float
        size of four block patch as a fraction of the root
        diameter, range 0 < Fcap < 1.
    Fblend: float
        factor controlling shape of four block patch.

        | Fblend => 0. takes the shape of tip_con,
        | Fblend => 1. takes the shape of a rectangle.
    direction: float
        Blade direction along z-axis: 1 positive z, -1 negative z
    """

    def __init__(self, **kwargs):
        self.Proot = np.array([])
        self.cap_radius = 0.001
        self.Fcap = 0.95
        self.Fblend = 0.5
        self.ni_root = 8
        self.direction = 1.0
        self.tip_con = np.array([])
        self.s_root_start = 0.0
        self.s_root_end = 0.005
        self.ds_root_start = 0.0005
        self.ds_root_end = 0.001

        self.c2d_flag = False
        self.s_start_c2d = 0.0

        for (
            k,
            w,
        ) in kwargs.items():
            if k.startswith("cap_"):
                name = k[4:]
            else:
                name = k
            if hasattr(self, name):
                setattr(self, name, w)

        self.domain = Domain()

    def update(self):
        self.bsize = (self.tip_con.shape[0] - 1) // 4 + 1

        x = self.tip_con
        xt = np.zeros(x.shape)
        shift = (self.bsize - 1) // 2
        xt[:-shift] = x[shift:].copy()
        xt[-(shift + 1) :] = x[: (shift + 1)].copy()
        self.ni = x.shape[0]
        c = Curve(points=xt)
        self.base_cons = c.divide_connector(self.bsize)
        self.root_cons = []
        pcen = np.array(
            [
                np.mean(self.tip_con[:, 0]),
                np.mean(self.tip_con[:, 1]),
                np.mean(self.tip_con[:, 2]) - self.cap_radius * self.direction,
            ]
        )

        self.collar_ps = []
        for i in range(4):
            p0 = x[shift + i * (self.bsize - 1), :]
            p1 = p0.copy()
            p1[2] -= pcen[2]
            p2 = self.Fcap * p1 + (1.0 - self.Fcap) * pcen
            p2[2] = p1[2]
            b = BezierCurve()
            b.add_control_point(p0)
            b.add_control_point(p1)
            b.add_control_point(p2)
            b.ni = self.ni_root
            b.update()
            b.redistribute(
                ni=self.ni_root,
                dist=[
                    [0.0, self.ds_root_end / b.smax, 1],
                    [1.0, self.ds_root_start / b.smax, self.ni_root],
                ],
            )
            self.collar_ps.append(b.copy())
        self.collar_ps.append(self.collar_ps[0].copy())
        # create patch connectors

        self.patch_cons = []
        tcons = []
        for i in range(4):
            p0 = self.collar_ps[i].points[-1]
            p1 = self.collar_ps[i + 1].points[-1]
            l1 = Line(p0, p1, ni=self.bsize)
            tcons.append(l1.copy())
        for i in range(4):
            c = self.base_cons[i].copy()
            c.points[:, 2] -= pcen[2]
            c.points[:, :2] = (
                self.Fcap * c.points[:, :2] + (1.0 - self.Fcap) * pcen[:2]
            )
            c.points[:, :2] = (
                self.Fblend * c.points[:, :2]
                + (1.0 - self.Fblend) * tcons[i].points[:, :2]
            )
            c.initialize(c.points)
            self.patch_cons.append(c.copy())

        self.base_cons[2].points = self.base_cons[2].points[::-1].copy()
        self.base_cons[2].initialize(self.base_cons[2].points)
        self.base_cons[3].points = self.base_cons[3].points[::-1].copy()
        self.base_cons[3].initialize(self.base_cons[3].points)

        self.patch_cons[2].points = self.patch_cons[2].points[::-1].copy()
        self.patch_cons[2].initialize(self.patch_cons[2].points)
        self.patch_cons[3].points = self.patch_cons[3].points[::-1].copy()
        self.patch_cons[3].initialize(self.patch_cons[3].points)

        self.domain = Domain()

        p = CoonsPatch(
            edge0=self.patch_cons[0].copy(),
            edge1=(self.patch_cons[2].copy()),
            edge2=(self.patch_cons[3].copy()),
            edge3=(self.patch_cons[1].copy()),
            name="cap_base-0000",
        )
        self.patches = []
        self.patches.append(p)
        p._flip_block()
        self.domain.add_blocks(p.split((self.bsize - 1) // 2 + 1))
        for i in [0, 1]:
            p = CoonsPatch(
                edge0=(self.collar_ps[i].copy()),
                edge1=(self.collar_ps[i + 1].copy()),
                edge2=(self.base_cons[i].copy()),
                edge3=(self.patch_cons[i].copy()),
                name="cap-%04d" % i,
            )
            p._flip_block()
            self.patches.append(p)
            self.domain.add_blocks(p)
        for i in [2, 3]:
            p = CoonsPatch(
                edge0=self.collar_ps[i + 1],
                edge1=self.collar_ps[i],
                edge2=self.base_cons[i],
                edge3=self.patch_cons[i],
                name="cap-%04d" % i,
            )
            self.patches.append(p)
            self.domain.add_blocks(p)
        if self.direction == -1:
            self.domain.flip_all()
        self.domain.join_blocks("cap-0000", "cap-0001", newname="root")
        self.domain.join_blocks("root", "cap-0002", newname="root")
        self.domain.join_blocks("root", "cap-0003", newname="root")
        bs = self.domain.blocks["root"].isplits((self.bsize - 1) // 2 + 1)
        del self.domain.blocks["root"]
        self.domain.add_blocks(bs)
        for i in [7, 6, 5, 4, 3, 2, 1]:
            self.domain.join_blocks("root", "root-%04d" % i, newname="root")

        if self.c2d_flag:
            self.compute_c2d()

    def compute_c2d(self):
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
            # c2d[:, :, 2] = -1.
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
