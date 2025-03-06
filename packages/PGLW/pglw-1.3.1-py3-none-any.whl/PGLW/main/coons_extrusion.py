import copy
import math

import numpy as np
from numpy.linalg import norm

from PGLW.main.bezier import BezierCurve, FitBezier
from PGLW.main.coons import CoonsPatch
from PGLW.main.curve import Curve
from PGLW.main.domain import Domain
from PGLW.main.geom_tools import project_points


class CoonsExtrusion(object):
    """generate a coons surface based on two cross sections"""

    def __init__(self, sec0, sec1):
        self.sec0 = sec0
        self.sec1 = sec1

        self.np = 2  # Number of chordwise patches
        self.fW0 = 0.25
        self.fW1 = 0.25  # blend factor
        self.ni = 20

        self.ds0 = -1
        self.ds1 = -1
        self.s = None
        self.interpolant = "cubic"

    def update(self):
        self.create_section()
        self.update_patches()

    def create_section(self):
        # split sec0 and sec1 into nb sections and generate end connectors

        # if self.close_te_flag:

        c = Curve(points=self.sec0)
        ni = (c.ni - 1) // (self.np * 2) + 1
        self.c0 = c.divide_connector(ni)
        c = Curve(points=self.sec1)
        ni = (c.ni - 1) // (self.np * 2) + 1
        self.c1 = c.divide_connector(ni)

        # create spanwise connectors as Bezier curves
        self.cs = []
        nps = list(range(self.np * 2 + 1))
        for i in nps:
            if i == nps[-1]:
                ix = -1
                i -= 1
            else:
                ix = 0
            p0 = self.c0[i].points[ix]
            p3 = self.c1[i].points[ix]
            dp = p3 - p0
            # print dp
            p1 = p0 + dp * self.fW0
            p2 = p3 - dp * self.fW1
            c = BezierCurve()
            c.add_control_point(p0)
            c.add_control_point(p1)
            c.add_control_point(p2)
            c.add_control_point(p3)
            c.ni = self.ni
            c.update()
            if isinstance(self.s, np.ndarray):
                c.redistribute(s=self.s)
            elif self.ds0 > 0 or self.ds1 > 0:
                c.dist = np.array([[0, self.ds0, 1], [1, self.ds1, self.ni]])
                c.redistribute(dist=c.dist)
            else:
                c.redistribute(s=np.linspace(0, 1, self.ni))
            self.cs.append(c)

        # create patches
        self.patches = []
        for i in range(self.np * 2):
            p = CoonsPatch(
                edge0=self.c0[i],
                edge1=self.c1[i],
                edge2=self.cs[i],
                edge3=self.cs[i + 1],
                interpolant=self.interpolant,
            )
            self.patches.append(p)

    def update_patches(self):
        self.domain = Domain()
        for p in self.patches:
            p.update()
            self.domain.add_blocks(p)
        for i in range(1, self.np * 2):
            self.domain.join_blocks("coons-%04d" % i, "coons", newname="coons")

    def setZero(self, edge, sdir="z"):
        """
        sets gradient at edges
        """

        # todo: add option to set gradient according to normal to cross section

        if edge == 0:
            for i in range(self.np * 2 + 1):
                if sdir == "z":
                    self.cs[i].CPs[1][:2] = self.cs[i].CPs[0][:2]
                elif sdir == "y":
                    self.cs[i].CPs[1][0] = self.cs[i].CPs[0][0]
                    self.cs[i].CPs[1][2] = self.cs[i].CPs[0][2]
                elif sdir == "x":
                    self.cs[i].CPs[1][1] = self.cs[i].CPs[0][1]
                    self.cs[i].CPs[1][2] = self.cs[i].CPs[0][2]
                elif isinstance(sdir, np.ndarray):
                    dp = self.cs[i].CPs[-1] - self.cs[i].CPs[0]
                    dp = np.linalg.norm(dp)
                    sdir /= np.linalg.norm(sdir)
                    self.cs[i].CPs[1] = (
                        self.cs[i].CPs[0] + dp * sdir * self.fW1
                    )
                self.cs[i].update()
                if hasattr(self.cs[i], "dist"):
                    self.cs[i].redistribute(dist=self.cs[i].dist)
        elif edge == 1:
            for i in range(self.np * 2 + 1):
                if isinstance(sdir, str):
                    if sdir == "z":
                        self.cs[i].CPs[-2][:2] = self.cs[i].CPs[-1][:2]
                    elif sdir == "y":
                        self.cs[i].CPs[-2][0] = self.cs[i].CPs[-1][0]
                        self.cs[i].CPs[-2][2] = self.cs[i].CPs[-1][2]
                    elif sdir == "x":
                        self.cs[i].CPs[-2][1] = self.cs[i].CPs[-1][1]
                        self.cs[i].CPs[-2][2] = self.cs[i].CPs[-1][2]
                elif isinstance(sdir, np.ndarray):
                    dp = self.cs[i].CPs[-1] - self.cs[i].CPs[0]
                    dp = np.linalg.norm(dp)
                    sdir /= np.linalg.norm(sdir)
                    self.cs[i].CPs[2] = (
                        self.cs[i].CPs[-1] + dp * sdir * self.fW1
                    )
                self.cs[i].update()
                if hasattr(self.cs[i], "dist"):
                    self.cs[i].redistribute(dist=self.cs[i].dist)
