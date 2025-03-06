from collections import OrderedDict

import numpy as np

from PGLW.main.bezier import _C
from PGLW.main.domain import Block
from PGLW.main.geom_tools import RotX, dotX


class BezierPatch(object):
    """
    Bezier patch based on a set of control points array(m, n, 3)

    parameters
    ----------

    CPs: array
        array of control points with dimension (m, n, 3),
        where m is the number of CPs in the u direction,
        n is the number of CPs in the v direction.
    ni: int
        number of vertices in i direction
    nj: int
        number of vertices in j direction
    """

    def __init__(self):
        self.CPs = np.array([])
        self.ni = 33
        self.nj = 33
        self.sizes = np.array([33, 33])

    def update(self):
        P = self._compute(self.CPs)
        self.x = P
        self.P = Block(P[:, :, 0], P[:, :, 1], P[:, :, 2])
        self._compute_dp()

    def elevate(self, index):
        """
        elevate the order of the bezier surface in one direction

        parameters
        ----------
        index: int
            coordinate index for u or v direction (0 or 1)
        """

        if index == 0:
            k = self.CPs.shape[0]
            CPs = np.zeros((k + 1, self.CPs.shape[1], 3))
            CPs[0] = self.CPs[0]
            CPs[-1] = self.CPs[-1]
            for i in range(1, k):
                CPs[i, :, :] = (
                    (k - i) * self.CPs[i, :, :] + i * self.CPs[i - 1, :, :]
                ) / k
        if index == 1:
            k = self.CPs.shape[1]
            CPs = np.zeros((self.CPs.shape[0], k + 1, 3))
            CPs[0] = self.CPs[0]
            CPs[-1] = self.CPs[-1]
            for i in range(1, k):
                CPs[:, i, :] = (
                    (k - i) * self.CPs[:, i, :] + i * self.CPs[:, i - 1, :]
                ) / k

        self.CPs = CPs
        self.update()

    def _compute(self, C):
        self.ni = self.sizes[0]
        self.nj = self.sizes[1]

        P = np.zeros((self.ni, self.nj, 3), dtype=C.dtype)
        denu = 1.0 / (self.ni - 1)
        denv = 1.0 / (self.nj - 1)

        _m = range(C.shape[0])
        _n = range(C.shape[1])

        for k in range(3):
            for j in range(self.nj):
                v = j * denv
                for i in range(self.ni):
                    u = i * denu
                    nn = _n[-1]
                    mm = _m[-1]
                    for n in _n:
                        # compute n'th bernstein polynomial
                        b_j = _C(nn, n) * v**n * (1 - v) ** (nn - n)
                        for m in _m:
                            # compute m'th bernstein polynomial
                            b_i = _C(mm, m) * u**m * (1 - u) ** (mm - m)
                            # multiply control point (m, n, k) by m'th and n'th
                            # bernstein polynomial
                            P[i, j, k] += C[m, n, k] * b_i * b_j

        return P

    def _compute_dp(self):
        """
        computes the derivatives (tangent vectors) along a Bezier curve
        wrt ``t``.

        see: http://pomax.github.io/bezierinfo/
        """
        Cm = np.zeros(
            (self.CPs.shape[0] - 1, self.CPs.shape[1], 3), dtype=self.CPs.dtype
        )
        nC = Cm.shape[0]
        for i in range(nC):
            Cm[i, :, :] = float(nC) * (
                self.CPs[i + 1, :, :] - self.CPs[i, :, :]
            )

        self.dPdu = self._compute(Cm)
        for j in range(self.dPdu.shape[1]):
            for i in range(self.dPdu.shape[0]):
                self.dPdu[i, j, :] = self.dPdu[i, j, :] / np.linalg.norm(
                    self.dPdu[i, j, :]
                )

        Cn = np.zeros(
            (self.CPs.shape[0], self.CPs.shape[1] - 1, 3), dtype=self.CPs.dtype
        )
        nC = Cn.shape[1]
        for j in range(nC):
            Cn[:, j, :] = float(nC) * (
                self.CPs[:, j + 1, :] - self.CPs[:, j, :]
            )

        self.dPdv = self._compute(Cn)
        for j in range(self.dPdv.shape[1]):
            for i in range(self.dPdv.shape[0]):
                self.dPdv[i, j, :] = self.dPdv[i, j, :] / np.linalg.norm(
                    self.dPdv[i, j, :]
                )

    def plot_CPs(self, wireframe=True):
        du = self.CPs[:, 0].max() - self.CPs[:, 0].min()
        dv = self.CPs[:, 1].max() - self.CPs[:, 1].min()
        dP = self.CPs[:, 2].max() - self.CPs[:, 2].min()
        maxd = np.max([du, dv, dP])
        scale = maxd / 75.0
        from mayavi import mlab
        from tvtk.api import tvtk

        if wireframe:
            mlab.figure(mlab, bgcolor=(1, 1, 1))
            xall = np.zeros((self.CPs.shape[0] * self.CPs.shape[1], 3))
            xall[:, 0] = self.CPs[:, :, 0].flatten(order="F")
            xall[:, 1] = self.CPs[:, :, 1].flatten(order="F")
            xall[:, 2] = self.CPs[:, :, 2].flatten(order="F")
            sgrid = tvtk.StructuredGrid(
                dimensions=(self.CPs.shape[0], self.CPs.shape[1], 1)
            )
            sgrid.points = xall
            d = mlab.pipeline.add_dataset(sgrid)
            mlab.pipeline.grid_plane(d, color=(0, 0, 1), line_width=2)

        for j in range(self.CPs.shape[1]):
            for i in range(self.CPs.shape[0]):
                mlab.points3d(
                    self.CPs[i, j, 0],
                    self.CPs[i, j, 1],
                    self.CPs[i, j, 2],
                    mode="sphere",
                    color=(1, 0, 0),
                    scale_factor=scale,
                )


