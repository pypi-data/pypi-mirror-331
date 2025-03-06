import time

import numpy as np

from PGLW.main.bezier import BezierCurve, FitBezier
from PGLW.main.coons import CoonsPatch
from PGLW.main.curve import Curve
from PGLW.main.domain import Domain
from PGLW.main.geom_tools import (
    calculate_rotation_matrix,
    dotX,
    project_points,
)

# from PGLW.main.airfoilshape import AirfoilShape


class CoonsBladeTip(object):
    """
        Class for generation of blade tips using coons patches.

    Parameters
    ----------

    fLE1: float
        Leading edge connector control in spanwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    fLE2: float
        Leading edge connector control in chordwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    fTE1: float
        Trailing edge connector control in spanwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    fTE2: float
        Trailing edge connector control in chordwise direction.
        pointy tip 0 <= fLE1 => 1 square tip.
    fM1: float
        Control of connector from mid-surface to tip.
        straight line 0 <= fM1 => orthogonal to starting point.
    fM2: float
        Control of connector from mid-surface to tip.
        straight line 0 <= fM2 => orthogonal to end point.
    fM3: float
        Controls thickness of tip.
        Zero thickness 0 <= fM3 => 1 same thick as tip airfoil.
    dist_cLE: float
        Cell size at tip leading edge starting point.
    dist_cTE: float
        Cell size at tip trailing edge starting point.
    dist_tip: float
        Cell size of LE and TE connectors at tip.
    dist_mid0: float
        Cell size of mid chord connector start.
    dist_mid1: float
        Cell size of mid chord connector at tip.

    s_tip: float
        Spanwise position of rounded tip
    s_tip_start: float
        Spanwise position of tip base start
    c0_angle: float
        Angle of connector from mid chord to LE/TE
    ds_tip_start: float
        Cell size in spanwise direction at tip domain start

    ni_tip: int
        Index along main axis where the tip domains replace the blade_section
    nj_LE: int
        Index along mid-airfoil connector used as starting point for tip connector
    main_section: array
        blade main section of shape (ni, nj, 3)
    """

    def __init__(self, **kwargs):
        self.fLE1 = 0.5
        self.fLE2 = 0.5
        self.fTE1 = 0.5
        self.fTE2 = 0.5
        self.fM1 = 1.0
        self.fM2 = 1.0
        self.fM3 = 0.3
        self.dist_cLE = 0.0001
        self.dist_cTE = 0.0001
        self.dist_tip = 0.00025
        self.dist_mid0 = 0.00025
        self.dist_mid1 = 0.00004
        self.s_tip = 0.995
        self.s_tip_start = 0.98
        self.c0_angle = 30.0
        self.ds_tip_start = 0.001
        self.ni_tip = 20
        self.nj_LE = 20
        self.ibase = 0
        self.Ptip = np.array([])
        self.axis = None
        self.main_section = np.array([])
        self.shear_sweep = False
        self.c2d = np.array([])
        self.c2d_flag = False
        self.s_start_c2d = 0.0

        for (
            k,
            w,
        ) in kwargs.items():
            if k.startswith("tip_"):
                name = k[4:]
            else:
                name = k
            if hasattr(self, name):
                setattr(self, name, w)

        self.connectors = []
        self.domain = Domain()

    def update(self):
        t0 = time.time()

        self.patches = []
        self.domain = Domain()
        self.connectors = []

        # the topology used requires that we have 8 edges at the tip
        self.ni = (self.main_section.shape[0] - 1) // 8

        # chord-wise split of pressure /suction side connectors
        self.nj_TE = 2 * self.ni - self.nj_LE

        if isinstance(self.axis, type(None)):
            axis = np.zeros((self.main_section.shape[1], 3))
            for j in range(self.main_section.shape[1]):
                for nd in range(3):
                    axis[j, nd] = np.mean(self.main_section[:, j, nd])
            self.axis = Curve(points=axis)

        # helper curves
        LE = self.main_section[4 * self.ni, :, :]
        TE = self.main_section[-1, :, :]
        P = self.main_section[self.ni + self.nj_TE, :, :]
        S = self.main_section[5 * self.ni + self.nj_LE, :, :]
        if self.Ptip.shape[0] == 0:
            self.Ptip = self.axis.points[-1]

        LE[-1] = self.Ptip
        TE[-1] = self.Ptip
        P[-1] = self.Ptip
        S[-1] = self.Ptip
        self.LE = Curve(points=LE)
        self.TE = Curve(points=TE)
        self.P = Curve(points=P)
        self.S = Curve(points=S)
        # self.main_axis = Curve(points=self.main_axis)

        # self.itip = np.where(abs(self.s_tip - self.PCs.s) == \
        # abs(self.s_tip - self.PCs.s).min())[0][0]
        # self.ibase = np.where(abs(self.s_tip_start - self.PCs.s) == \
        # abs(self.s_tip_start - self.PCs.s).min())[0][0]

        if self.ibase == 0:
            self.ibase = np.where(
                abs(self.s_tip_start - self.axis.s)
                == abs(self.s_tip_start - self.axis.s).min()
            )[0][0]
        self.itip = np.where(
            abs(self.s_tip - self.axis.s)
            == abs(self.s_tip - self.axis.s).min()
        )[0][0]
        self.root_airfoil = self.main_section[:, self.ibase, :]
        points = self.main_section[:, self.itip, :]
        self.Pbase = self.axis.points[self.ibase, :]

        # smooth the tip airfoil TE
        self.close_te_xc = 0.95
        nn = points.shape[0] // 2
        id1 = (np.abs(points[nn:, 0] - self.close_te_xc)).argmin() + nn
        id2 = nn - (np.abs(points[nn:0:-1, 0] - self.close_te_xc)).argmin()
        factor = 0.02
        for n in range(40):
            for i in range(id1, points[:, 0].shape[0] - 2):
                points[i, :] = (
                    factor * (0.5 * (points[i - 1, :] + points[i + 1, :]))
                    + (1.0 - factor) * points[i, :]
                )
            for i in range(1, id2 + 1):
                points[i, :] = (
                    factor * (0.5 * (points[i - 1, :] + points[i + 1, :]))
                    + (1.0 - factor) * points[i, :]
                )
        self.tip_airfoil = points
        self.tip_x1 = self.axis.s[self.itip]

        upper = self.tip_airfoil[4 * self.ni :, :]
        lower = self.tip_airfoil[: 4 * self.ni + 1, :][::-1]
        self.lower = lower
        self.upper = upper

        # construct suction side tip airfoil connectors
        self.c2LEs, self.c2TEs = self.airfoil_c2_connectors(
            upper, self.ni, self.nj_LE
        )
        self.c2LEp, self.c2TEp = self.airfoil_c2_connectors(
            lower, self.ni, self.nj_LE
        )
        (
            self.c0LEp,
            self.c0LEs,
            self.c0TEp,
            self.c0TEs,
        ) = self.airfoil_c0_connectors()
        self.connectors.extend(
            [self.c0LEs, self.c2LEs, self.c0TEs, self.c2TEs]
        )
        self.connectors.extend(
            [self.c0LEp, self.c2LEp, self.c0TEp, self.c2TEp]
        )

        self.base_patches(self.ni_tip)

        # leading edge of tip
        self.c3LE = self.edge_connector(
            self.cLE,
            self.c0LEp.points[-1],
            self.fLE1,
            self.fLE2,
            self.nj_LE,
            self.dist_cLE,
            self.dist_tip,
        )
        # trailing edge of tip
        self.c3TE = self.edge_connector(
            self.cTE,
            self.c0TEp.points[-1],
            self.fTE1,
            self.fTE2,
            self.nj_TE,
            self.dist_cTE,
            self.dist_tip,
        )

        # fix gradient across tip in case tip and base are not in y-plane
        self.c3LE, self.c3TE = self.fix_tip_connectors(self.c3LE, self.c3TE)

        # upper surface helper curve
        self.c1s = self.mid_connector(
            self.S,
            upper,
            1.0,
            self.fM1,
            self.fM2,
            self.fM3,
            self.ni,
            self.dist_mid0,
            self.dist_mid1,
        )
        # lower surface helper curve
        self.c1p = self.mid_connector(
            self.P,
            lower,
            -1.0,
            self.fM1,
            self.fM2,
            self.fM3,
            self.ni,
            self.dist_mid0,
            self.dist_mid1,
        )

        self.connectors.append(self.c3LE)
        self.connectors.append(self.c3TE)
        self.connectors.append(self.c1s)
        self.connectors.append(self.c1p)

        self.connectors.append(self.c3LE)
        self.connectors.append(self.c3TE)
        self.connectors.append(self.c1s)
        self.connectors.append(self.c1p)

        for p in self.patches:
            p.update()
            self.domain.add_blocks(p)

        # suction side leading edge patch
        p = CoonsPatch(
            edge0=self.c2LEs,
            edge1=self.c3LE,
            edge2=self.c0LEs,
            edge3=self.c1s,
            name="tip-LEs",
        )
        # if self.set_C1:
        #     b, dp0 = self.correct_C1(self.domain.blocks['tip-base4'],
        #                              p, 10, 0, None, f0=0.65)
        #     b.name = 'tip-LEs'
        #     self.domain.add_blocks(b)
        # else:
        self.domain.add_blocks(p)
        # pressure side leading edge patch
        p = CoonsPatch(
            edge0=self.c0LEp,
            edge1=self.c1p,
            edge2=self.c2LEp,
            edge3=self.c3LE,
            name="tip-LEp",
        )
        # if self.set_C1:
        #     b, dp1 = self.correct_C1(self.domain.blocks['tip-base3'],
        #                              p, 10, 1, None, f0=0.65)
        #     b.name = 'tip-LEp'
        #     self.domain.add_blocks(b)
        # else:
        self.domain.add_blocks(p)
        # suction side trailing edge patch
        p = CoonsPatch(
            edge0=self.c0TEs,
            edge1=self.c1s,
            edge2=self.c2TEs,
            edge3=self.c3TE,
            name="tip-TEs",
        )
        # if self.set_C1:
        #     b, dp2  = self.correct_C1(self.domain.blocks['tip-base7'],
        #                               p, 10, 1, dp0, f0=0.5)
        #     b.name = 'tip-TEs'
        #     self.domain.add_blocks(b)
        # else:
        self.domain.add_blocks(p)
        # pressure side trailing edge patch
        p = CoonsPatch(
            edge0=self.c2TEp,
            edge1=self.c3TE,
            edge2=self.c0TEp,
            edge3=self.c1p,
            name="tip-TEp",
        )
        # if self.set_C1:
        #     b, dp3 = self.correct_C1(self.domain.blocks['tip-base0'],
        #                              p, 10, 0, dp1, f0=0.5)
        #     b.name = 'tip-TEp'
        #     self.domain.add_blocks(b)
        # else:
        self.domain.add_blocks(p)

        # re-size tip domains
        self.domain.join_blocks("tip-LEp", "tip-TEp", newname="tip_patch_P")
        self.domain.split_blocks(blocks=["tip_patch_P"], bsize=self.ni + 1)
        self.domain.join_blocks("tip-LEs", "tip-TEs", newname="tip_patch_S")
        self.domain.split_blocks(blocks=["tip_patch_S"], bsize=self.ni + 1)

        # join base patches
        self.domain.join_blocks("tip-base0", "tip-base1", newname="tip-base")
        for i in range(6):
            self.domain.join_blocks(
                "tip-base" + str(i + 2), "tip-base", newname="tip-base"
            )

        if self.c2d_flag:
            self.compute_c2d()

        print("tip done ...", time.time() - t0)

    def edge_connector(self, P, p0, f1, f2, ni=32, dist0=0.001, dist1=0.001):
        c3 = BezierCurve()
        c3.ni = ni + 1

        # tip point
        p3 = self.Ptip

        # unit vector in the direction of the leading / trailing edge
        dp = P.dp[-1]

        # max length of vector from p0 in the diction of dp
        dpl = self.axis.dp[-1].copy()
        if self.shear_sweep:
            dpl[0] = 0.0
        ds2 = np.dot((p3 - p0), dpl) / np.dot(dp, dpl)

        # first CP along leading edge
        p1 = p0 + ds2 * dp * f1
        # second CP in tip plane
        p2 = p0 + ds2 * dp
        p2 = f2 * p2 + (1 - f2) * p3

        # add control points
        c3.add_control_point(p0)
        c3.add_control_point(p1)
        c3.add_control_point(p2)
        c3.add_control_point(p3)
        c3.update()
        c3.redistribute(
            dist=[[0.0, dist0 / c3.smax, 1], [1.0, dist1 / c3.smax, ni + 1]]
        )
        c3.dist = [[0.0, dist0 / c3.smax, 1], [1.0, dist1 / c3.smax, ni + 1]]
        return c3

    def fix_tip_connectors(self, cLE, cTE):
        t1 = cLE.CPs[-2] - cLE.CPs[-1]
        t2 = cTE.CPs[-1] - cTE.CPs[-2]
        # dp = 0.5 * (t1 + t2)
        dp = 0.5 * (t1 / np.dot(t1, t1) ** 0.5 + t2 / np.dot(t2, t2) ** 0.5)
        cLE.CPs[-2, 1:] = (
            cLE.CPs[-1, 1:] + dp[1:] * self.fLE2 * np.dot(t1, t1) ** 0.5
        )
        cTE.CPs[-2, 1:] = (
            cTE.CPs[-1, 1:] - dp[1:] * self.fTE2 * np.dot(t2, t2) ** 0.5
        )
        cLE.update()
        cTE.update()
        cLE.redistribute(dist=cLE.dist)
        cTE.redistribute(dist=cTE.dist)
        return cLE, cTE

    def mid_connector(
        self, P, x, dirN, f1, f2, f3, ni=32, dist0=0.001, dist1=0.001
    ):
        """
        generate leading edge connector

        p : array(n,3)
            leading/trailing edge curve including tip
        """
        c1 = BezierCurve()
        c1.ni = ni + 1

        idx = self.itip
        # gradient of suction / pressure side curve
        dp = P.dp[idx]
        ds = 1.0 - self.axis.s[idx]
        # first control points
        p0 = P.points[idx]
        # last control points
        p4 = self.Ptip

        # first CP (max length is half distance between p0 and p4)
        p1 = p0 + dp * ds * 0.5 * f1

        # dt is a measure for the max thickness at the tip
        dt = P.points[idx, :] - self.axis.points[idx, :]
        dt = np.dot(dt, dt) ** 0.5

        # construct unit vector in thickness direction at tip
        v1 = self.axis.dp[-1]
        v2 = np.array([1.0, 0.0, 0.0]) * dirN
        dptip = np.cross(v1, v2)
        dptip = dptip / np.dot(dptip, dptip) ** 0.5

        # third CP controlling thickness at the tip
        p3 = p4.copy()
        p3[1] = p3[1] + abs(dt) * f3
        # project onto normal vector
        p3 = p4 + dptip * (p3[1] - p4[1])
        # unit vector
        dp2 = p3 - p1
        dp2 /= np.dot(dp2, dp2) ** 0.5
        p2 = p1 + dp2 * ds * 0.5 * (1.0 - f2)
        p2[0] = p3[0]

        c1.add_control_point(p0)
        c1.add_control_point(p1)
        c1.add_control_point(p2)
        c1.add_control_point(p3)
        c1.add_control_point(p4)
        c1.update()
        c1.redistribute(
            dist=[[0.0, dist0 / c1.smax, 1], [1.0, dist1 / c1.smax, ni + 1]]
        )
        # ps = project_points(c1.points, self.main_section,
        #                     self.PCs.main_axis.dp[self.itip])

        return c1

    def base_patches(self, ni):
        # list of connectors in spanwise direction
        cu = []
        # trailing edge connector - bezier fit
        c = self.TE.points[self.ibase : self.itip + 1].copy()
        c = np.vstack([c, self.c0TEs.points[-1]])
        self.cTE = Curve(points=c)
        self.cTE.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cTE / self.cTE.smax, ni],
            ]
        )
        self.cTE.dist = [
            [0.0, self.ds_tip_start / self.cTE.smax, 1],
            [1.0, self.dist_cTE / self.cTE.smax, ni],
        ]
        cu.append(self.cTE)

        # connector ending at tip junction TE pressure side
        c = Curve(
            points=self.main_section[self.ni, self.ibase : self.itip + 1, :]
        )
        c.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cTE / c.smax, ni],
            ]
        )
        cu.append(c)
        # curve connecting to mid tip
        c = Curve(
            points=self.main_section[
                2 * self.ni, self.ibase : self.itip + 1, :
            ]
        )
        c.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cTE / c.smax, ni],
            ]
        )
        cu.append(c)
        # connector ending at tip junction LE pressure side
        c = Curve(
            points=self.main_section[
                3 * self.ni, self.ibase : self.itip + 1, :
            ]
        )
        c.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cLE / c.smax, ni],
            ]
        )
        cu.append(c)

        # leading edge connector - bezier fit
        c = self.LE.points[self.ibase : self.itip + 1].copy()
        c = np.vstack([c, self.c0LEs.points[-1]])
        self.cLE = Curve(points=c)
        self.cLE.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cLE.smax, 1],
                [1.0, self.dist_cLE / self.cLE.smax, ni],
            ]
        )
        self.cLE.dist = [
            [0.0, self.ds_tip_start / self.cLE.smax, 1],
            [1.0, self.dist_cLE / self.cLE.smax, ni],
        ]
        cu.append(self.cLE)

        # connector ending at tip junction LE suction side
        c = Curve(
            points=self.main_section[
                5 * self.ni, self.ibase : self.itip + 1, :
            ]
        )
        c.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cLE / c.smax, ni],
            ]
        )
        cu.append(c)
        # curve connecting to mid tip
        c = Curve(
            points=self.main_section[
                6 * self.ni, self.ibase : self.itip + 1, :
            ]
        )
        c.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cTE / c.smax, ni],
            ]
        )
        cu.append(c)
        # connector ending at tip junction TE suction side
        c = Curve(
            points=self.main_section[
                -self.ni - 1, self.ibase : self.itip + 1, :
            ]
        )
        c.redistribute(
            dist=[
                [0.0, self.ds_tip_start / self.cTE.smax, 1],
                [1.0, self.dist_cTE / c.smax, ni],
            ]
        )
        cu.append(c)
        cu.append(self.cTE)

        # list of connectors in chordwise direction root
        cv0 = self.divide_connector(self.root_airfoil, self.ni + 1)
        ct = self.divide_connector(self.tip_airfoil, self.ni + 1)
        # construct tip connector and split in segments of size ni
        ctip = self.c0TEp.points[::-1]
        ctip = np.append(ctip, ct[1].points[1:], axis=0)
        ctip = np.append(ctip, ct[2].points[1:], axis=0)
        ctip = np.append(ctip, self.c0LEp.points[1:], axis=0)
        ctip = np.append(ctip, self.c0LEs.points[::-1][1:], axis=0)
        ctip = np.append(ctip, ct[5].points[1:], axis=0)
        ctip = np.append(ctip, ct[6].points[1:], axis=0)
        ctip = np.append(ctip, self.c0TEs.points[1:], axis=0)
        cv1 = self.divide_connector(ctip, self.ni + 1)

        self.connectors.extend(cv0)
        self.connectors.extend(cv1)

        for i in range(8):
            p = CoonsPatch(
                edge2=cu[i],
                edge3=cu[i + 1],
                edge0=cv0[i],
                edge1=cv1[i],
                interpolant="cubic",
                name="tip-base" + str(i),
            )
            self.connectors.append(cu[i])
            self.connectors.append(cu[i + 1])
            self.connectors.append(cv0[i])
            self.connectors.append(cv1[i])
            self.patches.append(p)

    def airfoil_c0_connectors(self):
        """
        construct tip airfoil connectors
        """
        x = self.tip_airfoil
        ni = (x.shape[0] - 1) // 8
        # leading edge pressure side connector
        c1 = x[3 * ni : 4 * ni + 1, :]
        dx = sum((c1[-1] - c1[0]) ** 2) ** 0.5 * np.tan(
            np.pi / 180 * self.c0_angle
        )
        x1 = self.interpolate_profile(self.tip_x1 + dx)
        c2 = x1[3 * ni : 4 * ni + 1, :]
        n = c1.shape[0]
        c0lep = self.interp_diag(c1, c2)
        # c0lep[1:-2] = project_points(c0lep[1:-2], self.main_section[:4*self.ni,:,:],
        #                              self.PCs.main_axis.dp[self.itip])
        c0lep = Curve(points=c0lep)
        c0lep.ni = n

        # leading edge suction side connector
        c1 = x[4 * ni : 5 * ni + 1, :][::-1]
        c2 = x1[4 * ni : 5 * ni + 1, :][::-1]
        n = c1.shape[0]
        c0les = self.interp_diag(c1, c2)
        # c0les[1:-2] = project_points(c0les[1:-2], self.main_section[4*self.ni:,:,:],
        #                              self.PCs.main_axis.dp[self.itip])
        c0les = Curve(points=c0les)
        c0les.ni = n

        # trailing edge pressure side connector
        c1 = x[: ni + 1, :][::-1]
        dx = sum((c1[-1] - c1[0]) ** 2) ** 0.5 * np.tan(
            np.pi / 180 * self.c0_angle
        )
        x1 = self.interpolate_profile(self.tip_x1 + dx)
        # curve from airfoil LE to x[ni]
        c2 = x1[: ni + 1, :][::-1]
        n = c1.shape[0]
        c0tep = self.interp_diag(c1, c2)
        # c0tep[1:-2] = project_points(c0tep[1:-2], self.main_section[:4*self.ni,:,:],
        #                              self.PCs.main_axis.dp[self.itip])
        c0tep = Curve(points=c0tep)
        c0tep.ni = n

        # trailing edge suction side connector
        c1 = x[-ni - 1 :, :]
        c2 = x1[-ni - 1 :, :]
        n = c1.shape[0]
        c0tes = self.interp_diag(c1, c2)
        # c0tes[1:-2] = project_points(c0tes[1:-2], self.main_section[4*self.ni:,:,:],
        #                              self.PCs.main_axis.dp[self.itip])
        c0tes = Curve(points=c0tes)
        c0tes.ni = n

        return c0lep, c0les, c0tep, c0tes

    def airfoil_c2_connectors(self, x, ni, nj):
        c2le = x[ni : ni + nj + 1, :]
        n = c2le.shape[0]
        c2le = Curve(nd=3, points=c2le)
        c2le.ni = n

        # curve from mid-point to x[3*ni]
        c2te = x[ni + nj : -ni, :][::-1]
        n = c2te.shape[0]
        c2te = Curve(nd=3, points=c2te)
        c2te.ni = n
        return c2le, c2te

    def interp_diag(self, c1, c2):
        """
        interpolate diagonally between two curves.

        used to construct angled connectors from LE and TE to
        mid-chord.
        """

        ni = c1.shape[0]
        denu = 1.0 / (c1.shape[0] - 1)

        cn = np.zeros(c1.shape)
        for i in range(ni):
            # dirty hack - needs to be improved
            # u = i * denu
            u = np.sin((i * denu) * np.pi / 2)
            # u = np.tanh(i * denu * 3.)
            cn[i, :] = (1 - u) * c1[i, :] + u * c2[i, :]

        cn = Curve(points=cn)
        # cn.redistribute( s=s)
        return cn.points

    def interpolate_profile(self, ix):
        """
        interpolate the profile at a ix position on the blade,
        relative to the running length of the blade

        Parameters:
        -----------
        ix: float
            position to interpolate the profile

        Returns:
        --------
        prof: array
            new profile
        """
        ni = self.main_section.shape[0]
        # Interpolate each points
        prof = np.zeros((ni, 3))
        for i in range(self.main_section.shape[0]):
            for iX in range(3):
                prof[i, iX] = np.interp(
                    ix, self.axis.s, self.main_section[i, :, iX]
                )

        return prof

    def divide_connector(self, con, ni):
        """ """

        cons = []
        if isinstance(con, Curve):
            points = con.points
        elif isinstance(con, np.ndarray):
            points = con

        for i in range((con.shape[0] - 1) // (ni - 1)):
            c = Curve(points=points[(ni - 1) * i : (ni - 1) * (i + 1) + 1, :])
            cons.append(c)

        return cons

    def correct_C1(self, P1, P2, ip, flip, dpn, f0=1.0):
        """NOT WORKING"""
        # unit vector in the direction of the leading / trailing edge
        c0 = Curve(
            points=np.vstack(
                [P1.x[:, ip, 0], P1.y[:, ip, 0], P1.z[:, ip, 0]]
            ).T
        )
        dp = c0.dp[-1]

        blocks = P2.jsplit(ip)
        b0 = blocks[0]
        b1 = blocks[1]
        if flip == 0:
            blocks = P2.jsplit(ip)
            b0 = blocks[0]
            b1 = blocks[1]
            cu = np.vstack([b0.x[:, -1, 0], b0.y[:, -1, 0], b0.z[:, -1, 0]]).T
            cu = Curve(points=cu)
        else:
            blocks = P2.isplit(ip)
            b0 = blocks[0]
            b1 = blocks[1]
            cu = np.vstack([b0.x[-1, :, 0], b0.y[-1, :, 0], b0.z[-1, :, 0]]).T
            cu = Curve(points=cu)

        self.fit_cu = cu
        cu.redistribute_flag = False
        fit = FitBezier()
        fit.nCPs = 5
        fit.lsq_xtol = 0.0001
        fit.curve_in = cu
        fit.execute()
        cuN = fit.curve_out
        dx = cuN.CPs[1] - cuN.CPs[0]
        dx = np.dot(dx, dx) ** 0.5 * f0
        cuN.CPs[1] = cuN.CPs[0] + dp * dx

        if dpn is not None:
            dx1 = cuN.CPs[-2] - cuN.CPs[-1]
            dx1 = np.dot(dx1, dx1) ** 0.5 * f0
            cuN.CPs[-2] = cuN.CPs[-1] + dpn * dx1
        cuN.fdist = cu.s
        cuN.execute()
        ps = cuN.points.copy()
        ps[1:-1] = project_points(
            cuN.points[1:-1], self.main_section, self.axis.dp[self.itip]
        )
        cuN = Curve(points=ps)
        cuN.fdist = cu.s
        cuN.execute()
        if flip == 0:
            Pu0 = Curve(
                points=np.vstack(
                    [b0.x[:, 0, 0], b0.y[:, 0, 0], b0.z[:, 0, 0]]
                ).T
            )
            Pu0.redistribute_flag = False
            Pu1 = cuN
            P0v = Curve(
                points=np.vstack(
                    [b0.x[0, :, 0], b0.y[0, :, 0], b0.z[0, :, 0]]
                ).T
            )
            P0v.redistribute_flag = False
            P1v = Curve(
                points=np.vstack(
                    [b0.x[-1, :, 0], b0.y[-1, :, 0], b0.z[-1, :, 0]]
                ).T
            )
            P1v.redistribute_flag = False
        else:
            Pu0 = Curve(
                points=np.vstack(
                    [b0.x[:, 0, 0], b0.y[:, 0, 0], b0.z[:, 0, 0]]
                ).T
            )
            Pu0.redistribute_flag = False
            Pu1 = Curve(
                points=np.vstack(
                    [b0.x[:, -1, 0], b0.y[:, -1, 0], b0.z[:, -1, 0]]
                ).T
            )
            Pu1.redistribute_flag = False
            P0v = Curve(
                points=np.vstack(
                    [b0.x[0, :, 0], b0.y[0, :, 0], b0.z[0, :, 0]]
                ).T
            )
            P0v.redistribute_flag = False
            P1v = cuN
        p0 = CoonsPatch(edge0=Pu0, edge1=Pu1, edge2=P0v, edge3=P1v)
        p0.update()

        if flip == 0:
            Pu0 = cuN
            Pu1 = Curve(
                points=np.vstack(
                    [b1.x[:, -1, 0], b1.y[:, -1, 0], b1.z[:, -1, 0]]
                ).T
            )
            Pu1.redistribute_flag = False
            P0v = Curve(
                points=np.vstack(
                    [b1.x[0, :, 0], b1.y[0, :, 0], b1.z[0, :, 0]]
                ).T
            )
            P0v.redistribute_flag = False
            P1v = Curve(
                points=np.vstack(
                    [b1.x[-1, :, 0], b1.y[-1, :, 0], b1.z[-1, :, 0]]
                ).T
            )
            P1v.redistribute_flag = False
        else:
            Pu0 = Curve(
                points=np.vstack(
                    [b1.x[:, 0, 0], b1.y[:, 0, 0], b1.z[:, 0, 0]]
                ).T
            )
            Pu0.redistribute_flag = False
            Pu1 = Curve(
                points=np.vstack(
                    [b1.x[:, -1, 0], b1.y[:, -1, 0], b1.z[:, -1, 0]]
                ).T
            )
            Pu1.redistribute_flag = False
            P0v = cuN
            P1v = Curve(
                points=np.vstack(
                    [b1.x[-1, :, 0], b1.y[-1, :, 0], b1.z[-1, :, 0]]
                ).T
            )
            P1v.redistribute_flag = False
        p1 = CoonsPatch(edge0=Pu0, edge1=Pu1, edge2=P0v, edge3=P1v)
        p1.update()
        d = Domain()
        d.add_blocks([p0.P, p1.P])
        d.join_blocks("coons", "coons-1")
        # return d.blocks['coons']
        return d.blocks["coons-joined"], cuN.dp[-1]

    def compute_c2d(self):
        # find normal of base airfoil
        normal = self.axis.dp[self.ibase]
        rot = calculate_rotation_matrix(normal)
        print("tip normal", normal)
        self.rot_points = []
        c2dmax = 0.0
        for name, block in self.domain.blocks.items():
            block.get_minmax()
            c2d = np.zeros((block.ni, block.nj, 3))
            points = (block._block2arr()).reshape(block.ni * block.nj, 3)
            points_rot = dotX(rot, points - self.Pbase) + self.Pbase
            self.rot_points.append(points_rot.copy())
            c2d[:, :, 0] = points_rot[:, 2].copy().reshape(block.ni, block.nj)
            c2d[:, :, 0] = (c2d[:, :, 0] - self.s_start_c2d) / (
                1.0 - self.s_start_c2d
            )
            c2dmax = np.maximum(c2dmax, c2d[:, :, 0].max())
            self.domain.blocks[name].add_scalar(
                "c2d0", np.atleast_3d(c2d[:, :, 0])
            )
            self.domain.blocks[name].add_scalar(
                "c2d1", np.atleast_3d(c2d[:, :, 1])
            )
            self.domain.blocks[name].add_scalar(
                "c2d2", np.atleast_3d(c2d[:, :, 2])
            )

        for name, block in self.domain.blocks.items():
            self.domain.blocks[name].scalars["c2d0"] /= c2dmax
