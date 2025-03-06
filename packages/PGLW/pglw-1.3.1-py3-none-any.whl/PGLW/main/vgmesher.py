import numpy as np

from PGLW.main.airfoil import AirfoilShape
from PGLW.main.coons import CoonsPatch
from PGLW.main.coons_extrusion import CoonsExtrusion
from PGLW.main.curve import Curve, Line
from PGLW.main.domain import Domain
from PGLW.main.naturalcubicspline import NaturalCubicSpline
from PGLW.main.pglmesher import PGLMesher
from PGLW.main.vgunit import VGUnit


class VGMesher(PGLMesher):
    """
    Generates a 3D airfoil cross section mesh fitted with a
    vortex generator.

    parameters
    ----------
    airfoil_filename: str
        path to file containing airfoil coordinates.
        Coordinates must be normalized to a length of 1,
        and must be ordered from TE pressure side to TE suction side.
    ni: str
        number of vertices on airfoil
    nte: str
        number of vertices on TE
    xc_vg: float
        chordwise position of VG
    l: float
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
        super(VGMesher, self).__init__(**kwargs)

        self.airfoil_filename = ""

        self.ni = 321
        self.nte = 11
        self.xc_vg = 0.2

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

    def update(self):
        self.domain = Domain()

        self.vgunit = VGUnit(**self.__dict__)
        self.vgunit.update()
        self.comps["vgunit"] = self.vgunit

        self.domain.add_domain(self.vgunit.domain)
        self.domain.get_minmax()
        self.af = AirfoilShape(
            points=np.loadtxt(self.airfoil_filename).astype(
                type(self.domain.xmin)
            ),
            nd=3,
        )
        self.af.redistribute(257)
        LE = self.af.interp_s(self.af.interp_x(self.xc_vg, "upper"))
        vgTE = self.len * np.cos(self.beta * np.pi / 180.0) + self.xc_vg
        sTE = self.af.interp_x(vgTE, "upper")
        TE = self.af.interp_s(sTE)
        # fix this
        ang = np.arctan2((TE[1].real - LE[1].real), (TE[0].real - LE[0].real))
        self.domain.scale(self.h)
        self.domain.translate_x(self.xc_vg)
        self.domain.translate_y(LE[1])
        self.domain.translate_z(-self.vgunit.zmin * self.h)
        self.domain.rotate_z(ang * 180.0 / np.pi, center=LE)
        self.domain.get_minmax()
        self.lete = Line(LE, TE, 50)

        smin = self.af.interp_x(self.domain.xmin, "upper")
        smax = self.af.interp_x(self.domain.xmax, "upper")

        ds_te = (self.af.points[-1, 1] - self.af.points[0, 1]) / (self.nte - 1)
        ds_te /= self.af.smax

        if self.nte % 2 == 0:
            self.nte += 1

        iLE = (self.ni - 1) // 2 - (self.nte - 1) // 2
        iVG_le = iLE + self.bsize
        iVG_te = iVG_le + 64
        iTE = self.ni - self.nte + 64 + 1
        dist = [
            [0.0, ds_te, 1],
            [self.af.sLE, self.af.leading_edge_dist(self.ni), iLE],
            [smin, 0.0005, iVG_le],
            [smax, 0.0005, iVG_te],
            [1.0, ds_te, iTE],
        ]
        self.af.redistribute(ni=iTE, dist=dist)
        self.dist = dist
        points = self.af.points[iLE:]
        p0 = np.array([self.domain.xmin, self.domain.ymin, 0])
        p1 = np.array([self.domain.xmax, self.domain.ymin, 0])
        l1 = Line(p0, p1, 100)
        l1.rotate_z(ang * 180.0 / np.pi, center=p0)
        self.ll = l1
        spl = NaturalCubicSpline(points[:, 0], points[:, 1])
        af_y = spl(l1.points[:, 0])
        offs = af_y - l1.points[:, 1]
        spl = NaturalCubicSpline(l1.points[:, 0], offs)
        for name, b in self.domain.blocks.items():
            offset = spl(b.x.flatten())
            b.y += offset.reshape(b.ni, b.nj, 1)

        self.af1 = self.af.points.copy()
        self.af1[:, 2] += (self.delta1 + self.delta2) / 2
        self.surf = CoonsExtrusion(self.af.points, self.af1)
        self.surf.ni = self.bsize
        self.surf.s = self.vgunit.connectors["xm"].s
        self.surf.np = 1
        self.surf.update()
        ds = self.surf.domain.blocks["coons"].isplit(iVG_le)
        dtes = ds[1].isplit(65)
        self.domain.add_blocks([ds[0], dtes[1]], names=["af0", "af1"])

        # close the trailing edge
        u0 = Curve(self.domain.blocks["af1"].get_edge(1))
        u1 = Curve(self.domain.blocks["af0"].get_edge(0))
        v0 = Line(u0.points[0], u1.points[0], self.nte)
        v1 = Line(u0.points[-1], u1.points[-1], self.nte)
        p = CoonsPatch(edge0=u0, edge1=u1, edge2=v0, edge3=v1)
        ds = p.jsplit((self.nte + 1) // 2)
        self.domain.add_blocks(ds[0], ["airfoilTEu"])
        self.domain.add_blocks(ds[1], ["airfoilTEl"])
        self.domain.join_blocks("airfoilTEl", "af0")
        self.domain.join_blocks("airfoilTEu", "af1")

        self.domain.check_connectivity(con_eps=1.0e-5)
