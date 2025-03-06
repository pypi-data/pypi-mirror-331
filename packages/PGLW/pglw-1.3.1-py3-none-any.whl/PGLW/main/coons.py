from __future__ import division

import warnings
from builtins import range

import numpy as np

from PGLW.main.domain import Block


class CoonsPatch(Block):
    """
    Nameing convension
                       edge1
            ---------------------------
            |                         |
            |                         |
       edge2|                         | edge3
            |                         |
            |                         |
            ---------------------------
                        edge0
    """

    def __init__(
        self,
        edge0=None,
        edge1=None,
        edge2=None,
        edge3=None,
        name="coons",
        interpolant="linear",
        edge_check=True,
        rtol_edges=1e5,
        atol_edges=1e-8,
        ni=None,
        nj=None,
    ):
        # Common parameters to both old and new construction style
        self._name = name
        self.edge_check = edge_check
        if interpolant == "linear":
            self._interpolant = self._linear
        else:
            self._interpolant = self._cubic
        self._rtol_edges = rtol_edges
        self._atol_edges = atol_edges

        if (isinstance(edge0, int) or isinstance(edge1, int)) or (
            (ni is not None) or (nj is not None)
        ):  # Old construction style
            warnings.warn(
                "Coons-Patch: The use of interger arguments for edge0 and edge1"
                "indicates that the old style CoonsPatch is used (later using add_edge"
                "to append edges). The new style CoonsPatch uses "
                "edges at initilazation. See more in Coons-Patch documentation",
                PendingDeprecationWarning,
                stacklevel=2,
            )
            if isinstance(edge0, int) or isinstance(edge1, int):
                x = np.ones([edge0 * edge1, 3])
            else:
                x = np.ones([ni * nj, 3])
            y = np.ones_like(x)
            z = np.ones_like(x)
            super(CoonsPatch, self).__init__(x=x, y=y, z=z, name=self._name)
            self._edge0 = None
            self._edge1 = None
            self._edge2 = None
            self._edge3 = None
        else:  # New construction style
            if (
                (edge0 is None)
                or (edge1 is None)
                or (edge2 is None)
                or (edge3 is None)
            ):
                raise ValueError(
                    "Coons-Patch: All edges needs needs to be specified"
                    "on initialization"
                    "(given: edge0=%s, edge1=%s, edge2=%s, edge3=%s)"
                    % (edge0, edge1, edge2, edge3)
                )
            self._edge0 = edge0
            self._edge1 = edge1
            self._edge2 = edge2
            self._edge3 = edge3
            self.update()

    def add_edge(self, edge, curve):
        warnings.warn(
            "Coons-Patch: Old-style coons construction will be remove in the future",
            PendingDeprecationWarning,
            stacklevel=2,
        )

        if edge not in list(range(4)):
            raise RuntimeError("edge index must be in the range 0-3")

        setattr(self, "_edge%d" % edge, curve)
        if not (
            (self.edge0 is None)
            or (self.edge1 is None)
            or (self.edge2 is None)
            or (self.edge3 is None)
        ):
            self.update()
        else:
            warnings.warn(
                "Coons-Patch: Was not updated since not all edges are set",
                UserWarning,
            )

    def _set_edge_connective(self):
        e00 = self._edge0.points[0]
        e20 = self._edge2.points[0]
        e30 = self._edge3.points[0]
        e2m1 = self._edge2.points[-1]
        e3m1 = self._edge3.points[-1]

        # Check connection for e00 (checking which end points of e2 and e3 is closest)
        i_e00_con = np.argmin(
            np.linalg.norm(np.array([e20, e2m1, e30, e3m1]) - e00, axis=1)
        )
        if i_e00_con == 0:
            self._edge_con = "0 -> 1, 2 -> 3"
        elif i_e00_con == 1:
            self._edge_con = "1 -> 0, 2 -> 3"
        elif i_e00_con == 2:
            self._edge_con = "0 -> 1, 3 -> 2"
        elif i_e00_con == 3:
            self._edge_con = "1 -> 0, 3 -> 2"

    def _check_edges(self):
        # Check if edge0 and edge1 as well as edge2 and edge3 have same size
        if (
            not self._edge0.points.shape[0] == self._edge1.points.shape[0]
        ) or not (self._edge2.points.shape[0] == self._edge3.points.shape[0]):
            err_msg = (
                "Edge 0,1 and Edge 2,3 needs to have the same size"
                "(edge0.shape[0]=%s, edge1.shape[0]=%s) "
                "(edge2.shape[0]=%s, edge3.shape[0]=%s)"
                % (
                    self._edge0.points.shape[0],
                    self._edge1.points.shape[0],
                    self._edge2.points.shape[0],
                    self._edge3.points.shape[0],
                )
            )
            raise ValueError(err_msg)

        # Edge end-points
        e00 = self._edge0.points[0]
        e10 = self._edge1.points[0]
        e20 = self._edge2.points[0]
        e30 = self._edge3.points[0]
        e0m1 = self._edge0.points[-1]
        e1m1 = self._edge1.points[-1]
        e2m1 = self._edge2.points[-1]
        e3m1 = self._edge3.points[-1]

        if self._edge_con == "0 -> 1, 2 -> 3":
            np.testing.assert_allclose(
                e00, e20, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e10, e2m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e0m1, e30, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e1m1, e3m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
        elif self._edge_con == "1 -> 0, 2 -> 3":
            np.testing.assert_allclose(
                e00, e2m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e10, e20, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e0m1, e3m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e1m1, e30, rtol=self.rtol_edges, atol=self.atol_edges
            )
        elif self._edge_con == "0 -> 1, 3 -> 2":
            np.testing.assert_allclose(
                e00, e30, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e10, e3m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e0m1, e20, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e1m1, e2m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
        elif self._edge_con == "1 -> 0, 3 -> 2":
            np.testing.assert_allclose(
                e00, e3m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e10, e30, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e0m1, e2m1, rtol=self.rtol_edges, atol=self.atol_edges
            )
            np.testing.assert_allclose(
                e1m1, e20, rtol=self.rtol_edges, atol=self.atol_edges
            )

    @property
    def edge0(self):
        return self._edge0

    @property
    def edge1(self):
        return self._edge1

    @property
    def edge2(self):
        return self._edge2

    @property
    def edge3(self):
        return self._edge3

    @property
    def rtol_edges(self):
        """Relative error tolerance for edge connection"""
        return self._rtol_edges

    @rtol_edges.setter
    def rtol_edges(self, rtol):
        self._rtol_edges = rtol

    @property
    def atol_edges(self):
        """Absolute error tolerance for edge connection"""
        return self._atol_edges

    @atol_edges.setter
    def atol_edges(self, atol):
        self._atol_edges = atol

    @property
    def P(self):
        warnings.warn(
            "Coons-Patch: Use of P attribute is depreciated."
            "Coons-Patch is now a child-class of Block so "
            "block attributes should be used directly",
            PendingDeprecationWarning,
            stacklevel=2,
        )
        return self

    def print_edge_connetivity(self):
        print(self._edge_con)
        if self._edge_con == "0 -> 1, 2 -> 3":
            print(
                """                       edge1
            ---------------------------
            |                         |
            |  v                      |
       edge2|  ^                      | edge3
            |  |                      |
            | -|----> u               |
            ---------------------------
                        edge0"""
            )
        elif self._edge_con == "1 -> 0, 2 -> 3":
            print(
                """                       edge1
             ---------------------------
             | -|----> u               |
             |  |                      |
        edge2|  v                      | edge3
             |  v                      |
             |                         |
             ---------------------------
                         edge0"""
            )
        elif self._edge_con == "0 -> 1, 3 -> 2":
            print(
                """                       edge1
             ---------------------------
             |                         |
             |                      v  |
        edge2|                      ^  | edge3
             |                      |  |
             |               u <----|- |
             ---------------------------
                         edge0"""
            )
        elif self._edge_con == "1 -> 0, 2 -> 3":
            print(
                """                       edge1
             ---------------------------
             |               u <----|- |
             |                      |  |
        edge2|                      v  | edge3
             |                      v  |
             |                         |
             ---------------------------
                         edge0"""
            )

    def _linear(self, i, j, u0, u1, v0, v1):
        u = self._get_u_from_ij(i, j, u0, u1)
        v = self._get_v_from_ij(i, j, v0, v1)
        return u, v

    def _cubic(self, i, j, u0, u1, v0, v1):
        u, v = self._linear(i, j, u0, u1, v0, v1)
        u = 3 * u**2 - 2.0 * u**3
        v = 3 * v**2 - 2.0 * v**3
        return u, v

    def _edge_u(self, iedge):
        # Get s
        s = self._edge_s(iedge)
        # return u as normalized s
        return s / s[-1]

    def _edge_s(self, iedge):
        # Get edge points
        ps = getattr(self, "edge%d" % iedge)

        # Compute ds as 3 component vector
        ds_vec = np.diff(ps.points, axis=0)

        if np.all(ds_vec < 1.0e-15):
            return np.linspace(0, 1, ps.points.shape[0])
        else:
            # Compute ds vector (n-1)
            ds = np.linalg.norm(ds_vec, axis=1)

            # Computing s as sum of ds
            s = np.zeros(len(ds) + 1)
            s[1:] = np.cumsum(ds)
            return s

    def _get_u_or_v_from_ij(self, i, j, nj, u0, u1):
        return u0[i] * j / (nj - 1) + u1[i] * (1 - j / (nj - 1))

    def _get_u_from_ij(self, i, j, u0, u1):
        return self._get_u_or_v_from_ij(
            i, j, self._edge2.points.shape[0], u0, u1
        )

    def _get_v_from_ij(self, i, j, v0, v1):
        return self._get_u_or_v_from_ij(
            j, i, self._edge0.points.shape[0], v0, v1
        )

    def edges2xyz(self):
        # if not self._edge_con == "0 -> 1, 2 -> 3":
        #     raise ValueError("CoonsPatch can only handle edges with (0 -> 1, 2 -> 3)"
        #                      "for index order "
        #                      "(given: %s)"%self._edge_con)

        if self._edge_con == "1 -> 0, 2 -> 3":
            Pu0 = self.edge1.points
            Pu1 = self.edge0.points
            P0v = self.edge2.points
            P1v = self.edge3.points
            u0 = self._edge_u(1)
            u1 = self._edge_u(0)
            v0 = self._edge_u(2)
            v1 = self._edge_u(3)
        elif self._edge_con == "0 -> 1, 3 -> 2":
            Pu0 = self.edge0.points
            Pu1 = self.edge1.points
            P0v = self.edge3.points
            P1v = self.edge2.points
            u0 = self._edge_u(0)
            u1 = self._edge_u(1)
            v0 = self._edge_u(3)
            v1 = self._edge_u(2)
        elif self._edge_con == "1 -> 3, 3 -> 2":
            Pu0 = self.edge1.points
            Pu1 = self.edge0.points
            P0v = self.edge3.points
            P1v = self.edge2.points
            u0 = self._edge_u(1)
            u1 = self._edge_u(0)
            v0 = self._edge_u(3)
            v1 = self._edge_u(2)
        else:  # self._edge_con == "0 -> 1, 2 -> 3"
            Pu0 = self.edge0.points
            Pu1 = self.edge1.points
            P0v = self.edge2.points
            P1v = self.edge3.points
            u0 = self._edge_u(0)
            u1 = self._edge_u(1)
            v0 = self._edge_u(2)
            v1 = self._edge_u(3)

        P00 = P0v[0, :]
        P10 = P1v[0, :]
        P01 = P0v[-1, :]
        P11 = P1v[-1, :]

        P = np.zeros((len(u0), len(v0), 3))
        for i in range(len(u0)):
            for j in range(len(v0)):
                u, v = self._interpolant(i, j, u0, u1, v0, v1)
                P[i, j, :] = (
                    (1 - u) * P0v[j, :]
                    + u * P1v[j, :]
                    + (1 - v) * Pu0[i, :]
                    + v * Pu1[i, :]
                )

                P[i, j, :] = (
                    P[i, j, :]
                    - (1 - u) * (1 - v) * P00
                    - u * (1 - v) * P10
                    - (1 - u) * v * P01
                    - u * v * P11
                )

        return P[:, :, 0], P[:, :, 1], P[:, :, 2]

    def update(self):
        # Deduces how edges are connected
        self._set_edge_connective()

        # Check edges
        if self.edge_check:
            self._check_edges()

        # Get x, y, z
        x, y, z = self.edges2xyz()

        # Set x, y, z from block initilize
        super(CoonsPatch, self).__init__(x=x, y=y, z=z, name=self._name)
