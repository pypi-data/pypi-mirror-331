import numpy as np

from PGLW.main.curve import Curve
from PGLW.main.distfunc import distfunc
from PGLW.main.geom_tools import calculate_length


def read_blade_planform(filename):
    """
    read a planform file with columns:

    |  s: normalized running length of blade
    |  x: x-coordinates of blade axis
    |  y: y-coordinates of blade axis
    |  z: z-coordinates of blade axis
    |  rot_x: x-rotation of blade axis
    |  rot_y: y-rotation of blade axis
    |  rot_z: z-rotation of blade axis
    |  chord: chord distribution
    |  rthick: relative thickness distribution
    |  p_le: pitch axis aft leading edge distribution
    |  dy: vertical offset of cross-section

    parameters
    ----------
    filename: str
        path to file containing planform data

    returns
    -------
    pf: dict
        dictionary containing planform data normalized
        to a span of 1.
    """

    data = np.loadtxt(filename)
    s = calculate_length(data[:, [0, 1, 2]])

    pf = {}
    pf["blade_length"] = data[-1, 2]
    pf["s"] = s / s[-1]
    pf["smax"] = s[-1]
    pf["x"] = data[:, 0] / data[-1, 2]
    pf["y"] = data[:, 1] / data[-1, 2]
    pf["z"] = data[:, 2] / data[-1, 2]
    pf["rot_x"] = data[:, 3]
    pf["rot_y"] = data[:, 4]
    pf["rot_z"] = data[:, 5]
    pf["chord"] = data[:, 6] / data[-1, 2]
    pf["rthick"] = data[:, 7]
    pf["rthick"] /= pf["rthick"].max()
    pf["athick"] = pf["rthick"] * pf["chord"]
    pf["p_le"] = data[:, 8]
    try:
        pf["dy"] = data[:, 9]
    except IndexError:
        pf["dy"] = np.zeros(data.shape[0])

    return pf


def write_blade_planform(pf, filename):
    """
    write a planform file with columns:

    |  s: normalized running length of blade
    |  x: x-coordinates of blade axis
    |  y: y-coordinates of blade axis
    |  z: z-coordinates of blade axis
    |  rot_x: x-rotation of blade axis
    |  rot_y: y-rotation of blade axis
    |  rot_z: z-rotation of blade axis
    |  chord: chord distribution
    |  rthick: relative thickness distribution
    |  p_le: pitch axis aft leading edge distribution
    |  dy: vertical offset of cross-section

    parameters
    ----------
    pf: dict
        planform dictionary
    filename: str
        path to file containing planform data
    """

    data = np.zeros((pf["x"].shape[0], 10))
    s = calculate_length(data[:, [0, 1, 2]])

    names = [
        "x",
        "y",
        "z",
        "rot_x",
        "rot_y",
        "rot_z",
        "chord",
        "rthick",
        "p_le",
        "dy",
    ]
    for i, name in enumerate(names):
        try:
            data[:, i] = pf[name]
        except RuntimeError:
            print("failed writing %s - assuming zeros" % name)
            data[:, i] = np.zeros(s.shape[0])
    fid = open(filename, "w")
    exp_prec = 15  # exponential precesion
    col_width = exp_prec + 10  # column width required for exp precision
    header_full = "#"
    header_full += (
        "".join(
            [
                (hh + " [%i]").center(col_width + 1) % i
                for i, hh in enumerate(names)
            ]
        )
        + "\n"
    )
    fid.write(header_full)
    np.savetxt(fid, data)
    fid.close()


