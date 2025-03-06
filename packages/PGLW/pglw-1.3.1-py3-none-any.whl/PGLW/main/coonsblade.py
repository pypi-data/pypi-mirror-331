import copy
import math

import numpy as np
from numpy.linalg import norm

from PGLW.main.airfoil import AirfoilShape
from PGLW.main.bezier import BezierCurve, FitBezier
from PGLW.main.coons import CoonsPatch
from PGLW.main.coons_extrusion import CoonsExtrusion
from PGLW.main.curve import Curve
from PGLW.main.domain import Domain
from PGLW.main.geom_tools import project_points


class CoonsBlade(object):
    def __init__(self):
        super(CoonsBlade, self).__init__()

        # self.sections = []
        # for i in range(nsec+1):
        #     setattr(self, 'af%i' % i, np.zeros(ni, 3))
        #
        # self.ni = ni
        # self.nj = nj
        # self.nsec = nsec

        self.close_te_flag = False
        self.nte = 17
        self.dist_LE = np.array([])
        self.np = 2
        self.dist_span = np.array([])
        self.cross_sections = []
        self.scale = []
        self.rot = []
        self.pos = []
        self.p_le = []
        self.chord_ni = 257
        self.ni_span = 129
        self.ni_root = 8
        self.ni_tip = 20
        self.s_tip_start = 0.98
        self.s_root_start = 0.05
        self.s_root_blend = 0.0
        self.ds_root = 0.008
        self.ds_root_start = 0.005
        self.ds_tip_start = 0.0012
        self.ds_tip = 0.00005
        self.base_rthick = np.array([])
        self.blade_filename = "blade.pfd"
        self.chord = np.array([])
        self.twist = np.array([])

        self.x = np.array([])
        self.domain = None

        # self.sections = []
        self.nsec = 0
        self.dps = []
        self.trn = []
        self.fWs = []

    def update(self):
        self._compute_cross_sections()
        self.compute_sections()
        self.set_C1()
        self.update_sections()
        # self.apply_transforms()

        self.domain = Domain()
        self.surface = Domain()
        for s in self.sections:
            self.domain.add_domain(s.domain)
        for i in range(1, self.nsec):
            self.domain.join_blocks("coons", "coons-%04d" % i, newname="coons")

        # for s in self.sections[:-2]:
        #     self.surface.add_domain(s.domain)
        # for i in range(1, self.nsec-2):
        # self.surface.join_blocks('coons', 'coons-%i'%i, newname='coons')
        self.domain.rename_block("coons", "main_section")
        # self.surface.blocks['coons'].transpose()
        # self.surface.blocks['coons']._flip_block(1)
        self.domain.blocks["main_section"].transpose()
        self.domain.blocks["main_section"]._flip_block(1)
        self.x = self.domain.blocks["main_section"]._block2arr()[:, :, 0]

    def update_sections(self):
        for sec in self.sections:
            sec.update_patches()

    def add_cross_section(
        self, points, pos, rot, chord, p_le, dp=-1, fWs=0.25
    ):
        self.cross_sections.append(points.copy())
        self.dps.append(dp)
        self.fWs.append(fWs)
        self.scale.append(chord)
        self.p_le.append(p_le)
        self.rot.append(rot)
        self.pos.append(pos)

    def _compute_cross_sections(self):
        self.scale = np.asarray(self.scale)
        self.rot = np.asarray(self.rot)
        self.pos = np.asarray(self.pos)
        self.p_le = np.asarray(self.p_le)

        self.base_airfoils = []
        for i, points in enumerate(self.cross_sections):
            points[:, 0] *= -1
            af = AirfoilShape(points=points, nd=3)
            af.redistribute(self.chord_ni, even=True)
            af.points *= self.scale[i]
            af.points[:, 2] += self.pos[i, 2]
            af.points[:, 0] += self.scale[i] * self.p_le[i]
            af.rotate_z(self.rot[i, 2], center=self.pos[i])
            af.rotate_y(self.rot[i, 1], center=self.pos[i])
            af.rotate_x(self.rot[i, 0], center=self.pos[i])
            self.base_airfoils.append(copy.deepcopy(af))
        self.nsec = len(self.base_airfoils) - 1

    def compute_sections(self):
        # construct curve for controlling spanwise distribution of points
        pts = []
        self.sections = []
        # dist = []
        # for i in range(len(self.trn)):
        #     pts.append(self.trn[i][0:3])
        #     dist.append([pts[2], 0.01, 20*i + 1])
        # self.c = Curve(points=np.array(pts))
        # self.c.redistribute(dist=dist)

        # blen = self.trn[-1][2] - self.trn[0][2]
        # ni0 = 1
        # ds0 = self.c.ds[0]
        # c = self.c
        for i in range(self.nsec):
            sec0 = self.base_airfoils[i].points
            sec1 = self.base_airfoils[i + 1].points
            sec = CoonsExtrusion(sec0, sec1)
            sec.np = self.np
            # # set ni and point distributions
            # slen = (bs[i+1] - bs[i]) * c.smax
            # ni1 = int(math.ceil(np.interp(bs[i+1], c.s, range(c.ni)))) + 1
            # ds1 = c.ds[ni1-2]
            sec.ni = 21
            # sec.ds0 = ds0  / slen
            # sec.ds1 = ds1  / slen
            sec.fW0 = self.fWs[i]
            sec.fW1 = self.fWs[i + 1]
            # print 'create', i, ni0, ni1, sec.ds0, sec.ds1, bs[i+1], slen
            sec.create_section()
            self.sections.append(sec)
        #
        #     ni0 = ni1
        #     ds0 = ds1
        # self.bs = bs

    def set_C1(self):
        # match edges and set c1 on Bezier CPs
        for s in range(1, self.nsec):
            sec0 = self.sections[s - 1]
            sec1 = self.sections[s]
            if norm(sec0.sec1 - sec1.sec0) < 1.0e-8:
                for i in range(sec0.np * 2 + 1):
                    if self.dps[s] != -1:
                        print("set dp", self.pos[s][2], self.dps[s])
                        sec0.setZero(1, self.dps[s])
                        sec1.setZero(0, self.dps[s])
                        sec0.cs[i].update()
                        sec1.cs[i].update()
                    else:
                        CPmax = np.zeros(2)
                        CPmax[0] = max(
                            abs(sec0.cs[i].CPs[1:-2, 0].flatten()).max(),
                            abs(sec1.cs[i].CPs[1:-2, 0].flatten()).max(),
                        )
                        CPmax[1] = max(
                            abs(sec0.cs[i].CPs[1:-2, 1].flatten()).max(),
                            abs(sec1.cs[i].CPs[1:-2, 1].flatten()).max(),
                        )
                        t1 = sec0.cs[i].CPs[-1] - sec0.cs[i].CPs[-2]
                        t2 = sec1.cs[i].CPs[1] - sec1.cs[i].CPs[0]
                        dp = 0.5 * (
                            t1 / np.dot(t1, t1) ** 0.5
                            + t2 / np.dot(t2, t2) ** 0.5
                        )
                        dp1 = sec0.cs[i].CPs[-1] - dp * t1[2]
                        dp2 = sec1.cs[i].CPs[0] + dp * t2[2]
                        # sec0.cs[i].CPs[-2][0] = np.sign(dp1[0]) * min(abs(dp1[0]), CPmax[0])
                        # sec0.cs[i].CPs[-2][1] = np.sign(dp1[1]) * min(abs(dp1[1]), CPmax[1])
                        # sec1.cs[i].CPs[1][0] = np.sign(dp2[0]) * min(abs(dp2[0]), CPmax[0])
                        # sec1.cs[i].CPs[1][1] = np.sign(dp2[1]) * min(abs(dp2[1]), CPmax[1])
                        sec0.cs[i].CPs[-2][:2] = dp1[:2]
                        sec1.cs[i].CPs[1][:2] = dp2[:2]

                        # update curves
                        sec0.cs[i].update()
                        sec1.cs[i].update()

        self.sections[0].setZero(0, self.dps[0])
        if self.dps[-1] != -1:
            self.sections[-1].setZero(1, self.dps[-1])
