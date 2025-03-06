import numpy as np

from PGLW.main.bezier import BezierCurve
from PGLW.main.coons import CoonsPatch
from PGLW.main.curve import Curve, Line, SegmentedCurve
from PGLW.main.domain import Domain
from PGLW.main.pglcomponent import PGLComponent


class VGUnit(PGLComponent):
    """

    Parameters
    ----------
    len: float
        vortex generator length
    h: float
        vortex generator height
    w: float
        vortex generator vane width
    delta1: float
        VG unit inter spacing
    delta2: float
        VG unit intra spacing
    l_base: float
        length of base plate relative to VG length
    base_offset: float
        chordwise offset of base relative to VG where base_offset = 0
        will result in the VG being centered on the base.
        offset is normalized with base plate length.
    bsize: int
        number of vertices in the i and j directions of each block (usually 65)
    ni_base: int
        number of points on VG base fairing
    ni_cap: int
        number of points on aft part of VG LE
    ni_edge: int
        number of points on VG edge
    ni_mid: int
        number of points on the bottom part of the VG. Number of points on the
        base will therefore be bsize - ni_mid.
    fLE0: float
        controls gradient of connector from VG LE to VG base corner at VG LE
    fLE1: float
        controls gradient of connector from VG LE to VG base corner at base corner
    fTE0: float
        controls gradient of connector from VG TE to VG base corner at VG TE
    fTE1: float
        controls gradient of connector from VG TE to VG base corner at base corner
    fLEcap: float
        fraction of LE length of position of cap connector end point on the LE.
    CPb0: float
        controls horizontal position of connector on VG sides
    wCap: float
        controls vertical position of connector on VG sides
    """

    def __init__(self, **kwargs):
        self.len = 0.02
        self.h = 0.005
        self.w = 0.00015
        self.beta = 15.0

        self.delta1 = 0.02
        self.delta2 = 0.02
        self.l_base = 2.0
        self.base_offset = 0.0
        self.dr_base = 0.04

        self.bsize = 65
        self.ni_edge = 6
        self.ni_base = 5
        self.ni_cap = 50
        self.ni_mid = 20

        # distribution CPs
        self.fLEcap = 0.6
        self.fLE0 = 0.2
        self.fLE1 = 0.1
        self.fTE0 = 0.4
        self.fTE1 = 0.4
        self.CPb0 = 0.3
        self.CPLE0 = 0.3
        self.wCap = 0.4

        # self.s1_base = 0.6
        # self.LEoffset = 0.
        # self.LEpos = np.array([])
        # self.ds_LE = 0.001
        # self.ds_TE = 0.
        # self.s1_TE = 0.6

        # self.ds_TE = 0.
        # self.s1_TE = 0.6
        # self.ni_TE = 40
        # self.ds_TEbase = 0.001

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

    def update(self):
        self.segments = []
        self.patches = {}
        self.connectors = {}
        self.domain = Domain()

        # base plate width
        self.pwidth = (self.delta1 + self.delta2) / 2.0

        self.draw_vg()

    def draw_vg(self):
        """create the normalized VG shape"""

        lnorm = self.len / self.h
        wnorm = self.w / self.h

        # trailing edge with unit height with fairing
        pBaseL = np.array([lnorm + self.dr_base, 0, 0])
        pBaseM = np.array([lnorm, 0, 0])
        pBaseU = np.array([lnorm, self.dr_base, 0])
        pTip = np.array([lnorm, 1.0, 0])
        pLE = np.zeros(3)
        c = BezierCurve()
        c.add_control_point(pBaseL)
        c.add_control_point(pBaseM)
        c.add_control_point(pBaseU)
        c.ni = self.ni_base
        c.update()
        self.add_connector("TEbase", c)

        self.ni_TE = (self.ni_mid - 1) + (self.bsize - self.ni_cap) + 1
        l0 = Line(pBaseU, pTip, self.ni_TE)
        l0.redistribute(
            dist=[[0.0, 0.02 / l0.smax, 1], [1.0, 0.02 / l0.smax, self.ni_TE]]
        )
        # l.points[:,0] += lnorm
        self.add_connector("TE", l0)

        TEc = Curve(points=self.TE.points.copy())
        TEc.points[:, 2] += wnorm / 2.0
        self.add_connector("TEc", TEc)
        TEbasec = Curve(points=self.TEbase.points.copy())
        TEbasec.rotate_y(-45.0, center=self.TE.points[-1])
        TEbasec.translate_z(wnorm / 2.0)
        TEbasec.redistribute(ni=self.ni_base)
        self.add_connector("TEbasec", TEbasec)

        TEbaseL = BezierCurve()
        p0 = self.TEbasec.points[0]
        p2 = self.TEbase.points[0]
        p1 = p0.copy()
        p1[0] = p2[0]
        TEbaseL.add_control_point(p0)
        TEbaseL.add_control_point(p1)
        TEbaseL.add_control_point(p2)
        TEbaseL.ni = self.ni_edge
        TEbaseL.update()
        TEbaseL.redistribute(ni=self.ni_edge)
        # TEbaseL.dist =[[0, 0.05, 1],[1., -1, self.ni_edge]]
        self.add_connector("TEbaseL", TEbaseL)
        TEbaseU = Line(
            self.TEbasec.points[-1], self.TEbase.points[-1], self.ni_edge
        )
        self.add_connector("TEbaseU", TEbaseU)
        p = CoonsPatch(
            edge0=self.TEbaseL,
            edge1=self.TEbaseU,
            edge3=self.TEbase,
            edge2=self.TEbasec,
        )
        self.TEbaseP = p
        self.patches["TEbaseP"] = self.TEbaseP
        self.domain.add_blocks(p, names=["collar0"])

        TEtopc = Line(self.TEc.points[-1], self.TE.points[-1], self.ni_edge)
        self.add_connector("TEtopc", TEtopc)

        p = CoonsPatch(
            edge0=self.TEbaseU,
            edge1=self.TEtopc,
            edge3=self.TE,
            edge2=self.TEc,
        )
        self.patches["TE"] = p
        nn = self.ni_TE - (self.bsize - self.ni_cap)
        bs = p.jsplit(nn)
        self.domain.add_blocks(bs, names=["TEl", "TEu"])

        self.ni_LE = self.ni_cap + self.ni_mid + self.ni_base - 2
        LE = Line(self.TE.points[-1], pLE, self.ni_LE)
        LE.redistribute(
            dist=[
                [0.0, 0.02 / LE.smax, 1],
                [self.fLEcap, -1, self.ni_cap],
                [1.0 - self.dr_base, 0.006, self.ni_LE - self.ni_base + 1],
                [1.0, 0.004, self.ni_LE],
            ]
        )
        c0, c1 = LE.split(1.0 - self.dr_base)
        LEt = Curve(points=c1[::-1].copy())
        LEfillet = BezierCurve()
        p0 = LEt.points[0].copy()
        p0[0] -= self.dr_base / 2
        LEfillet.add_control_point(p0)
        LEfillet.add_control_point(LEt.points[0].copy())
        LEfillet.add_control_point(LEt.points[-1].copy())
        LEfillet.ni = LEt.ni
        LEfillet.update()
        LEfillet.redistribute(s=LEt.s)
        self.add_connector("LEfillet", LEfillet)
        LE = Curve(points=c0.copy())
        self.add_connector("LE", LE)

        LEc = Curve(points=c0.copy())
        LEc.points[:, 2] += wnorm / 2.0
        LEc.initialize(LEc.points)
        self.add_connector("LEc", LEc)
        c1[:, 2] += wnorm / 2.0
        LEcc = BezierCurve()
        p0 = c1[0].copy()
        p1 = c1[2].copy()
        p2 = c1[-1].copy()
        p2[0] = c1[-2][0]
        p2[2] += self.dr_base
        LEcc.add_control_point(p2)
        LEcc.add_control_point(p1)
        LEcc.add_control_point(p0)
        LEcc.ni = self.ni_base
        LEcc.update()
        LEcc.redistribute(s=LEt.s)
        # LEcc.redistribute(s=1. - cTmp.s[::-1].copy())
        self.add_connector("LEcc", LEcc)

        c = BezierCurve()
        c.add_control_point(self.LEcc.points[0])
        p1 = np.array([LEfillet.points[0, 0], 0.0, self.LEcc.points[0, 2]])
        c.add_control_point(p1)
        c.add_control_point(self.LEfillet.points[0])
        c.ni = self.ni_edge
        c.update()
        c.redistribute(ni=self.ni_edge)
        self.add_connector("LEbottomc", c)
        LEbottom1 = Line(
            self.LEcc.points[-1], self.LEfillet.points[-1], ni=self.ni_edge
        )
        self.add_connector("LEbottom1", LEbottom1)

        p = CoonsPatch(
            edge2=self.LEbottomc,
            edge3=self.LEbottom1,
            edge0=self.LEcc,
            edge1=self.LEfillet,
            interpolant="linear",
        )
        self.patches["collar2"] = p
        self.domain.add_blocks(p, names=["collar2"])

        p = CoonsPatch(
            edge2=self.LEbottom1,
            edge3=self.TEtopc,
            edge0=self.LEc,
            edge1=self.LE,
        )
        self.patches["LE"] = p
        bs = p.isplit(self.ni_cap)
        self.domain.add_blocks(bs, names=["LEu", "LEl"])

        ni_base = (self.bsize - 1) * 3 - 2 * (self.ni_edge - 1) + 1
        p0 = self.TEbasec.points[-1]
        p1 = self.LEc.points[-1]
        baseH = Line(p0, p1, ni=ni_base)
        # baseH.dist = [[0, 0.001, 1], [1, 0.003, ni_base]]
        baseH.redistribute(
            dist=[
                [0, 0.003, 1],
                [0.45, 0.006, int(ni_base * 0.55)],
                [1, 0.005, ni_base],
            ]
        )
        self.add_connector("baseH", baseH)

        base = Line(
            self.TEbasec.points[0], self.LEcc.points[0].copy(), ni=ni_base
        )
        base.redistribute(
            dist=[
                [0, 0.003, 1],
                [0.45, 0.006, int(ni_base * 0.55)],
                [1, 0.005, ni_base],
            ]
        )
        self.add_connector("base", base)

        p = CoonsPatch(
            edge0=(self.base),
            edge1=(self.baseH),
            edge2=(self.TEbasec),
            edge3=(self.LEcc.copy()),
            interpolant="linear",
        )
        self.patches["collar1"] = p
        self.domain.add_blocks(p, names=["collar1"])

        # create helper lines to find tip patch corners
        p0 = (1.0 - self.CPb0) * self.baseH.points[
            0
        ] + self.CPb0 * self.baseH.points[-1]
        p1 = self.LEc.points[self.ni_cap]
        p2 = self.TEc.points[-(self.bsize - self.ni_cap + 1)]

        self.CP0 = self.wCap * p1 + (1 - self.wCap) * p0
        self.CP1 = self.wCap * p2 + (1 - self.wCap) * p0
        l3 = Line(self.CP1, self.CP0, ni=self.bsize)
        # self.add_connector('cap0', l3)

        nn = self.bsize - self.ni_cap + 1
        cap1 = SegmentedCurve()
        c1 = Curve(points=self.TEc.points[-nn:])
        c2 = Curve(points=self.LEc.points[: self.ni_cap])
        cap1.add_segment(c1)
        cap1.add_segment(c2)
        cap1.update()
        self.add_connector("cap1", cap1)

        cap2 = Line(
            self.CP1, self.cap1.points[0], ni=self.bsize - self.ni_edge + 1
        )
        cap3 = Line(
            self.CP0, self.cap1.points[-1], ni=self.bsize - self.ni_edge + 1
        )

        self.add_connector("cap2", cap2)
        self.add_connector("cap3", cap3)

        ni0 = (self.bsize - 1) - (self.ni_edge - 1)
        ni1 = ni0 + (self.bsize - 1)
        c0 = self.baseH.points[: ni0 + 1]
        c1 = self.baseH.points[ni0 : ni1 + 1]
        c2 = self.baseH.points[ni1:]

        # self.ni_LE1 = self.ni_LE - self.ni_cap - self.ni_base + 2

        mid0 = Curve(points=c1)
        # mid1 = self.cap0.copy()
        mid2 = Line(mid0.points[0], self.CP1, ni=self.ni_mid)
        mid3 = Line(mid0.points[-1], self.CP0, ni=self.ni_mid)
        self.add_connector("mid0", mid0)
        # self.add_connector('mid1', mid1)
        self.add_connector("mid2", mid2)
        self.add_connector("mid3", mid3)

        v0 = -self.cap3.dp[0]
        v1 = self.mid3.dp[-1]
        v3 = 0.5 * (v0 + v1)
        v3 = v3 / np.dot(v3, v3) ** 0.5
        p0 = self.cap3.points[0].copy()
        vlen = self.CP1 - self.CP0
        vlen = np.dot(vlen, vlen) ** 0.5
        p1 = p0 + 0.4 * vlen * v3
        CP0h = p1.copy()
        test_norm = Line(p0, p1, 33)
        self.add_connector("test_norm0", test_norm)

        v0 = -self.cap2.dp[0]
        v1 = self.mid2.dp[-1]
        v3 = 0.5 * (v0 + v1)
        v3 = v3 / np.dot(v3, v3) ** 0.5
        p0 = self.cap2.points[0].copy()
        p1 = p0 + 0.4 * vlen * v3
        CP1h = p1.copy()
        test_norm = Line(p0, p1, 33)
        self.add_connector("test_norm1", test_norm)

        b = BezierCurve()
        b.add_control_point(self.CP1)
        b.add_control_point(CP1h)
        b.add_control_point(CP0h)
        b.add_control_point(self.CP0)
        b.ni = self.bsize
        b.update()
        self.add_connector("cap0", b)
        self.add_connector("mid1", b.copy())

        p = CoonsPatch(
            edge2=self.cap0,
            edge3=self.cap1,
            edge0=self.cap2,
            edge1=self.cap3,
            interpolant="linear",
        )
        self.patches["cap"] = p
        self.domain.add_blocks(p, names=["cap"])

        p = CoonsPatch(
            edge2=self.mid0, edge3=self.mid1, edge0=self.mid2, edge1=self.mid3
        )
        self.patches["mid1"] = p
        self.domain.add_blocks(p, names=["mid1"])

        basec0 = Curve(points=c0)
        self.add_connector("basec0", basec0)
        TEc0 = Curve(points=self.TEc.points[: self.ni_mid].copy())
        self.add_connector("TEc0", TEc0)
        cap2inv = Curve(points=self.cap2.points[::-1].copy())
        self.add_connector("cap2inv", cap2inv)

        p = CoonsPatch(
            edge2=self.basec0,
            edge3=self.cap2inv,
            edge0=self.TEc0,
            edge1=self.mid2,
        )
        self.patches["mid0"] = p
        self.domain.add_blocks(p, names=["mid0"])

        cfront = Curve(points=c2)
        self.add_connector("cfront", cfront)
        ctmp = Curve(points=self.LEc.points[::-1])
        cons = ctmp.divide_connector(self.ni_mid)
        cLEsplit = cons[0]
        self.add_connector("cLEsplit", cLEsplit)

        p = CoonsPatch(
            edge0=self.mid3,
            edge1=self.cLEsplit,
            edge2=self.cfront,
            edge3=self.cap3,
        )
        self.patches["mid2"] = p
        self.domain.add_blocks(p, names=["mid2"])

        self.domain.join_blocks("collar0", "collar1")
        self.domain.join_blocks("collar0-joined", "collar2")
        self.domain.split_blocks(bsizei=self.bsize, blocks=["collar0-joined"])
        self.domain.join_blocks("mid0", "TEl")
        self.domain.join_blocks("LEu", "TEu")
        self.domain.join_blocks("cap", "LEu-joined")
        self.domain.join_blocks("mid2", "LEl")
        self.domain.join_blocks("mid0-joined", "collar0-split0002")
        self.domain.join_blocks("mid1", "collar0-split0001")
        self.domain.join_blocks("mid2-joined", "collar0-split0000")

        # mirror the VG vane and rotate
        self.domain.mirror_z(copy=True)
        self.domain.rotate_y(self.beta)

        # call MesherBase's mirror and rotate to copy and rotate all connectors
        self.mirror_z(copy=True)
        self.rotate_y(self.beta)

        # save original connectors
        self.hconnectors = self.connectors
        self.connectors = {}
        # new connectors based on domain block boundaries
        self.connectors_from_domain()

        # VG anchor point used to position base plate
        self.TE_anchor = self.TE.points[0]
        self.TE_anchor[1] = 0.0

        # base plate
        delta1 = self.delta1 / self.h
        delta2 = self.delta2 / self.h
        plate_len = lnorm * self.l_base
        xmin = -(plate_len - lnorm) / 2.0 + self.base_offset / plate_len
        xmax = xmin + plate_len + self.base_offset / plate_len
        zmin = self.TE_anchor[2] - delta1 / 2.0
        zmax = self.TE_anchor[2] + delta2 / 2.0
        self.zmin = zmin
        self.zmax = zmax
        self.xmin = xmin
        self.xmax = xmax
        # draw box
        zm = Line(
            np.array([xmax, 0, zmin]),
            np.array([xmin, 0, zmin]),
            ni=(self.bsize - 1) * 2 + 1,
        )
        zm.redistribute(
            dist=[[0, 0.02, 1], [0.5, 0.005, zm.ni / 2.0], [1.0, 0.02, zm.ni]]
        )
        zp = Line(
            np.array([xmax, 0, zmax]),
            np.array([xmin, 0, zmax]),
            ni=(self.bsize - 1) * 2 + 1,
        )
        zp.redistribute(
            dist=[[0, 0.02, 1], [0.5, 0.005, zp.ni / 2.0], [1.0, 0.02, zp.ni]]
        )
        xm = Line(
            np.array([xmin, 0, zmin]), np.array([xmin, 0, zmax]), ni=self.bsize
        )
        # xm.dist = [[0, 0.01, 1], [0.5, 0.001, self.bsize/2],[1., 0.01, self.bsize]]
        xm.redistribute(
            dist=[
                [0, 0.04, 1],
                [0.5, 0.01, int((self.bsize + 1) * 0.5)],
                [1.0, 0.04, self.bsize],
            ]
        )
        xp = Line(
            np.array([xmax, 0, zmax]), np.array([xmax, 0, zmin]), ni=self.bsize
        )
        xp.redistribute(
            dist=[
                [0, 0.04, 1],
                [0.5, 0.01, int((self.bsize + 1) * 0.5)],
                [1.0, 0.04, self.bsize],
            ]
        )
        cc = zm.divide_connector(self.bsize)
        # cc[1].invert()
        self.add_connector("zm0", cc[1])
        self.add_connector("zm1", cc[0])
        cc = zp.divide_connector(self.bsize)
        # cc[1].dist = [[0, 0.05, 1], [1., -1, self.bsize]]
        # cc[1].redistribute_flag = True
        # cc[1].dist_ni = self.bsize
        cc[1].invert()
        self.add_connector("zp0", cc[1])
        self.add_connector("zp1", cc[0])
        self.add_connector("xm", xm)
        self.add_connector("xp", xp)
        self.place_cons = [
            self.zm0,
            self.zm1,
            self.zp0,
            self.zp1,
            self.xm,
            self.xp,
        ]

        # create Bezier curve from LE to (xmin, 0, zmax)
        ni_plate = self.bsize - self.connectors["mid2-joined_u1"].ni + 1
        p0 = self.connectors["mid2-joined_u0"].points[-1]
        self.pLE = p0
        pts = self.connectors["mid2-joined_u0"].points
        p3 = np.array([self.xmin, 0.0, self.zmax])
        t2 = p0 - p3
        l2 = np.dot(t2, t2) ** 0.5
        n1 = pts[-1] - pts[0]
        n1[1] = 0
        n1 /= np.dot(n1, n1) ** 0.5
        p1 = self.fLE0 * p0 + self.fLE0 * l2 * n1
        n2 = np.array([2**0.5 / 2, 0, -(2**0.5) / 2])
        p2 = p3 + self.fLE1 * l2 * n2
        l0 = BezierCurve()
        l0.add_control_point(p0)
        l0.add_control_point(p1)
        l0.add_control_point(p2)
        l0.add_control_point(p3)
        l0.ni = ni_plate
        l0.update()
        l0.redistribute(dist=[[0, 0.01, 1], [1, -1, ni_plate]])
        self.add_connector("plate_LE", l0)

        p0 = self.connectors["mid2-joined_v1"].points[-1]
        p3 = self.connectors["zp0"].points[-1]
        l1 = Line(p0, p3, ni=ni_plate)
        dp = self.connectors["mid0-joined_u0"].dp[-1]
        dp[1] = 0.0
        p1 = p0 + dp * l1.smax * 0.2
        l2 = BezierCurve()
        l2.add_control_point(p0)
        l2.add_control_point(p1)
        l2.add_control_point(p3)
        l2.ni = ni_plate
        l2.update()
        l2.redistribute(dist=[[0, 0.01, 1], [1, -1, ni_plate]])
        self.add_connector("plate_midp0", l2)

        p = CoonsPatch(
            edge2=self.connectors["mid2-joined_v1"],
            edge3=self.connectors["zp0"],
            edge0=self.connectors["plate_LE"],
            edge1=self.connectors["plate_midp0"],
            interpolant="linear",
        )
        self.domain.add_blocks(p, ["platez0"])
        # create Bezier curve from VG z+ mid to zp curve

        p0 = self.connectors["mid1-joined_v0"].points[0]
        p3 = self.connectors["zp1"].points[0]
        l3 = Line(p0, p3, ni_plate)
        dp = self.connectors["mid0-joined_u0"].dp[-1]
        dp[1] = 0.0
        p1 = p0 + dp * l3.smax * 0.2
        # l = Line(p0, p3, ni_plate)
        # l.redistribute(dist=[[0, 0.01, 1], [1, -1, ni_plate]])
        l3 = BezierCurve()
        l3.add_control_point(p0)
        l3.add_control_point(p1)
        l3.add_control_point(p3)
        l3.ni = ni_plate
        l3.update()
        l3.redistribute(dist=[[0, 0.01, 1], [1, -1, ni_plate]])
        self.add_connector("plate_midp1", l3)

        p = CoonsPatch(
            edge0=self.connectors["mid1-joined_v0"],
            edge1=self.connectors["zp1"],
            edge2=self.connectors["plate_midp1"],
            edge3=self.connectors["plate_midp0"],
            interpolant="linear",
        )
        self.domain.add_blocks(p, ["platez1"])

        # create Bezier curve from TE to (xmax, 0, zmin)
        p0 = self.connectors["mid0-joined_v1"].points[-1]
        p3 = np.array([self.xmax, 0.0, self.zmin])
        t2 = p0 - p3
        l2 = np.dot(t2, t2) ** 0.5
        n1 = p0 - self.pLE
        n1[1] = 0
        n1 /= np.dot(n1, n1) ** 0.5
        p1 = p0 + self.fTE0 * l2 * n1
        n2 = np.array([-(2**0.5) // 2, 0, 2**0.5 // 2])
        p2 = p3 + self.fTE1 * l2 * n2
        l4 = BezierCurve()
        l4.add_control_point(p0)
        l4.add_control_point(p1)
        l4.add_control_point(p2)
        l4.add_control_point(p3)
        l4.ni = ni_plate
        l4.update()
        l4.redistribute(dist=[[0, 0.0065, 1], [1, -1, ni_plate]])
        self.add_connector("plate_TE", l4)

        p = CoonsPatch(
            edge2=self.connectors["mid0-joined_v1"],
            edge3=self.connectors["xp"],
            edge0=self.connectors["plate_midp1"],
            edge1=self.connectors["plate_TE"],
            interpolant="linear",
        )
        self.domain.add_blocks(p, ["plate_TE"])

        c = self.connectors["mid0-joined-copy_v0"].copy()
        c.invert()
        self.add_connector("mid0-joined-copy_v0c", c)
        p0 = self.connectors["mid0-joined-copy_v0c"].points[-1]
        p3 = self.connectors["zm1"].points[-1]
        lt = Line(p0, p3, ni=ni_plate)
        dp = self.connectors["mid0-joined-copy_u0"].dp[0]
        dp[1] = 0.0
        p1 = p0 - dp * lt.smax * 0.2
        l5 = BezierCurve()
        l5.add_control_point(p0)
        l5.add_control_point(p1)
        l5.add_control_point(p3)
        l5.ni = ni_plate
        l5.update()
        l5.redistribute(dist=[[0, 0.01, 1], [1, -1, ni_plate]])
        self.add_connector("plate_midm1", l5)

        p = CoonsPatch(
            edge2=self.connectors["mid0-joined-copy_v0c"],
            edge3=self.connectors["zm1"],
            edge0=self.connectors["plate_TE"],
            edge1=self.connectors["plate_midm1"],
            interpolant="linear",
        )
        self.domain.add_blocks(p, ["platezm1"])

        lt = Line(p0, p3, ni=ni_plate)
        p0 = self.connectors["mid1-joined-copy_v1"].points[-1]
        dp = self.connectors["mid2-joined-copy_u1"].dp[0]
        dp[1] = 0.0
        p1 = p0 - dp * lt.smax * 0.2
        p3 = self.connectors["zm0"].points[-1]
        l6 = BezierCurve()
        l6.add_control_point(p0)
        l6.add_control_point(p1)
        l6.add_control_point(p3)
        l6.ni = ni_plate
        l6.update()
        # l = Line(p0, p3, ni=ni_plate)
        # l.redistribute(dist=[[0, 0.01, 1], [1, -1, ni_plate]])
        self.add_connector("plate_midm0", l6)

        p = CoonsPatch(
            edge2=self.connectors["mid1-joined-copy_v1"],
            edge3=self.connectors["zm0"],
            edge0=self.connectors["plate_midm1"],
            edge1=self.connectors["plate_midm0"],
            interpolant="linear",
        )
        self.domain.add_blocks(p, ["platezm0"])

        c = self.connectors["mid2-joined-copy_v0"].copy()
        c.invert()
        self.add_connector("mid2-joined-copy_v0c", c)

        p = CoonsPatch(
            edge2=self.connectors["mid2-joined-copy_v0c"],
            edge3=self.connectors["xm"],
            edge0=self.connectors["plate_midm0"],
            edge1=self.connectors["plate_LE"],
            interpolant="linear",
        )
        self.domain.add_blocks(p, ["plate_LEm"])

        # join the domains
        self.domain.join_blocks("mid2-joined", "platez0")
        self.domain.join_blocks("mid1-joined", "platez1")
        self.domain.join_blocks("mid0-joined", "plate_TE")
        self.domain.join_blocks("mid0-joined-copy", "platezm1")
        self.domain.join_blocks("mid1-joined-copy", "platezm0")
        self.domain.join_blocks("mid2-joined-copy", "plate_LEm")

        # not used ...
        sc = SegmentedCurve()
        c = Curve(self.connectors["mid0-joined_v1"].points[::-1])
        sc.add_segment(c)
        sc.add_segment(self.connectors["mid1-joined_v0"])
        c = Curve(points=self.connectors["mid2-joined_v1"].points[::-1])
        sc.add_segment(c)
        sc.add_segment(self.connectors["mid2-joined-copy_v0"])
        c = Curve(points=self.connectors["mid1-joined-copy_v1"].points[::-1])
        sc.add_segment(c)
        sc.add_segment(self.connectors["mid0-joined-copy_v0"])
        sc.update()

        self.sf = sc

        c = Curve(points=self.xp.points[::-1].copy())
        sc = SegmentedCurve()
        sc.add_segment(c)
        sc.add_segment(self.zp1)
        c = Curve(points=self.zp0.points[::-1].copy())
        sc.add_segment(c)
        c = Curve(points=self.xm.points[::-1].copy())
        sc.add_segment(c)
        c = Curve(points=self.zm0.points[::-1].copy())
        sc.add_segment(c)
        c = Curve(points=self.zm1.points[::-1].copy())
        sc.add_segment(c)
        sc.update()
        self.sfout = sc

        # build plate padding
        dx = 0.2
        dz = 0.2
        sc = SegmentedCurve()
        p0 = np.array([self.xmin - dx, 0, self.zmax + dz])
        p1 = np.array([self.xmax + dx, 0, self.zmax + dz])
        p2 = np.array([self.xmax + dx, 0, self.zmin - dz])
        p3 = np.array([self.xmin - dx, 0, self.zmin - dz])

        l0 = Line(p0, p1, ni=self.bsize * 2 - 1)
        l1 = Line(p1, p2, ni=self.bsize)
        l2 = Line(p2, p3, ni=self.bsize * 2 - 1)
        l3 = Line(p3, p0, ni=self.bsize)
        sc.add_segment(l0)
        sc.add_segment(l1)
        sc.add_segment(l2)
        sc.add_segment(l3)
        sc.update()
        self.plate_buffer = sc