def redistribute_planform(pf, dist=[], s=None, spline_type="akima"):
    """
    redistribute a blade planform

    Parameters
    ----------
    pf: dict
        optional dictionary containing planform. If not supplied,
        planform_filename is required. Keys:

        |  s: normalized running length of blade
        |  x: x-coordinates of blade axis
        |  y: y-coordinates of blade axis
        |  z: z-coordinates of blade axis
        |  rot_x: x-rotation of blade axis
        |  rot_y: y-rotation of blade axis
        |  rot_z: z-rotation of blade axis
        |  chord: chord distribution
        |  rthick: relative thickness distribution
        |  p_le: pitch axis aft leading edge distribution
        |  dy: vertical offset of cross-section
    dist: list
        list of control points with the form

        | [[s0, ds0, n0], [s1, ds1, n1], ... [s<n>, ds<n>, n<n>]]

        | where

            | s<n> is the curve fraction at each control point,
            | ds<n> is the cell size at each control point,
            | n<n> is the cell count at each control point.
    s: array
        optional normalized distribution of cells.
    """

    if len(dist) > 0:
        s_new = distfunc(dist)
    elif isinstance(s, np.ndarray):
        s_new = s
    else:
        raise RuntimeError("neither a valid dist or s was supplied")

    pf_new = {}
    pf_new["s"] = s_new
    for name, var in pf.items():
        if name in ["s", "blade_length", "smax"]:
            continue
        c = Curve(
            points=np.array([pf["s"], var]).T, s=pf["s"], spline=spline_type
        )
        c.redistribute(s=s_new)
        pf_new[name] = c.points[:, 1].copy()
        if name == "rthick":
            pf_new["rthick"] = np.minimum(
                np.ones(pf_new["s"].shape[0]), pf_new["rthick"]
            )

    return pf_new


class RedistributedPlanform(object):
    """
    class for redistributing a blade planform
    used by BladeMesher.

    Parameters
    ----------
    pf: dict
        optional dictionary containing planform. If not supplied,
        planform_filename is required. Keys:

        |  s: normalized running length of blade
        |  x: x-coordinates of blade axis
        |  y: y-coordinates of blade axis
        |  z: z-coordinates of blade axis
        |  rot_x: x-rotation of blade axis
        |  rot_y: y-rotation of blade axis
        |  rot_z: z-rotation of blade axis
        |  chord: chord distribution
        |  rthick: relative thickness distribution
        |  p_le: pitch axis aft leading edge distribution
        |  dy: vertical offset of cross-section
    user_dist: bool
        flag for user specified distfunc input
    dist: array
        optional distfunc input
    s_root_start: float
        spanwise position of root start
    s_root_end: float
        spanwise position of root start
    ds_root_start: float
        spanwise distribution at root start
    ds_root_end: float
        spanwise distribution at root end
    ni_root: int
        number of spanwise points
    s_tip_start: float
        Spanwise position of tip base start
    s_tip: float
        Spanwise position of rounded tip
    ds_tip_start: float
        Cell size in spanwise direction at tip domain start
    ds_tip: float
        Cell size in spanwise direction at tip
    ni_tip: int
        Index along main axis where the tip domains replace the blade_section
    n_refined_tip: int
        number of vertices from s_tip_start to tip

    returns
    -------
    pf_out: dict
        redistributed planform
    """

    def __init__(self, **kwargs):
        self.pf = {}
        self.s_tip_start = 0.99
        self.s_root_end = 0.05
        self.ds_root_start = 0.008
        self.ds_root_end = 0.005
        self.ds_tip_start = 0.0012
        self.ds_tip = 0.00005
        self.ni_span = 129
        self.ni_root = 8
        self.ni_tip = 20
        self.n_refined_tip = 50
        self.user_dist = False
        self.dist = np.array([])
        self.only_s = False

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

        self.pf_out = {}

    def add_dist_point(self, s, ds, index):
        """
        Add distribution points to distfunc

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

        self.dist = np.asarray(self.dist)

        try:
            if s in self.dist[:, 0]:
                return
        except IndexError:
            pass
        try:
            self.dist = np.append(
                self.dist, np.array([[s, ds, index]]), axis=0
            )
        except ValueError:
            self.dist = np.array([[s, ds, index]])

        self.dist = self.dist[np.argsort(self.dist[:, 0]), :]

    def update(self):
        """
        call redistribute_planform

        returns
        -------
        pf_out: dict
            redistributed planform
        """

        # add required dist points for root and tip
        if not self.user_dist:
            self.itip_start = self.ni_span - self.ni_tip
            self.add_dist_point(0.0, self.ds_root_start, 1)
            if self.ni_root > 0:
                self.add_dist_point(
                    self.s_root_end, self.ds_root_end, self.ni_root
                )
            self.add_dist_point(
                self.s_tip_start, self.ds_tip_start, self.itip_start + 1
            )
            self.add_dist_point(
                1.0, self.ds_tip, self.ni_span + self.n_refined_tip + 1
            )

        if self.only_s:
            self.pf_out["s"] = distfunc(self.dist)
        else:
            self.pf_out = redistribute_planform(self.pf, self.dist)
