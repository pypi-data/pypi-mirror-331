import math
import time

import numpy as np

from PGLW.main.bezier import BezierCurve
from PGLW.main.coons import CoonsPatch
from PGLW.main.curve import Circle, Curve, Line, SegmentedCurve
from PGLW.main.domain import Block, Domain
from PGLW.main.geom_tools import RotX, dotX


class CoonsNacelle(object):
    """
    Generates a CFD ready structured grid around a rotationally
    symmetric spinner and nacelle with blade root connecting to
    a blade surface.

    Parameters
    ----------
    nblades: int
        number of blades
    blade_root_radius: float
        blade root radius
    hub_length: float
        length of the hub, extending from spinner end to nacelle start
    nacelle_curve: array
        2D nacelle shape curve oriented in x-y with blade root center
        at x=0 and spinner tip at -x
    nacelle_shape_file: str
        file containing 2D cross sectional shape of nacelle
        (only needed if nacelle_curve is not provided)
    tip_con: array
        blade root cross-sectional shape curve
    ds_root_start: float
        cell size at root/hub junction
    ds_root_end: float
        cell size at root end/blade start junction
    ds_nacelle: float
        cell size at nacelle start
    nb_nacelle: int
        number of blocks in the flow direction on nacelle surface
    ni_root: int
        number of points in spanwise direction on hub and blade root
    base_nv: int
        number of points on hub in spanwise direction (ni on blade will be ni_root - base_nv)

    Returns
    -------
    domain: object
        PGLW.main.domain.Domain object containing the surface mesh
    """

    def __init__(self, **kwargs):
        self.nblades = 3
        self.downwind = False
        self.blade_root_radius = 0.06
        self.hub_length = 0.076
        self.cone_angle = 0.0

        self.tip_con = np.array([])
        self.ni_root = 20
        self.base_nv = 7
        self.nb_nacelle = 1

        self.ds_root_start = 0.001
        self.ds_root_end = 0.001
        self.ds_nacelle = 0.001

        self.dr_junction = 0.2
        self.nacelle_dr = 0.001

        self.nacelle_curve = np.array([])
        self.nacelle_shape_file = ""
        self.nacelle_dist = np.array([[]])

        self.c2d_flag = False

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

        self.domain = Domain()

    def update(self):
        t0 = time.time()

        self.domain = Domain()

        self.ni_collar = self.ni_root - self.base_nv + 1

        if self.nblades == 2:
            self.rot_period = 90.0
        elif self.nblades == 3:
            self.rot_period = 60.0

        if self.downwind:
            tip_con = Curve(points=self.tip_con)
            tip_con.rotate_z(180.0)
            nn = tip_con.points.shape[0]
            con = np.zeros(tip_con.points.shape)
            con[: (nn - 1) / 2 + 1, :] = tip_con.points[(nn - 1) / 2 :, :]
            con[(nn - 1) / 2 :, :] = tip_con.points[: (nn - 1) / 2 + 1, :]
            self.tip_con = con

        if self.nacelle_shape_file is not "":
            self.read_nacelle_shape()
        self.find_points()

        self.patches = []

        self.build_hub()
        self.build_spinner()
        self.build_nacelle()
        self.domain.rotate_z(90)
        for i in range(8):
            self.domain.join_blocks(
                "hub_base%i" % i, "hub_collar%i" % i, newname="root%i" % i
            )
        self.domain.join_blocks("root2", "root3", newname="root")
        for i in [4, 5, 6, 7, 0, 1]:
            self.domain.join_blocks("root", "root%i" % i, newname="root")

        self.domain.join_blocks(
            "nacelle_collar0", "nacelle_front0", newname="nacelle0"
        )
        self.domain.join_blocks(
            "nacelle_collar1", "nacelle_front1", newname="nacelle1"
        )

        if self.c2d_flag:
            self.compute_c2d()

        if self.downwind:
            self.domain.rotate_z(180.0)
        print("nacelle done ...", time.time() - t0)

    def read_nacelle_shape(self):
        data = np.loadtxt(self.nacelle_shape_file)
        if data.shape[1] == 2:
            dim3 = np.zeros(data.shape[0])
            points = (
                np.append(data.T.flatten(), dim3).reshape(3, data.shape[0]).T
            )
        self.nacelle_curve = Curve(points=points)

    def find_points(self):
        if not hasattr(self, "nacelle_curve"):
            raise RuntimeError(
                "nacelle_curve needs to be created if no nacelle shape file is supplied"
            )

        if self.nacelle_curve.points.shape[1] == 2:
            c = self.nacelle_curve
            dim3 = np.zeros(c.points.shape[0])
            points = (
                np.append(c.points.T.flatten(), dim3)
                .reshape(3, c.points.shape[0])
                .T
            )
            self.nacelle_curve = Curve(points=points, s=points[:, 0])
        self.nacelle_curve.rotate_x(90)
        self.hub_radius = np.interp(
            0.0,
            self.nacelle_curve.points[:, 0],
            self.nacelle_curve.points[:, 2],
        )
        self.dcone = self.hub_radius * np.sin(np.deg2rad(self.cone_angle))

        self.hubP0 = np.zeros(3)
        for i in range(3):
            self.hubP0[i] = np.interp(
                self.hub_length / 2,
                self.nacelle_curve.points[:, 0],
                self.nacelle_curve.points[:, i],
            )
        self.hubP1 = np.zeros(3)
        for i in range(3):
            self.hubP1[i] = np.interp(
                -self.hub_length / 2,
                self.nacelle_curve.points[:, 0],
                self.nacelle_curve.points[:, i],
            )
        if self.hubP0[2] != self.hubP1[2]:
            # its a cone
            self.compute_intersection = self.compute_cone_intersection
        else:
            self.compute_intersection = self.compute_cylinder_intersection

    def build_hub(self):
        # blade root
        p = self.tip_con
        self.ni = p.shape[0]
        pp = np.zeros(p.shape)
        bb = (self.ni - 1) // 4
        pp[: bb + 1, :] = p[-bb - 1 :, :]
        pp[bb:, :] = p[:-bb, :]
        root = Curve(points=pp)
        root.rotate_z(-90)

        self.bsize = (self.ni - 1) // 8 + 1

        # collar grid
        dr = self.hub_radius - self.blade_root_radius
        r = self.blade_root_radius + dr * self.dr_junction
        # b = self.blade_root_radius + self.dr_junction
        xb = self.compute_intersection(r, self.hubP0, self.hubP1, self.ni)

        # project points onto actual nacelle shape
        xb[:, 0] -= self.dcone
        for i in range(xb.shape[0]):
            xb[i, :] = self.correct_nacelle_surface(
                self.nacelle_curve, xb[i, :]
            )

        self.collar_u0s = self.divide_connector(xb, self.bsize)
        xb = self.compute_intersection(
            self.blade_root_radius, self.hubP0, self.hubP1, 9
        )
        # project points onto actual nacelle shape
        for i in range(xb.shape[0]):
            xb[i, :] = self.correct_nacelle_surface(
                self.nacelle_curve, xb[i, :]
            )
        # xb = xb[::-1]
        xb[:, 0] -= self.dcone
        self.collar_cps = Curve(points=xb)
        # root = Circle(radius=self.blade_root_radius, ni=self.ni, nd=3)
        # root.dist_ni = self.ni
        # root.run()
        # root.points[:, 2] = self.root_start

        self.collar_u1s = self.divide_connector(root.points, self.bsize)

        self.collar_vs = []
        nb = (self.ni - 1) // (self.bsize - 1)
        for i in range(nb):
            c0 = BezierCurve()
            c0.ni = self.ni_collar
            # add distribution function !
            p0 = self.collar_u0s[i].points[0]
            p1 = self.collar_cps.points[i]
            p2 = self.collar_u1s[i].points[0]
            c0.add_control_point(p0)
            c0.add_control_point(p1)
            c0.add_control_point(p2)
            c0.update()
            c0.redistribute(
                dist=np.array(
                    [
                        [0, self.ds_root_start / c0.smax, 1],
                        [1, self.ds_root_end / c0.smax, self.ni_collar],
                    ]
                )
            )
            self.collar_vs.append(c0)
        self.collar_vs.append(self.collar_vs[0])

        for i in range(8):
            p = CoonsPatch(
                edge0=(self.collar_u0s[i].copy()),
                edge1=(self.collar_u1s[i].copy()),
                edge2=(self.collar_vs[i].copy()),
                edge3=(self.collar_vs[i + 1].copy()),
                name="hub_collar" + str(i),
            )
            self.patches.append(p)
            self.domain.add_blocks(p)

        # hub base grid
        # u - curves along the base of the hub
        self.base_u0s = []
        c = Circle(
            radius=self.hubP0[2],
            ang0=np.pi - (self.nblades - 2) * np.pi / 6.0,
            ang1=(self.nblades - 2) * np.pi / 6.0,
            ax="x",
            ni=self.bsize * 2 - 1,
            nd=3,
        )
        c.translate_x(self.hubP0[0])
        cc0 = self.divide_connector(c, self.bsize)
        self.base_u0s.append(cc0[1])

        c = Circle(
            radius=self.hubP1[2],
            ang0=(self.nblades - 2) * np.pi / 6.0,
            ang1=np.pi - (self.nblades - 2) * np.pi / 6.0,
            ni=self.bsize * 2 - 1,
            ax="x",
            nd=3,
        )
        c.translate_x(self.hubP1[0])
        cc2 = self.divide_connector(c, self.bsize)

        l = np.array([cc0[1].points[-1], cc2[0].points[0]])
        c2 = Curve(points=l.copy())
        c2.redistribute(s=np.linspace(0, 1, self.bsize * 2 - 1))
        cc1 = self.divide_connector(c2, self.bsize)
        self.base_u0s.append(cc1[0])
        self.base_u0s.append(cc1[1])
        self.base_u0s.append(cc2[0])
        self.base_u0s.append(cc2[1])

        l = np.array([cc2[1].points[-1], cc0[0].points[0]])
        c3 = Curve(points=l)
        c3.redistribute(s=np.linspace(0, 1, self.bsize * 2 - 1))
        cc3 = self.divide_connector(c3, self.bsize)
        self.base_u0s.extend(cc3)
        self.base_u0s.append(cc0[0])

        self.base_vs = []
        for i in range(nb):
            p0 = self.collar_u0s[i].points[0]
            p1 = self.base_u0s[i].points[0]
            x = np.linspace(p0[0], p1[0], self.base_nv)
            ang0 = self.compute_angle(p0, 0)
            ang1 = self.compute_angle(p1, 0)
            t = np.linspace(ang0, ang1, self.base_nv)
            xx = self.cone(self.hubP0, self.hubP1, x, t)
            c = Curve(points=xx)
            c.redistribute(s=np.linspace(0, 1, self.base_nv))
            self.base_vs.append(c)
        self.base_vs.append(self.base_vs[0])

        for n in range(nb):
            p = CoonsPatch(
                edge0=(self.base_u0s[n].copy()),
                edge1=(self.collar_u0s[n].copy()),
                edge2=(self.base_vs[n].copy()),
                edge3=(self.base_vs[n + 1].copy()),
                name="hub_base" + str(n),
                interpolant="linear",
            )
            P = np.zeros(3)
            for j in range(p.nj):
                for i in range(p.ni):
                    P[0] = p.x[i, j, 0]
                    P[1] = p.y[i, j, 0]
                    P[2] = p.z[i, j, 0]
                    P1 = self.correct_nacelle_surface(self.nacelle_curve, P)
                    p.y[i, j, 0] = P1[1]
                    p.z[i, j, 0] = P1[2]
            self.patches.append(p)
            self.domain.add_blocks(p)

    def add_nacelle_dist_point(self, s, ds, index, x=None):
        """
        Add distribution points to nacelle distfunc

        Parameters
        ----------
        s : float
            Curve fraction, where 0 is at the root, and 1 at the tip.
        ds : float
            Normalized distance between points. Total curve length is 1. When
            set to -1 distfunc will figure something out.
        index : int
            Force index number on the added point.
        """
        self.nacelle_dist = np.asarray(self.nacelle_dist)

        try:
            if s in self.nacelle_dist[:, 0]:
                return
        except:
            pass
        try:
            self.nacelle_dist = np.append(
                self.nacelle_dist, np.array([[s, ds, index]]), axis=0
            )
        except:
            self.nacelle_dist = np.array([[s, ds, index]])

        self.nacelle_dist = self.nacelle_dist[
            np.argsort(self.nacelle_dist[:, 0]), :
        ]

    def build_nacelle(self):
        ni_nac = self.nb_nacelle * (self.bsize - 1) + 1 - 5
        p0 = self.base_u0s[0].points[0]
        #       p1 = p0.copy()
        p1 = np.zeros(3)
        p1[0] = self.nacelle_curve.points[-1, 0] - self.nacelle_dr
        x0 = np.linspace(p0[0], p1[0], ni_nac)
        c0 = np.zeros((ni_nac, 3))
        for i in range(3):
            c0[:, i] = np.interp(
                x0,
                self.nacelle_curve.points[:, 0],
                self.nacelle_curve.points[:, i],
            )
        p1[2] = c0[-1, 2]
        # c0[:, 0] = x0
        # c0[:, 2] = p0[2]
        c0 = Curve(points=c0)

        p2 = p1.copy()
        p2[0] += self.nacelle_dr
        p3 = p2.copy()
        p3[2] -= self.nacelle_dr
        c = BezierCurve()
        c.add_control_point(p1)
        c.add_control_point(p2)
        c.add_control_point(p3)
        c.update()
        st = c0.smax
        cu1 = SegmentedCurve(spline="pchip")
        cu1.add_segment(c0)
        cu1.add_segment(c)
        cu1.update()
        self.cu1 = cu1
        self.add_nacelle_dist_point(
            0, self.base_vs[0].ds[-1] / (self.cu1.smax * 2), 1
        )
        self.add_nacelle_dist_point(
            st / self.cu1.smax,
            self.ds_nacelle / (self.cu1.smax * 1.2),
            ni_nac - 7,
        )
        self.add_nacelle_dist_point(1, self.ds_nacelle / self.cu1.smax, ni_nac)
        self.cu1.redistribute(dist=self.nacelle_dist)

        self.cu0 = Curve(points=self.cu1.points.copy())
        self.cu0.rotate_x(self.rot_period)
        self.cu2 = Curve(points=self.cu1.points.copy())
        self.cu2.rotate_x(-self.rot_period)

        self.cv0 = Circle(
            radius=p1[2] - self.nacelle_dr,
            ang0=np.pi - (self.nblades - 2) * np.pi / 6.0,
            ang1=np.pi / 2.0,
            ni=self.bsize,
            ax="x",
            nd=3,
        )
        self.cv0.points[:, 0] = p3[0]
        self.cv1 = Circle(
            radius=p1[2] - self.nacelle_dr,
            ang0=np.pi / 2.0,
            ang1=(self.nblades - 2) * np.pi / 6.0,
            ni=self.bsize,
            ax="x",
            nd=3,
        )
        self.cv1.points[:, 0] = p3[0]

        p1 = p3.copy()
        p1[2] -= self.nacelle_dr
        p0 = dotX(RotX(np.pi / 180.0 * self.rot_period), p1)
        p2 = dotX(RotX(-np.pi / 180.0 * self.rot_period), p1)
        l1 = Line(p0, p1, ni=self.bsize)
        l2 = Line(p1, p2, ni=self.bsize)
        self.cnu0 = l1
        self.cnu1 = l2
        l3 = Line(
            p0,
            self.cu0.points[-1],
            ni=self.nb_nacelle * (self.bsize - 1) - ni_nac + 2,
        )
        l4 = Line(
            p1,
            self.cu1.points[-1],
            ni=self.nb_nacelle * (self.bsize - 1) - ni_nac + 2,
        )
        l5 = Line(
            p2,
            self.cu2.points[-1],
            ni=self.nb_nacelle * (self.bsize - 1) - ni_nac + 2,
        )

        pb = np.array([p3[0], 0, 0])
        l6 = Line(pb, p0, ni=self.bsize)
        l7 = Line(pb, p2, ni=self.bsize)
        self.l6 = l6
        self.l7 = l7

        l8 = Curve(points=self.cnu1.points.copy())
        l8.points = l8.points[::-1]

        p = CoonsPatch(
            edge0=(self.base_u0s[-1].copy()),
            edge1=(self.cv0.copy()),
            edge2=(self.cu0.copy()),
            edge3=(self.cu1.copy()),
            name="nacelle_front0",
        )
        self.patches.append(p)
        self.domain.add_blocks(p)
        p = CoonsPatch(
            edge0=(self.base_u0s[0].copy()),
            edge1=(self.cv1.copy()),
            edge2=(self.cu1.copy()),
            edge3=(self.cu2.copy()),
            name="nacelle_front1",
        )
        self.patches.append(p)
        self.domain.add_blocks(p)

        p = CoonsPatch(
            edge0=(self.cnu0.copy()),
            edge1=(self.cv0.copy()),
            edge2=(l3.copy()),
            edge3=(l4.copy()),
            name="nacelle_collar0",
        )
        self.patches.append(p)
        self.domain.add_blocks(p)
        p = CoonsPatch(
            edge0=(self.cnu1.copy()),
            edge1=(self.cv1.copy()),
            edge2=(l4.copy()),
            edge3=(l5.copy()),
            name="nacelle_collar1",
        )
        self.patches.append(p)
        self.domain.add_blocks(p)

        p = CoonsPatch(
            edge0=(l7.copy()),
            edge1=(self.cnu0.copy()),
            edge2=(l6.copy()),
            edge3=(l8.copy()),
            name="nacelle_rear",
        )
        self.patches.append(p)
        self.domain.add_blocks(p)

    def build_spinner(self):
        s = np.linspace(self.nacelle_curve.points[0, 0], self.hubP1[0], 100)
        c = np.zeros((100, 3))
        for i in range(3):
            c[:, i] = np.interp(
                s,
                self.nacelle_curve.points[:, 0],
                self.nacelle_curve.points[:, i],
            )

        c = c[::-1]
        c = Curve(points=c.copy())
        c.redistribute(s=np.linspace(0, 1, self.bsize * 2 - 1))
        self.spinner_curve = c

        cc = self.divide_connector(c, self.bsize)
        cvm0 = cc[0]
        cv0 = Curve(points=c.points.copy())
        cv1 = Curve(points=c.points.copy())

        cv0.rotate_x(self.rot_period)

        cv0s = []
        cv0a, cv0b = cv0.split(0.65)
        self.spinner_cv0 = cv0
        cv0a = Curve(points=cv0a)
        cv0a.redistribute(s=np.linspace(0, 1, self.bsize))
        cv0b = Curve(points=cv0b)
        cv0b.redistribute(s=np.linspace(0, 1, self.bsize))
        cv0b.points = cv0b.points[::-1]
        cv0s = [cv0a, cv0b]
        self.cv0s = cv0s
        cv1a = Curve(cv0a.points.copy())
        cv1b = Curve(cv0b.points.copy())
        cv1a.rotate_x(-2.0 * self.rot_period)
        cv1b.rotate_x(-2.0 * self.rot_period)
        cv1s = [cv1a, cv1b]
        self.cv1s = cv1s

        cu1 = Line(cv0s[0].points[-1], cvm0.points[-1], self.bsize)
        cu2 = Line(cv1s[0].points[-1], cvm0.points[-1], self.bsize)
        for i in range(cu1.ni):
            cu1.points[i, :] = self.correct_spinner_surface(
                self.spinner_curve, cu1.points[i, :]
            )
            cu2.points[i, :] = self.correct_spinner_surface(
                self.spinner_curve, cu2.points[i, :]
            )

        cu1.points[-1] = cu2.points[-1]

        self.spinner_cons = []
        self.spinner_cons.extend(cv0s)
        self.spinner_cons.extend(cv1s)
        self.spinner_cons.append(cvm0)
        self.spinner_cons.append(cu1)
        self.spinner_cons.append(cu2)

        p = CoonsPatch(
            edge0=(cv0s[1].copy()),
            edge1=(cu2.copy()),
            edge2=(cv1s[1].copy()),
            edge3=(cu1.copy()),
            name="spinner_tip",
        )
        self.patches.append(p)
        P = np.zeros(3)
        for j in range(1, p.nj - 1):
            for i in range(1, p.ni - 1):
                P[0] = p.x[i, j, 0]
                P[1] = p.y[i, j, 0]
                P[2] = p.z[i, j, 0]
                P1 = self.correct_spinner_surface(self.spinner_curve, P)
                p.y[i, j, 0] = P1[1]
                p.z[i, j, 0] = P1[2]
        self.domain.add_blocks(p)

        cbase0 = Curve(points=self.base_u0s[4].points.copy())
        cbase0.points = cbase0.points[::-1]

        p = CoonsPatch(
            edge0=(cbase0.copy()),
            edge1=(cu1.copy()),
            edge2=(cv0s[0].copy()),
            edge3=(cvm0.copy()),
            name="spinner_base0",
        )
        self.patches.append(p)
        P = np.zeros(3)
        for j in range(1, p.nj - 1):
            for i in range(1, p.ni - 1):
                P[0] = p.x[i, j, 0]
                P[1] = p.y[i, j, 0]
                P[2] = p.z[i, j, 0]
                P1 = self.correct_spinner_surface(self.spinner_curve, P)
                p.y[i, j, 0] = P1[1]
                p.z[i, j, 0] = P1[2]
        self.domain.add_blocks(p)

        p = CoonsPatch(
            edge0=(cv1s[0].copy()),
            edge1=(cvm0.copy()),
            edge2=(self.base_u0s[3].copy()),
            edge3=(cu2.copy()),
            name="spinner_base1",
        )
        self.patches.append(p)
        P = np.zeros(3)
        for j in range(1, p.nj - 1):
            for i in range(1, p.ni - 1):
                P[0] = p.x[i, j, 0]
                P[1] = p.y[i, j, 0]
                P[2] = p.z[i, j, 0]
                P1 = self.correct_spinner_surface(self.spinner_curve, P)
                p.y[i, j, 0] = P1[1]
                p.z[i, j, 0] = P1[2]
        self.domain.add_blocks(p)

    def compute_cylinder_intersection(self, b, P0, P1, ni):
        """
        compute the analytical intersection curve between
        two cylinders at right angles.
        `a` is the radius of the nacelle and b is the radius
        of the blade root.
        """

        a = P0[2]

        x = np.zeros((ni, 3))
        t = np.linspace(0, 2 * np.pi, ni)
        x[:, 0] = b * np.cos(t)
        x[:, 1] = b * np.sin(t)
        x[:, 2] = (a**2 - b**2 * np.sin(t) ** 2) ** 0.5

        return x

    def compute_cone_intersection(self, r1, P0, P1, ni):
        """
        compute the intersection between a cone and a cylinder
        at right angles with the cylinder centered around z=0 and
        the cone centered around x=0.
        """

        # height of the cone
        m = (P1[2] - P0[2]) / (P1[0] - P0[0])
        r = P0[2] - m * P0[0]
        h = -r / m
        c = r / h
        x = np.zeros((ni, 3))
        t = np.linspace(0, 2 * np.pi, ni)
        x[:, 0] = r1 * np.cos(t)
        x[:, 1] = r1 * np.sin(t)
        x[:, 2] = (
            c**2 * h**2
            - 2 * c**2 * h * r1 * np.cos(t)
            + c**2 * r1**2 * np.cos(t) ** 2
            - r1**2 * np.sin(t) ** 2
        ) ** (0.5)
        return x

    def cone(self, P0, P1, x, t):
        """
        compute z for a cone defined by P0 and P1
        with its axis along x=0
        """

        # height of the cone
        m = (P1[2] - P0[2]) / (P1[0] - P0[0])
        r = P0[2] - m * P0[0]
        h = -r / m
        c = r / h

        if P1[2] - P0[2] != 0:
            y = (h - x) / h * r * np.cos(t)
            z = (h - x) / h * r * np.sin(t)
        else:
            y = r * np.cos(t)
            z = r * np.sin(t)
        if isinstance(x, np.ndarray):
            xx = np.vstack([x, y, z]).T
        else:
            xx = np.array([x, y, z])
        return xx

    def correct_cone_surface(self, S):
        P = np.zeros(3)
        for j in range(S.nj):
            for i in range(S.ni):
                P[0] = S.x[i, j, 0]
                P[1] = S.y[i, j, 0]
                P[2] = S.z[i, j, 0]
                rot = self.compute_angle(P, 0)
                P1 = self.cone(self.hubP0, self.hubP1, P[0], rot)
                S.y[i, j, 0] = P1[1]
                S.z[i, j, 0] = P1[2]

        return S

    def correct_nacelle_surface(self, c, P):
        rot = self.compute_angle(P, 0) - np.pi / 2.0
        P1 = np.zeros(3)
        for i in range(3):
            P1[i] = np.interp(P[0], c.points[:, 0], c.points[:, i])
        P2 = dotX(RotX(rot), P1)
        return P2

    def correct_spinner_surface(self, c, P):
        rot = self.compute_angle(P, 0) - np.pi / 2.0
        P1 = np.zeros(3)
        for i in range(3):
            P1[i] = np.interp(P[0], c.points[:, 0][::-1], c.points[:, i][::-1])
        P2 = dotX(RotX(rot), P1)
        return P2

    def divide_connector(self, con, ni, name=None):
        cons = []
        if isinstance(con, Curve):
            points = con.points
        elif isinstance(con, np.ndarray):
            points = con

        for i in range((points.shape[0] - 1) // (ni - 1)):
            c = Curve(points=points[(ni - 1) * i : (ni - 1) * (i + 1) + 1, :])
            cons.append(c)

        return cons

    def compute_angle(self, P, axis):
        if axis == 0:
            angle = np.arctan2(P[2], P[1])
        if axis == 1:
            angle = np.arctan2(P[2], P[0])
        if axis == 2:
            angle = np.arctan2(P[1], P[0])

        return angle

    def compute_c2d(self):
        # find normal of base airfoil
        for name, block in self.domain.blocks.items():
            c2d = np.zeros((block.ni, block.nj, 3))
            points = block._block2arr()
            c2d[:, :, 0] = points[:, :, 0, 1]
            c2d[:, :, 2] = -1.0
            self.domain.blocks[name].add_scalar(
                "c2d0", np.atleast_3d(c2d[:, :, 0])
            )
            self.domain.blocks[name].add_scalar(
                "c2d1", np.atleast_3d(c2d[:, :, 1])
            )
            self.domain.blocks[name].add_scalar(
                "c2d2", np.atleast_3d(c2d[:, :, 2])
            )