class BezierBody(object):
    def __init__(self, nu, nv, phi0, phi1):
        self.CPs = np.zeros((nu * 3 + 1, nv * 3 + 1, 3))
        self.Ps = OrderedDict()
        self.sizes = np.array([33, 33])
        x = np.linspace(0, 1, nv * 3 + 1)
        rot = phi0
        # ang0 = 0.0
        phi = (phi1 - phi0) / nu
        C1x = 1.0
        C1y = 4.0 / 3.0 * np.tan(phi / 4.0)
        C2x = np.cos(phi) + 4.0 / 3.0 * np.tan(phi / 4.0) * np.sin(phi)
        C2y = np.sin(phi) - 4.0 / 3.0 * np.tan(phi / 4.0) * np.cos(phi)

        for j in range(nv * 3 + 1):
            self.CPs[:, j, 0] = x[j]
            self.CPs[0, j, [1, 2]] = [1, 0]
            self.CPs[1, j, [1, 2]] = [C1x, C1y]
            self.CPs[2, j, [1, 2]] = [C2x, C2y]
            self.CPs[3, j, [1, 2]] = [np.cos(phi), np.sin(phi)]

        for c, i in enumerate(range(3, (nu - 1) * 3 + 1, 3)):
            phij = phi * (c + 1)
            self.CPs[i : i + 4, :, :] = dotX(RotX(phij), self.CPs[:4, :, :])

        for jj, j in enumerate(range(0, (nv - 1) * 3 + 1, 3)):
            for ii, i in enumerate(range(0, (nu - 1) * 3 + 1, 3)):
                p = BezierPatch()
                p.sizes = self.sizes
                p.CPs = self.CPs[i : i + 4, j : j + 4, :]
                self.Ps["p%i%i" % (ii, jj)] = p

        self.CPs[:, :, :] = dotX(RotX(rot), self.CPs)

    def update(self):
        for name, p in self.Ps.items():
            p.update()
