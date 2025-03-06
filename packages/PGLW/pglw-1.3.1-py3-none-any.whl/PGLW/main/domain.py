"""
"""

import copy
import glob
import re
import warnings

import numpy as np

from PGLW.main.curve import Curve
from PGLW.main.distfunc import distfunc
from PGLW.main.geom_tools import *

deg2rad = np.pi / 180.0


def read_plot3d(filename, name="block", single_precision=False):
    """
    method to read plot3d multiblock grids

    parameters
    ----------
    filename: str
        name of the file to read
    name: str
        name given to the block
    single_precision: bool
        read file as single precision

    returns
    -------
    domain: object
        PGLW.main.domain.Domain object
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    with FortranFile(filename) as f:
        # read number of blocks
        nb = f.read_ints(dtype=np.int32)[0]
        bsizes = f.read_ints(dtype=np.int32)
        bsizes = bsizes.reshape(nb, 3)

        # create a domain object
        domain = Domain()

        # read per block data
        for n in range(nb):
            bname = name + "-%04d" % n
            ni, nj, nk = bsizes[n, :]
            # read x, y, z data
            if single_precision:
                xt = f.read_reals(dtype=np.float32)
            else:
                xt = f.read_reals()
            # split into blocks
            nt = ni * nj * nk
            xt = xt.reshape(3, nt)
            # split into x, y, z and reshape into ni, nj, nk
            x = xt[0, :].reshape(nk, nj, ni).swapaxes(0, 2)
            y = xt[1, :].reshape(nk, nj, ni).swapaxes(0, 2)
            z = xt[2, :].reshape(nk, nj, ni).swapaxes(0, 2)
            domain.add_blocks(Block(x, y, z, name=bname))
    return domain


def read_plot3d_f(d, filename, name="block", single_precision=False):
    """
    method to read plot3d multiblock function files

    Does this work?

    parameters
    ----------
    d: object
        PGLW.main.domain.Domain object
    filename: str
        file containg the data
    name: str
        name given to the block
    single_precision: bool
        read data as single precision

    returns
    -------
    domain: object
        PGLW.main.domain.Domain object
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    f = FortranFile(filename)

    # read number of blocks
    nb = f.read_ints(dtype=np.int32)[0]
    bsizes = f.read_ints(dtype=np.int32)
    bsizes = bsizes.reshape(nb, 4)

    # create a domain object

    data = []
    # read per block data
    for n in range(nb):
        bname = name + "-%04d" % n
        try:
            b = d.blocks[bname]
        except:
            raise RuntimeError("unknown block name %s" % bname)
        ni, nj, nk = bsizes[n, :3]
        arr = np.zeros((ni, nj, nk))
        # read x, y, z data
        if single_precision:
            xt = f.read_reals(dtype=np.float32)
        else:
            xt = f.read_reals()
        # split into blocks
        nt = ni * nj * nk
        # xt = xt.reshape(3, nt)
        # split into x, y, z and reshape into ni, nj, nk
        x = xt.reshape(nk, nj, ni, bsizes[n, -1]).swapaxes(0, 2)
        b.scalars["attr"] = x.copy()
    f.close()

    return d


def write_plot3d(
    domain,
    filename="out.xyz",
    bcs="wall",
    exclude_ghost=False,
    single_precision=False,
    binary=True,
):
    """
    write a domain to an unformatted plot3d file

    parameters
    ----------
    domain: object
        PGLW.main.domain.Domain object
    filename: str
        name of output file
    bcs: str
        | wall: assign all boundaries as wall
        | ellipsys: use this if the attr's have EllipSys format
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    if binary:
        with FortranFile(filename, mode="w") as f:
            f.write_record(np.int32(domain.nb))
            bsizes = []
            if exclude_ghost:
                for name, block in sorted(domain.blocks.items()):
                    bsizes.extend(
                        [
                            block.x.shape[0] - 2,
                            block.x.shape[1] - 2,
                            block.x.shape[2] - 2,
                        ]
                    )
            else:
                for name, block in sorted(domain.blocks.items()):
                    bsizes.extend(block.x.shape)

            f.write_record(np.array([nis for nis in bsizes], dtype=np.int32))

            for name, block in sorted(domain.blocks.items()):
                if exclude_ghost:
                    x = block.x[1:-1, 1:-1, 1:-1].flatten(order="F")
                    x = np.append(
                        x, block.y[1:-1, 1:-1, 1:-1].flatten(order="F")
                    )
                    x = np.append(
                        x, block.z[1:-1, 1:-1, 1:-1].flatten(order="F")
                    )
                else:
                    x = block.x.flatten(order="F")
                    x = np.append(x, block.y.flatten(order="F"))
                    x = np.append(x, block.z.flatten(order="F"))

                if single_precision:
                    x.dtype = np.float32
                    f.write_record(x)
                else:
                    f.write_record(x)
    else:
        with open(filename, "w") as f:
            # no. of blocks
            f.write(f"{domain.nb}\n")
            # write block size for each block
            for name, block in sorted(domain.blocks.items()):
                ni, nj, nk = block.x.shape
                f.write("{0:d} {1:d} {2:d}\n".format(ni, nk, nj))
            # assemble data
            for name, block in sorted(domain.blocks.items()):
                if exclude_ghost:
                    x = block.x[1:-1, 1:-1, 1:-1].flatten(order="F")
                    x = np.append(
                        x, block.y[1:-1, 1:-1, 1:-1].flatten(order="F")
                    )
                    x = np.append(
                        x, block.z[1:-1, 1:-1, 1:-1].flatten(order="F")
                    )
                else:
                    x = block.x.flatten(order="F")
                    x = np.append(x, block.y.flatten(order="F"))
                    x = np.append(x, block.z.flatten(order="F"))

                # Convert x to a formatted string and write it to the file
                x_str = " ".join(map(str, x))
                f.write(x_str + "\n")

    write_plot3d_bnd(domain, filename=filename, bcs=bcs)


def write_plot3d_bnd(dom, filename="out.xyz", bcs="wall"):
    """
    write the plot3d bnd file
    """
    if bcs == "wall":
        attr_dict = {1: 1}
    elif bcs == "ellipsys":
        attr_dict = {101: 1, 201: 2, 251: 3, 401: 4, 501: 5, 601: 6}

    ff = open(filename + ".fvbnd", "w")
    ff.write("FVBND 1 4\n")
    ff.write("wall\n")
    ff.write("inlet\n")
    ff.write("overset\n")
    ff.write("outlet\n")
    ff.write("periodic\n")
    ff.write("cyclic\n")
    ff.write("BOUNDARIES\n")
    for n, name in enumerate(sorted(dom.blocks.keys())):
        b = dom.blocks[name]

        for f in [1, 2]:
            istart = np.mod(f + 1, 2) * (b.ni - 1) + 1
            iend = np.mod(f + 1, 2) * (b.ni - 1) + 1
            jstart = 1
            jend = b.nj
            kstart = 1
            kend = b.nk
            attr = b.scalars["attr"][istart - 1, b.nj // 2, b.nk // 2]
            if attr in list(attr_dict.keys()):
                ff.write(
                    "%i %i %i %i %i %i %i %i F -1\n"
                    % (
                        attr_dict[attr],
                        n + 1,
                        istart,
                        iend,
                        jstart,
                        jend,
                        kstart,
                        kend,
                    )
                )
        for f in [3, 4]:
            jstart = np.mod(f + 1, 2) * (b.nj - 1) + 1
            jend = np.mod(f + 1, 2) * (b.nj - 1) + 1
            istart = 1
            iend = b.ni
            kstart = 1
            kend = b.nk
            attr = b.scalars["attr"][b.ni // 2, jstart - 1, b.nk // 2]
            if attr in list(attr_dict.keys()):
                ff.write(
                    "%i %i %i %i %i %i %i %i F -1\n"
                    % (
                        attr_dict[attr],
                        n + 1,
                        istart,
                        iend,
                        jstart,
                        jend,
                        kstart,
                        kend,
                    )
                )
        for f in [5, 6]:
            kstart = np.mod(f + 1, 2) * (b.nk - 1) + 1
            kend = np.mod(f + 1, 2) * (b.nk - 1) + 1
            istart = 1
            iend = b.ni
            jstart = 1
            jend = b.nj
            attr = b.scalars["attr"][b.ni // 2, b.nj // 2, kstart - 1]
            if attr in list(attr_dict.keys()):
                ff.write(
                    "%i %i %i %i %i %i %i %i F -1\n"
                    % (
                        attr_dict[attr],
                        n + 1,
                        istart,
                        iend,
                        jstart,
                        jend,
                        kstart,
                        kend,
                    )
                )

    ff.close()


def write_plot3d_f(
    domain, filename="out.f", exclude_ghost=False, single_precision=False
):
    """
    write a domain's attr to an unformatted plot3d file

    parameters
    ----------
    domain: object
        PGLW.main.domain.Domain object
    filename: str
        name of output file
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    b0 = domain.blocks[list(domain.blocks.keys())[0]]
    with open(filename[:-2] + ".nam", "w") as f:
        for name in b0.scalars.keys():
            f.write(name + "\n")

    # we assume all blocks to have the same number of scalars
    ns = len(b0.scalars)

    with FortranFile(filename, mode="w") as f:
        f.write_record(np.int32(domain.nb))
        bsizes = []
        if exclude_ghost:
            for name, block in sorted(domain.blocks.items()):
                bsizes.extend(
                    (block.x.shape[0], block.x.shape[1], block.x.shape[2], ns)
                )
        else:
            for name, block in sorted(domain.blocks.items()):
                bsizes.extend(
                    (block.x.shape[0], block.x.shape[1], block.x.shape[2], ns)
                )
        f.write_record(np.array([nis for nis in bsizes], dtype=np.int32))

        for name, block in sorted(domain.blocks.items()):
            fields = []
            for scalar, field in sorted(block.scalars.items()):
                if exclude_ghost:
                    fields.append(field[1:-1, 1:-1, 1:-1].flatten(order="F"))
                else:
                    fields.append(field.astype(float).flatten(order="F"))

            f.write_record(fields)


def readX2D(filename, name="block", nd=2, include_ghost=True, mglevel=0):
    """
    read a mesh file (X2D) created with basis2d

    parameters
    ----------
    filename: str
        name of file to read
    name: str
        name given to the block
    nd: int
        dimension of grid, 2 or 3
    include_ghost: bool
        flag for including the ghost cells in the grid

    returns
    -------
    domain: object
        PGLW.main.domain.Domain object
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    f = FortranFile(filename)

    # read number of blocks
    bsizes = np.zeros(5)
    bsize = bsizes[0] = f.read_ints(dtype=np.int32)[0]
    ni = bsize + 3
    nb = f.read_ints(dtype=np.int32)[0]
    dimInt = f.read_ints(dtype=np.int32)[0]
    mglev = 1
    for level in range(1, 6):
        if np.mod(bsizes[level - 1], 2) == 0 and bsizes[level - 1] > 2:
            bsizes[level] = bsizes[level - 1] // 2
            mglev += 1
    print("Grid info: ni = %i, nblock = %i, mglev = %i\n" % (bsize, nb, mglev))
    # create a domain object
    domain = Domain()
    attr = []
    x = []
    y = []
    z = []
    for level in range(mglev):
        attr.append([f.read_ints(dtype=np.int32) for i in range(nb)])
        x.append([f.read_reals() for i in range(nb)])
        y.append([f.read_reals() for i in range(nb)])
        if nd == 3:
            z.append([f.read_reals().T for i in range(nb)])

    if include_ghost:
        for n in range(nb):
            xx = np.array(x[mglevel][n]).reshape(ni, ni)
            yy = np.array(y[mglevel][n]).reshape(ni, ni)
            if nd == 3:
                zz = np.array(z[mglevel][n]).reshape(ni, ni)
            else:
                zz = np.zeros((ni, ni, 1))
            domain.add_blocks(Block(xx, yy, zz))
    else:
        for n in range(nb):
            bname = name + str(n)
            xx = np.array(x[mglevel][n]).reshape(ni, ni)[1:-1, 1:-1]
            yy = np.array(y[mglevel][n]).reshape(ni, ni)[1:-1, 1:-1]
            if nd == 3:
                zz = np.array(z[mglevel][n]).reshape(ni, ni)[1:-1, 1:-1]
            else:
                zz = np.zeros((bsize + 1, bsize + 1, 1))
            domain.add_blocks(Block(xx, yy, zz, name=bname))

    f.close()
    return domain


def write_x2d(
    domain,
    filename="grid.x2d",
    scale_factor=1.0,
    imin=0,
    imax=-1,
    zmin=-10000,
    zmax=10000,
    twoD=False,
):
    """
    Save a domain to the basis2d format

    parameters
    ----------
    filename: str
        name of the file
    scale_factor: float
        optional scaling factor
    imin: int
        optional min i index
    imax: int
        optional max i index
    zmin: float
        boundaries < zmin will be given attr=103
    zmax: float
        boundaries > zmax will be given attr=103
    """
    name, block = list(domain.blocks.items())[0]
    ni = block.ni

    def write_line(fid, attr, x, y, z=None):
        if z is None:
            fid.write(" %i   %24.18e   %24.18e\n" % (attr, x, y))
        else:
            fid.write(" %i   %24.18e   %24.18e   %24.18e\n" % (attr, x, y, z))

    fid = open(filename, "w")
    fid.write(" %i   %d\n" % (ni - 1, domain.nb))
    for name, dom in sorted(domain.blocks.items()):
        if [dom.ni, dom.nj] != [ni, ni]:
            raise RuntimeError(
                "block has wrong size. Expected [%i, %i], got [%i, %i]"
                % (ni, ni, dom.ni, dom.nj)
            )
        if imin > 0 or imax != -1:
            attr = dom.scalars["attr"][imin:imax, imin:imax, 0].flatten(
                order="F"
            )
            domX = scale_factor * dom.x[imin:imax, imin:imax, 0].flatten(
                order="F"
            )
            domY = scale_factor * dom.y[imin:imax, imin:imax, 0].flatten(
                order="F"
            )
            if twoD:
                for i in range(dom.x[imin:imax, imin:imax, 0].size):
                    write_line(fid, 1, domX[i], domY[i])
            else:
                domZ = scale_factor * dom.z[imin:imax, imin:imax, 0].flatten(
                    order="F"
                )
                for i in range(dom.x[imin:imax, imin:imax, 0].size):
                    write_line(fid, 1, domX[i], domY[i], z=domZ[i])
        else:
            attr = dom.scalars["attr"][:, :, 0].flatten(order="F")
            domX = scale_factor * dom.x[:, :, 0].flatten(order="F")
            domY = scale_factor * dom.y[:, :, 0].flatten(order="F")
            domZ = scale_factor * dom.z[:, :, 0].flatten(order="F")
            for i in range(dom.x[:, :, 0].size):
                if domZ[i] < zmin or domZ[i] > zmax:
                    write_line(fid, 103, domX[i], domY[i], z=domZ[i])
                else:
                    if twoD:
                        write_line(fid, attr[i], domX[i], domY[i])
                    else:
                        write_line(fid, attr[i], domX[i], domY[i], z=domZ[i])

    fid.close()


def read_x2d(filename):
    """
    read a Basis2D x2d formatted file

    parameters
    ----------
    filename: str
        name of the file to read
    """

    fid = open(filename, "r")
    t1, t2 = fid.readline().strip("\n").split()
    ni = int(t1)
    nblock = int(t2)
    data = np.loadtxt(fid)
    if data.shape[1] == 3:
        data = data[:, [1, 2]]
        data = data.reshape(ni + 1, ni + 1, nblock, 2, order="F")
        z = np.zeros((ni + 1, ni + 1))
        d = Domain()
        for n in range(nblock):
            b = Block(data[:, :, n, 0], data[:, :, n, 1], z[:, :])
            d.add_blocks(b)
    elif data.shape[1] == 4:
        data = data[:, [1, 2, 3]]
        data = data.reshape(ni + 1, ni + 1, nblock, 3, order="F")
        d = Domain()
        for n in range(nblock):
            b = Block(data[:, :, n, 0], data[:, :, n, 1], data[:, :, n, 2])
            d.add_blocks(b)
    return d


def read_DAT(filename):
    """
    read a HypGrid2D DAT formatted file

    parameters
    ----------
    filename: str
        name of the file to read
    """

    fid = open(filename, "r")
    t1, t2, t3, t4 = fid.readline().strip("\n").split()
    ni = int(t1)
    nj = int(t2)
    nblock = int(t3)
    data = np.loadtxt(fid)
    if data.shape[1] == 3:
        attr = data[:, 0]
        data = data[:, [1, 2]]
        attr = attr.reshape(ni, nj, nblock, order="F")
        data = data.reshape(ni, nj, nblock, 2, order="F")
        z = np.zeros((ni, nj))
        d = Domain()
        for n in range(nblock):
            b = Block(data[:, :, n, 0], data[:, :, n, 1], z[:, :])
            b.scalars["attr"][:, :, 0] = attr[:, :, n]
            d.add_blocks(b)
    elif data.shape[1] == 4:
        attr = data[:, 0]
        data = data[:, [1, 2, 3]]
        attr = attr.reshape(ni, nj, nblock, order="F")
        data = data.reshape(ni, nj, nblock, 3, order="F")
        d = Domain()
        for n in range(nblock):
            b = Block(data[:, :, n, 0], data[:, :, n, 1], data[:, :, n, 2])
            b.scalars["attr"][:, :, 0] = attr[:, :, n]
            d.add_blocks(b)
    return d


def read_x3dunf(filename, name="block", include_ghost=True):
    """
    read a mesh file (X3D) created with basis3d

    parameters
    ----------
    filename: str
        name of file to read
    name: str
        name given to the block
    include_ghost: bool
        include (possibly full of zeros) ghost cells

    returns
    -------
    domain: object
        PGLW.main.domain.Domain object
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    f = FortranFile(filename)

    # read number of blocks
    bsize = f.read_ints(dtype=np.int32)[0]
    ni = bsize + 3
    nb = f.read_ints(dtype=np.int32)[0]

    # create a domain object
    domain = Domain()

    attr = [f.read_ints(dtype=np.int32) for i in range(nb)]
    x = [f.read_reals() for i in range(nb)]
    y = [f.read_reals() for i in range(nb)]
    z = [f.read_reals() for i in range(nb)]

    for n in range(nb):
        bname = name + "-%04d" % n
        a = np.array(attr[n]).reshape(ni, ni, ni).T
        xx = np.array(x[n]).reshape(ni, ni, ni).T
        yy = np.array(y[n]).reshape(ni, ni, ni).T
        zz = np.array(z[n]).reshape(ni, ni, ni).T
        if not include_ghost:
            domain.add_blocks(
                Block(
                    xx[1:-1, 1:-1, 1:-1],
                    yy[1:-1, 1:-1, 1:-1],
                    zz[1:-1, 1:-1, 1:-1],
                    attr=a[1:-1, 1:-1, 1:-1],
                    name=bname,
                )
            )
        else:
            domain.add_blocks(Block(xx, yy, zz, attr=a, name=bname))

    f.close()
    return domain


def write_x3dunf(
    domain, filename="out.x3dunf", add_ghosts=False, single_precision=False
):
    """
    write a domain to file in the unformatted Basis3D format

    parameters
    ----------
    domain: object
        PGLW.main.domain.Domain object
    filename: str
        name of the file to be written
    add_ghosts: bool
        adds space for the ghost cells in the output array
    single_precision: bool
        write mesh as single precision
    """

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    name, block = list(domain.blocks.items())[0]
    if add_ghosts:
        bsize = block.ni - 1
    else:
        bsize = block.ni - 3

    try:
        from scipy.io import FortranFile
    except:
        raise ImportError("Install scipy: pip install scipy")

    f = FortranFile(filename, mode="w")
    f.write_record(bsize)
    f.write_record(domain.nb)

    for name, block in sorted(domain.blocks.items()):
        if add_ghosts:
            x = np.ones(
                (block.ni + 2, block.nj + 2, block.nk + 2), dtype=np.int32
            )
            x[1:-1, 1:-1, 1:-1] = block.scalars["attr"]
        else:
            x = block.scalars["attr"]
        f.write_record(x.flatten(order="F"))

    for name, block in sorted(domain.blocks.items()):
        if add_ghosts:
            x = np.ones((block.ni + 2, block.nj + 2, block.nk + 2))
            x[1:-1, 1:-1, 1:-1] = block.x
        else:
            x = block.x
        if single_precision:
            f.write_record(x.flatten(order="F").astype(np.float32))
        else:
            f.write_record(x.flatten(order="F"))

    for name, block in sorted(domain.blocks.items()):
        if add_ghosts:
            x = np.ones((block.ni + 2, block.nj + 2, block.nk + 2))
            x[1:-1, 1:-1, 1:-1] = block.y
        else:
            x = block.y
        if single_precision:
            f.write_record(x.flatten(order="F").astype(np.float32))
        else:
            f.write_record(x.flatten(order="F"))

    for name, block in sorted(domain.blocks.items()):
        if add_ghosts:
            x = np.ones((block.ni + 2, block.nj + 2, block.nk + 2))
            x[1:-1, 1:-1, 1:-1] = block.z
        else:
            x = block.z
        if single_precision:
            f.write_record(x.flatten(order="F").astype(np.float32))
        else:
            f.write_record(x.flatten(order="F"))
    f.close()


class Domain(object):
    """
    Domain object that holds a list of Block objects

    The class has methods to rotate the domain about the x, y, and z axes
    and plot the surface.
    """

    def __init__(self):
        self.groups = {}
        self.blocks = {}
        self.nb = 0
        self.con_eps = 1.0e-8

    def add_blocks(self, b, names=[]):
        if not isinstance(b, list):
            b = [b]
        for i, bl in enumerate(b):
            bl._n = self.nb + 1
            try:
                bl.name = self._check_name(names[i])
            except:
                bl.name = self._check_name(bl.name)
            self.blocks[bl.name] = bl
            self.nb += 1

    def rename_blocks(self, newnamebase):
        for name, block in self.blocks.items():
            del self.blocks[name]
            block.name = self._check_name(newnamebase)
            self.blocks[block.name] = block

    def add_group(self, group_name, blocks=[]):
        if blocks == []:
            blocks = list(self.blocks.keys())

        if not isinstance(blocks, list):
            blocks = list(blocks)

        self.groups[group_name] = blocks

    def add_domain(self, d, dname=""):

        self.add_blocks(
            list(d.blocks.values()),
            names=[dname + name for name in list(d.blocks.keys())],
        )

    def list_blocks(self):
        for i, name in enumerate(self.blocks.keys()):
            print(
                "Block %i: %s   (%i, %i, %i)"
                % (
                    i,
                    name,
                    self.blocks[name].ni,
                    self.blocks[name].nj,
                    self.blocks[name].nk,
                )
            )

    def get_blocksizes(self):
        nb = len(self.blocks.keys())
        isize = np.zeros(nb, dtype=int)
        jsize = np.zeros(nb, dtype=int)
        ksize = np.zeros(nb, dtype=int)
        for i, name in enumerate(self.blocks.keys()):
            isize[i] = self.blocks[name].ni
            jsize[i] = self.blocks[name].nj
            ksize[i] = self.blocks[name].nk
        # check if we're dealing with an EllipSys mesh
        if (
            list(isize).count(isize[0]) == len(isize)
            and list(jsize).count(jsize[0]) == len(jsize)
            and ksize[0] == 1
        ):
            return (isize[0], jsize[0], 1, nb)
        elif (
            list(isize).count(isize[0]) == len(isize)
            and list(jsize).count(jsize[0]) == len(jsize)
            and list(jsize).count(jsize[0]) == len(jsize)
        ):
            return (isize[0], jsize[0], ksize[0], nb)
        else:
            return (isize, jsize, ksize, nb)

    def rename_block(self, oldname, newname):
        self.blocks[newname] = self.blocks[oldname]
        self.blocks[newname].name = newname
        del self.blocks[oldname]

    def translate_x(self, x, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for n in blocks:
            b = self.blocks[n]
            b.translate_x(x)

    def translate_y(self, x, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for n in blocks:
            b = self.blocks[n]
            b.translate_y(x)

    def translate_z(self, x, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for n in blocks:
            b = self.blocks[n]
            b.translate_z(x)

    def scale(self, x, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for n in blocks:
            b = self.blocks[n]
            b.scale(x)

    def rotate_x(
        self,
        deg,
        blocks=None,
        groups=None,
        copy=False,
        center=np.array([0, 0, 0]),
    ):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for n in blocks:
            b = self.blocks[n]
            b.rotate_x(deg, center)

    def rotate_y(
        self,
        deg,
        blocks=None,
        groups=None,
        copy=False,
        center=np.array([0, 0, 0]),
    ):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for n in blocks:
            b = self.blocks[n]
            b.rotate_y(deg, center)

    def rotate_z(
        self,
        deg,
        blocks=None,
        groups=None,
        copy=False,
        center=np.array([0, 0, 0]),
    ):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for name in blocks:
            b = self.blocks[name]
            b.rotate_z(deg, center)

    # todo: should flipping be optional?

    def mirror_x(self, offset=0, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for name in blocks:
            b = self.blocks[name]
            b.mirror_x(offset)

    def mirror_y(self, offset=0, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for name in blocks:
            b = self.blocks[name]
            b.mirror_y(offset)

    def mirror_z(self, offset=0, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        for name in blocks:
            b = self.blocks[name]
            b.mirror_z(offset)

    def get_minmax(self, blocks=None, groups=None, copy=False):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)

        minmax = []
        for name in blocks:
            b = self.blocks[name]
            minmax.append(b.get_minmax())
        minmax = np.asarray(minmax)
        self.xmin = np.min(minmax[:, 0])
        self.xmax = np.max(minmax[:, 1])
        self.ymin = np.min(minmax[:, 2])
        self.ymax = np.max(minmax[:, 3])
        self.zmin = np.min(minmax[:, 4])
        self.zmax = np.max(minmax[:, 5])

    def set_scalar(self, blocks, name, vars):
        for block, var in zip(blocks, vars):
            self.blocks[block].set_scalar(name, var)

    def _set_blocks(self, blocks=None, copy=False):
        if blocks == None or blocks == []:
            blocks = list(self.blocks.keys())

        if not isinstance(blocks, list):
            raise ("blocks needs to be specified as a list")

        if copy:
            blocks = self.copy_blocks(blocks=blocks)

        return blocks

    def copy_blocks(self, blocks=None, groups=None, newnamebase=None):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(sorted(self.groups[g]))
        if blocks == []:
            blocks = list(sorted(self.blocks.keys()))

        new_blocks = []
        for name in sorted(blocks):
            self.nb += 1
            b = copy.deepcopy(self.blocks[name])
            if newnamebase:
                b.name = self._check_name(newnamebase)
            else:
                b.name = self._check_name(name + "-copy")
            self.blocks[b.name] = b
            new_blocks.append(b.name)

        return new_blocks

    def get_blocks(self, pattern):
        blocks = []
        names = self.blocks.keys()
        return glob.glob(names, pattern)

    def split_blocks(
        self,
        bsize=33,
        bsizei=None,
        bsizej=None,
        bsizek=None,
        blocks=None,
        groups=None,
    ):
        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks)

        for name in sorted(blocks):
            b = self.blocks[name]
            if bsizei is not None:
                newblocks = b.isplits(bsizei)
            elif bsizej is not None:
                newblocks = b.jsplits(bsizej)
            elif bsizek is not None:
                newblocks = b.ksplits(bsizek)
            else:
                newblocks = b.split(bsize)
            newnames = []
            if len(newblocks) == 0:
                print("failed splitting blocks")
            for i, newb in enumerate(newblocks):
                newname = b.name.split("-")[0] + "-split%04d" % i
                newb.name = self._check_name(newname)
                self.blocks[newb.name] = newb
                newnames.append(newb.name)
            del self.blocks[name]
            for gname, group in self.groups.items():
                if name in group:
                    l = list(set(group) - set([name]))
                    l.extend(newnames)
                    self.groups[gname] = l
        self.nb = len(list(self.blocks.keys()))

    def check_connectivity(self, con_eps=1.0e-8, verbose=True):
        """
        check which block edges are connected and return list with free edges
        verbose -- flag to print edge connection.
        verbose=True -> Information about all edges are printed
        verbose ="only free" -> Only information about free edges is printed
        """
        freeCons = []
        for name1, block1 in self.blocks.items():
            # D1 = self._block2arr(block1)
            for i in range(4):
                if block1.edgeCon[i][0] >= 0:
                    continue
                edge1 = block1.get_edge(i)
                for name2, block2 in self.blocks.items():
                    if name2 == name1:
                        continue
                    # D2 = self._block2arr(block2)
                    work = False
                    for j in range(4):
                        edge2 = block2.get_edge(j)
                        try:
                            eps = norm(edge1 - edge2)
                        except:
                            continue
                        if eps < con_eps:
                            block1.edgeCon[i] = [j, name2]
                            block2.edgeCon[j] = [i, name1]
                            block1.set_edge(i, edge2)
                            break
                        eps = norm(edge1 - edge2[::-1])
                        if eps < con_eps:
                            block1.edgeCon[i] = [j, name2]
                            block2.edgeCon[j] = [i, name1]
                            block1.set_edge(i, edge2[::-1])
                            break
                if block1.edgeCon[i][0] == -1:
                    freeCons.append(Curve(points=edge1))
        if verbose is True:
            self.print_connectivity()
        elif verbose == "only free":
            self.print_connectivity(only_free_edges=True)
        return freeCons

    def print_connectivity(self, only_free_edges=False):
        """
        Prints edge connections for all blocks in the domain
        only_free_edges -- If true only information about the free edges are printed
        """
        has_free_edges = False
        for name, block in self.blocks.items():
            if only_free_edges:
                for iblock, edgeCon in enumerate(block.edgeCon):
                    if edgeCon[0] == -1:
                        print(
                            "Block %s has a free edge at edge=%d"
                            % (name, iblock)
                        )
                        has_free_edges = True

                if has_free_edges is False:
                    print("Block %s has NO free edges" % name)
                has_free_edges = False
                print()

            else:
                print("Block: %s has the following edge connections" % name)
                for iblock, edgeCon in enumerate(block.edgeCon):
                    if edgeCon[0] == -1:
                        print("edge=%d is a free edge" % (iblock))
                    else:
                        print(
                            "edge=%d is connected to edge(%s)=%d"
                            % (iblock, edgeCon[1], edgeCon[0])
                        )
                print("\n")

    def _check_scalars(self, scalars):
        for name, scalar in scalars.items():
            assert len(scalar.shape) == 3

    def join_blocks(self, B1, B2, newname=None):
        """
        join two blocks, pop them and add the new one.

        this only operates on blocks with nk = 1
        """

        D1 = self._block2arr(self.blocks[B1])
        scalars1 = self.blocks[B1].scalars
        D2 = self._block2arr(self.blocks[B2])
        scalars2 = self.blocks[B2].scalars

        def run_con2(D1, scalars1, D2, scalars2):
            work, D3, scalars3 = self._match_blocks(D1, scalars1, D2, scalars2)
            if not work:
                work, D3, scalars3 = self._match_blocks(
                    D2, scalars2, D1, scalars1
                )
            return work, D3, scalars3

        def run_con(D1, scalars1, D2, scalars2):
            work, D3, scalars3 = run_con2(D1, scalars1, D2, scalars2)
            if not work:
                d2t, s2t = self._flip_block(D2, scalars2)
                work, D3, scalars3 = run_con2(D1, scalars1, d2t, s2t)
            return work, D3, scalars3

        for i in range(4):
            for j in range(4):
                D1t, a1t = self._rotate_dir(D1, scalars1, i)
                D2t, a2t = self._rotate_dir(D2, scalars2, j)
                work, D3, scalars3 = run_con(D1t, a1t, D2t, a2t)
                if work:
                    del self.blocks[B1]
                    del self.blocks[B2]
                    B = self._arr2block(D3)
                    B.scalars = scalars3
                    if newname is not None:
                        B.name = newname
                    else:
                        B.name = re.sub("\-joined$", "", B1) + "-joined"
                    self.blocks[B.name] = B
                    self.nb = len(list(self.blocks.keys()))
                    for gname, group in self.groups.items():
                        g = list(set(group) - set([B1]))
                        g = list(set(g) - set([B2]))
                        self.groups[gname] = g
                    return
        print("failed joining blocks", B1, B2)

    def flip_all(self, di=0):
        for name, b in self.blocks.items():
            b._flip_block(di=di)
            # b.transpose()
            # bb = self._block2arr(b)
            # bb = self._flip_block(bb)
            # bb = self._arr2block(bb)
            # bb.name = name
            # self.blocks[name] = bb

    def extrude(self, coord=None, nk=None, facx=None, facy=None, distz=None):
        for name, b in self.blocks.items():
            b.extrude(coord=coord, nk=nk, facx=facx, facy=facy, distz=distz)

    def revolve(self, ang0, ang1, center, ni):
        for name, b in self.blocks.iteritems():
            b.revolve(ang0, ang1, center, ni)

    def domain2basis2d(self, factor=1):
        sizes = self.get_blocksizes()
        if len(sizes) == 4:
            ni = (sizes[0] - 1) / factor + 3
            x = np.zeros((ni, ni, self.nb), order="F")
            y = np.zeros((ni, ni, self.nb), order="F")
            z = np.zeros((ni, ni, self.nb), order="F")
            attr = np.zeros((ni, ni, self.nb), dtype=int, order="F")
            # self.flip_all()
            for i, name in enumerate(np.sort(self.blocks.keys())):
                x[1:-1, 1:-1, i] = self.blocks[name].x[::factor, ::factor, 0]
                y[1:-1, 1:-1, i] = self.blocks[name].y[::factor, ::factor, 0]
                z[1:-1, 1:-1, i] = self.blocks[name].z[::factor, ::factor, 0]
                attr[1:-1, 1:-1, i] = self.blocks[name].scalars["attr"][
                    ::factor, ::factor, 0
                ]
            return x, y, z, attr

    def domain2basis3d(self, factor=1, add_ghost=False):
        if add_ghost:
            sli = slice(1, -1)
            bm = 1
        else:
            sli = slice(None, None)
            bm = 3

        sizes = self.get_blocksizes()
        if len(sizes) == 4:
            ni = int((sizes[0] - bm) / factor + 3)
            x = np.ones((ni, ni, ni, self.nb), order="F")
            y = np.ones((ni, ni, ni, self.nb), order="F")
            z = np.ones((ni, ni, ni, self.nb), order="F")
            attr = np.ones((ni, ni, ni, self.nb), dtype=np.int32, order="F")
            for i, (name, block) in enumerate(sorted(self.blocks.items())):
                x[sli, sli, sli, i] = block.x[::factor, ::factor, ::factor]
                y[sli, sli, sli, i] = block.y[::factor, ::factor, ::factor]
                z[sli, sli, sli, i] = block.z[::factor, ::factor, ::factor]
                attr[sli, sli, sli, i] = self.blocks[name].scalars["attr"][
                    ::factor, ::factor, ::factor
                ]
            return x, y, z, attr

    def _block2arr(self, B):
        B1 = np.empty((B.ni, B.nj, B.nk, 3), dtype=B.x.dtype)
        B1[:, :, 0, 0] = B.x[:, :, 0]
        B1[:, :, 0, 1] = B.y[:, :, 0]
        B1[:, :, 0, 2] = B.z[:, :, 0]
        return B1

    def _arr2block(self, B):
        return Block(B[:, :, :, 0], B[:, :, :, 1], B[:, :, :, 2])

    def _match_blocks(self, D1, scalars1, D2, scalars2):
        B2 = D2[-1, :, 0, :]
        B1 = D1[0, :, 0, :]
        if B1.size == B2.size:
            if norm(B1 - B2) < self.con_eps:
                # return the vertically stacked domains (in array[ni,nj,3] format)
                coords = np.vstack([D2[0:-1, :, :], D1])
                scalars = {}
                for name in scalars1.keys():
                    arr1 = scalars1[name]
                    arr2 = scalars2[name]
                    arr = np.vstack([arr2[0:-1, :, :], arr1])
                    scalars[name] = arr
                return True, coords, scalars

        return False, np.empty(D1.shape), {}

    def _rotate_dir(self, dom, scalars, n=0):
        def rotate1(dom, scalars):
            new_dom = dom[:, ::-1, :, :].copy()
            new_dom = new_dom.swapaxes(0, 1)
            new_scalars = copy.deepcopy(scalars)
            for name, field in scalars.items():
                field = field[:, ::-1, :].copy()
                new_scalars[name] = field.swapaxes(0, 1)

            return new_dom, new_scalars

        if n > 0:
            tmp_dom = dom
            tmp_scalars = scalars
            for i in range(n):
                tmp_dom, tmp_scalars = rotate1(tmp_dom, tmp_scalars)
            return tmp_dom, tmp_scalars
        else:
            return dom, scalars

    def _flip_block(self, dom, scalars, di=0):
        if di == 0:
            out = dom[::-1, :, :, :]
            new_scalars = {}
            for name, field in scalars.items():
                new_scalars[name] = field[::-1, :, :].copy()

        if di == 1:
            out = dom[:, ::-1, :, :]
            new_scalars = {}
            for name, field in scalars.items():
                new_scalars[name] = field[:, ::-1, :].copy()
        return out, new_scalars

    def plot_surface_grid(
        self,
        layer=0,
        mesh=True,
        edges=False,
        color=(1, 1, 1),
        scale=0.01,
        offscreen=False,
        name=False,
        blocks=[],
        groups=[],
    ):
        try:
            from mayavi import mlab
        except:
            raise ImportError("install mayavi to plot: conda install mayavi")

        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks)

        fig = mlab.figure(mlab, bgcolor=(1, 1, 1))
        for n in blocks:
            block = self.blocks[n]
            block.plot_surface_grid(
                layer=layer, color=color, edges=edges, name=name
            )

    def plot_surface(
        self,
        layer=0,
        color=(60 / 255.0, 90 / 255.0, 230 / 255.0),
        offscreen=False,
        size=(1280, 720),
        view=None,
        blocks=[],
        groups=[],
    ):
        try:
            from mayavi import mlab
        except:
            raise ImportError("install mayavi to plot: conda install mayavi")

        fig = mlab.figure(mlab, bgcolor=(1, 1, 1), size=size)

        if blocks == None:
            blocks = []
        if groups == None:
            groups = []

        if isinstance(groups, str):
            groups = [groups]
        for g in groups:
            blocks.extend(self.groups[g])
        blocks = self._set_blocks(blocks, copy)
        fig = mlab.figure(mlab, bgcolor=(1, 1, 1))
        for name in blocks:
            block = self.blocks[name]
            block.plot_surface(layer=layer, color=color, offscreen=offscreen)

    def savefig(self, filename, size=(1280, 720)):
        mlab.savefig(filename, size=size)

    def plot_normals(self):
        for name, block in self.blocks.items():
            block.plot_normals()

    def write_plot3d(self, filename, **kwargs):
        write_plot3d(self, filename, **kwargs)

    def write_x3dunf(
        self, filename="out.x3dunf", add_ghosts=True, single_precision=False
    ):
        write_x3dunf(
            domain=self,
            filename=filename,
            add_ghosts=add_ghosts,
            single_precision=single_precision,
        )

    def write_X3D(self):
        """
        Writes grid.X3D and grid.T3D file from a domain instance. (Requires pyellipsys to run PyBasis3D)
        """
        try:
            from pyellipsys.pybasis3d import PyBasis3D
        except ImportError:
            raise ImportError("pyellipsys needs to be installed")

        # Get block size and nblocks
        sizex, sizey, sizez, nblock = self.get_blocksizes()
        if not (sizex == sizey and sizex == sizez):
            raise ValueError(
                "size for all dimensions need to be the same (given: sizex=%d, sizey=%d, "
                "sizez=%d) use Domain.split_blocks(bsize=bsize) "
                "to make equal block sizes" % (sizex, sizey, sizez)
            )
        else:
            bsize = sizex - 1  # get_blocksizes includes ghostcells

        # Instanciate PyBasis3D (serial for now)
        bas3d = PyBasis3D()
        # Setting bsize and nblocks
        bas3d.set_blocksizes(bsize, nblock)
        # Setting volume array
        bas3d.initial_allocations()
        bas3d.set_volumemesh(*self.domain2basis3d(add_ghost=True))
        # Running basis 3D
        bas3d.run()
        # Writing grid.X3D and grid.T3D
        bas3d.writemesh()
        # Deallocate

    def _check_name(self, name, c=0):
        if name in list(self.blocks.keys()):
            c += 1
            newname = name.split("-")
            try:
                it = int(newname[-1])
                newname = newname[:-1]
            except:
                pass

            newname = "-".join(newname) + "-%04d" % c
            name = self._check_name(newname, c=c)
            return name
        else:
            return name

    def set_edge_attributes(self, attr):
        self.check_connectivity()
        for name, b in self.blocks.items():
            for i, edge in enumerate(b.edgeCon):
                if edge[0] < 0:
                    b.set_edge_attr(i, attr)


class Block(object):
    """
    Class that holds a single 3D grid with dimensions ni, nj, nk
    """

    def __init__(self, x, y, z, attr=None, name="block-0000", scalars={}):
        self.name = name
        self.edgeCon = [[-1, "free"]] * 4
        self.scalars = {}
        for name, value in scalars.items():
            self.scalars[name] = value
        shape = x.shape
        if len(shape) == 3:
            self.ni, self.nj, self.nk = shape
            self.x = x
            self.y = y
            self.z = z
        elif len(shape) == 2:
            self.ni, self.nj = shape
            self.nk = 1
            self.x = np.zeros([self.ni, self.nj, 1], dtype=x.dtype)
            self.y = np.zeros([self.ni, self.nj, 1], dtype=y.dtype)
            self.z = np.zeros([self.ni, self.nj, 1], dtype=z.dtype)
            self.x[:, :, 0] = x
            self.y[:, :, 0] = y
            self.z[:, :, 0] = z

        if not isinstance(attr, np.ndarray):
            attr = np.ones((self.ni, self.nj, self.nk), order="F", dtype=int)
            self.add_scalar("attr", attr)
        else:
            if len(attr.shape) == 2:
                self.scalars["attr"] = np.zeros(
                    [self.ni, self.nj, 1], dtype=z.dtype
                )
                self.scalars["attr"][:, :, 0] = attr
            else:
                self.scalars["attr"] = attr

    def add_scalar(self, name, var, overwrite=False):
        try:
            assert len(var.shape) == 3
        except:
            print("scalar array must be a 3D array")

        if not overwrite:
            if name in self.scalars:
                raise RuntimeError("Scalar %s is already defined")
        self.scalars[name] = var

    def set_scalar(self, name, var):
        self.add_scalar(name, var, overwrite=True)

    def copy(self):
        return copy.deepcopy(self)

    def translate_x(self, x):
        self.x += x

    def translate_y(self, y):
        self.y += y

    def translate_z(self, z):
        self.z += z

    def scale(self, fac):
        # if self.x.dtype == complex:
        #     fac = fac + 0j
        # if type(fac) == complex and self.x.dtype != complex:
        #     self.x = self.x.astype(np.complex)
        #     self.y = self.y.astype(np.complex)
        #     self.z = self.z.astype(np.complex)

        self.x = self.x * fac
        self.y = self.y * fac
        self.z = self.z * fac

    def rotate_x(self, deg, center=np.array([0, 0, 0])):
        self._rotate(deg, center, RotX)

    def rotate_y(self, deg, center=np.array([0, 0, 0])):
        self._rotate(deg, center, RotY)

    def rotate_z(self, deg, center=np.array([0, 0, 0])):
        self._rotate(deg, center, RotZ)

    def _rotate(self, deg, center, Rot):
        degrad = deg * deg2rad
        # xt = np.array([self.x.flatten(),self.y.flatten(),self.z.flatten()]).swapaxes(0,1)
        xt = np.zeros((self.ni * self.nj * self.nk, 3), dtype=self.x.dtype)
        xt[:, 0] = self.x.flatten(order="F")
        xt[:, 1] = self.y.flatten(order="F")
        xt[:, 2] = self.z.flatten(order="F")
        x = dotX(Rot(degrad), xt - center) + center
        # split into x, y, z and reshape into ni, nj, nk
        self.x = x[:, 0].reshape(self.nk, self.nj, self.ni).swapaxes(0, 2)
        self.y = x[:, 1].reshape(self.nk, self.nj, self.ni).swapaxes(0, 2)
        self.z = x[:, 2].reshape(self.nk, self.nj, self.ni).swapaxes(0, 2)

    def mirror_x(self, offset):
        bb = self._mirror(offset, 0)
        self.x = bb[:, :, :, 0]
        self._flip_block()

    def mirror_y(self, offset):
        bb = self._mirror(offset, 1)
        self.y = bb[:, :, :, 1]
        self._flip_block()

    def mirror_z(self, offset):
        bb = self._mirror(offset, 2)
        self.z = bb[:, :, :, 2]
        self._flip_block()

    def _mirror(self, offset, index):
        bb = self._block2arr()
        bb[:, :, :, index] = -bb[:, :, :, index] + offset * 2.0
        return bb

    def get_minmax(self):
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)
        self.ymin = np.min(self.y)
        self.ymax = np.max(self.y)
        self.zmin = np.min(self.z)
        self.zmax = np.max(self.z)
        return [
            self.xmin,
            self.xmax,
            self.ymin,
            self.ymax,
            self.zmin,
            self.zmax,
        ]

    def split(self, n=33):
        blocks = []
        if n > self.ni or n > self.nj:
            warnings.warn(
                "Trying to split with a base of %s a block that is only %sx%s."
                " Nothing done" % (n - 1, self.ni - 1, self.nj - 1),
                RuntimeWarning,
            )
            return []

        if self.nk == 1:
            if (self.ni - 1) % (n - 1) != 0 or (self.nj - 1) % (n - 1) != 0:
                raise ValueError(
                    "Requested block cannot be split with a base of %s,"
                    " since one/several dimensions are not divisible (current size: %sx%s)"
                    % (n - 1, self.ni - 1, self.nj - 1)
                )
            for i in range((self.ni - 1) // (n - 1)):
                for j in range((self.nj - 1) // (n - 1)):
                    block = Block(
                        self.x[
                            (n - 1) * i : (n - 1) * (i + 1) + 1,
                            (n - 1) * j : (n - 1) * (j + 1) + 1,
                            :,
                        ],
                        self.y[
                            (n - 1) * i : (n - 1) * (i + 1) + 1,
                            (n - 1) * j : (n - 1) * (j + 1) + 1,
                            :,
                        ],
                        self.z[
                            (n - 1) * i : (n - 1) * (i + 1) + 1,
                            (n - 1) * j : (n - 1) * (j + 1) + 1,
                            :,
                        ],
                        name=self.name,
                    )
                    for name, scalar in self.scalars.items():
                        block.scalars[name] = scalar[
                            (n - 1) * i : (n - 1) * (i + 1) + 1,
                            (n - 1) * j : (n - 1) * (j + 1) + 1,
                            :,
                        ]
                    blocks.append(block)
        else:
            if (
                (self.ni - 1) % (n - 1) != 0
                or (self.nj - 1) % (n - 1) != 0
                or (self.nk - 1) % (n - 1) != 0
            ):
                raise ValueError(
                    "Requested block cannot be split with a base of %s,"
                    " since one/several dimensions are not divisible (current size: %sx%sx%s)"
                    % (n - 1, self.ni - 1, self.nj - 1, self.nk - 1)
                )
            for i in range((self.ni - 1) // (n - 1)):
                for j in range((self.nj - 1) // (n - 1)):
                    for k in range((self.nk - 1) // (n - 1)):
                        block = Block(
                            self.x[
                                (n - 1) * i : (n - 1) * (i + 1) + 1,
                                (n - 1) * j : (n - 1) * (j + 1) + 1,
                                (n - 1) * k : (n - 1) * (k + 1) + 1,
                            ],
                            self.y[
                                (n - 1) * i : (n - 1) * (i + 1) + 1,
                                (n - 1) * j : (n - 1) * (j + 1) + 1,
                                (n - 1) * k : (n - 1) * (k + 1) + 1,
                            ],
                            self.z[
                                (n - 1) * i : (n - 1) * (i + 1) + 1,
                                (n - 1) * j : (n - 1) * (j + 1) + 1,
                                (n - 1) * k : (n - 1) * (k + 1) + 1,
                            ],
                            name=self.name,
                        )
                        for name, scalar in self.scalars.items():
                            block.scalars[name] = scalar[
                                (n - 1) * i : (n - 1) * (i + 1) + 1,
                                (n - 1) * j : (n - 1) * (j + 1) + 1,
                                (n - 1) * k : (n - 1) * (k + 1) + 1,
                            ]

                        blocks.append(block)
        return blocks

    def isplits(self, n=33):
        blocks = []
        if (self.ni - 1) % (n - 1) != 0:
            raise ValueError(
                "Requested block cannot be split with a base of %s,"
                " I dimension is not divisible (current size: %s)"
                % (n - 1, self.ni - 1)
            )
        for i in range((self.ni - 1) // (n - 1)):
            # for j in range((self.nj-1)/(n-1)):
            block = Block(
                self.x[(n - 1) * i : (n - 1) * (i + 1) + 1, :, :],
                self.y[(n - 1) * i : (n - 1) * (i + 1) + 1, :, :],
                self.z[(n - 1) * i : (n - 1) * (i + 1) + 1, :, :],
                name=self.name,
            )
            for name, scalar in self.scalars.items():
                block.scalars[name] = scalar[
                    (n - 1) * i : (n - 1) * (i + 1) + 1, :, :
                ]
            blocks.append(block)
        return blocks

    def jsplits(self, n=33):
        blocks = []
        if (self.nj - 1) % (n - 1) != 0:
            raise ValueError(
                "Requested block cannot be split with a base of %s,"
                " J dimension is not divisible (current size: %s)"
                % (n - 1, self.nj - 1)
            )
        for j in range((self.nj - 1) // (n - 1)):
            block = Block(
                self.x[:, (n - 1) * j : (n - 1) * (j + 1) + 1, :],
                self.y[:, (n - 1) * j : (n - 1) * (j + 1) + 1, :],
                self.z[:, (n - 1) * j : (n - 1) * (j + 1) + 1, :],
                name=self.name,
            )
            for name, scalar in self.scalars.items():
                block.scalars[name] = scalar[
                    :, (n - 1) * j : (n - 1) * (j + 1) + 1, :
                ]
            blocks.append(block)
        return blocks

    def ksplits(self, n=33):
        blocks = []
        if (self.nk - 1) % (n - 1) != 0:
            raise ValueError(
                "Requested block cannot be split with a base of %s,"
                " K dimension is not divisible (current size: %s)"
                % (n - 1, self.nk - 1)
            )
        for k in range((self.nk - 1) // (n - 1)):
            block = Block(
                self.x[:, :, (n - 1) * k : (n - 1) * (k + 1) + 1],
                self.y[:, :, (n - 1) * k : (n - 1) * (k + 1) + 1],
                self.z[:, :, (n - 1) * k : (n - 1) * (k + 1) + 1],
                name=self.name,
            )
            for name, scalar in self.scalars.items():
                block.scalars[name] = scalar[
                    :, :, (n - 1) * k : (n - 1) * (k + 1) + 1
                ]
            blocks.append(block)
        return blocks

    def isplit(self, n=33):
        blocks = []
        block = Block(
            self.x[:n, :, :],
            self.y[:n, :, :],
            self.z[:n, :, :],
            name=self.name,
        )
        for name, scalar in self.scalars.items():
            block.scalars[name] = scalar[:n, :, :]
        blocks.append(block)

        block = Block(
            self.x[n - 1 :, :, :],
            self.y[n - 1 :, :, :],
            self.z[n - 1 :, :, :],
            name=self.name,
        )
        for name, scalar in self.scalars.items():
            block.scalars[name] = scalar[n - 1 :, :, :]
        blocks.append(block)
        return blocks

    def jsplit(self, n=33):
        blocks = []
        block = Block(
            self.x[:, :n, :],
            self.y[:, :n, :],
            self.z[:, :n, :],
            name=self.name,
        )
        for name, scalar in self.scalars.items():
            block.scalars[name] = scalar[:, :n, :]
        blocks.append(block)

        block = Block(
            self.x[:, n - 1 :, :],
            self.y[:, n - 1 :, :],
            self.z[:, n - 1 :, :],
            name=self.name,
        )
        for name, scalar in self.scalars.items():
            block.scalars[name] = scalar[:, n - 1 :, :]
        blocks.append(block)

        return blocks

    def ksplit(self, n=33):
        blocks = []

        block = Block(
            self.x[:, :, :n],
            self.y[:, :, :n],
            self.z[:, :, :n],
            name=self.name,
        )
        for name, scalar in self.scalars.items():
            block.scalars[name] = scalar[:, :, :n]
        blocks.append(block)

        block = Block(
            self.x[:, :, n - 1 :],
            self.y[:, :, n - 1 :],
            self.z[:, :, n - 1 :],
            name=self.name,
        )
        for name, scalar in self.scalars.items():
            block.scalars[name] = scalar[:, :, n - 1 :]
        blocks.append(block)

        return blocks

    def roll(self, iroll, axis=0):
        x = np.zeros_like(self.x)
        x[:-1, :, :] = np.roll(self.x[:-1, :, :], iroll, axis=axis)
        x[-1, :, :] = x[0, :, :]
        self.x = x
        y = np.zeros_like(self.y)
        y[:-1, :, :] = np.roll(self.y[:-1, :, :], iroll, axis=axis)
        y[-1, :, :] = y[0, :, :]
        self.y = y
        z = np.zeros_like(self.y)
        z[:-1, :, :] = np.roll(self.z[:-1, :, :], iroll, axis=axis)
        z[-1, :, :] = z[0, :, :]
        self.z = z
        for name, scalar in self.scalars.items():
            attr = np.zeros_like(self.y)
            attr[:-1, :, :] = np.roll(scalar[:-1, :, :], iroll, axis=axis)
            attr[-1, :, :] = attr[0, :, :]
            self.scalars[name] = attr.copy()

    def _block2arr(self):
        B1 = np.empty((self.ni, self.nj, self.nk, 3), dtype=self.x.dtype)
        B1[:, :, :, 0] = self.x[:, :, :]
        B1[:, :, :, 1] = self.y[:, :, :]
        B1[:, :, :, 2] = self.z[:, :, :]
        return B1

    def _arr2block(self, B):
        return Block(B[:, :, :, 0], B[:, :, :, 1], B[:, :, :, 2])

    def get_edge(self, edge):
        D1 = self._block2arr()
        if edge == 0:
            points = D1[0, :, 0, :]
        if edge == 1:
            points = D1[-1, :, 0, :]
        if edge == 2:
            points = D1[:, 0, 0, :]
        if edge == 3:
            points = D1[:, -1, 0, :]
        return points

    def set_edge(self, edge, x):
        D1 = self._block2arr()
        if edge == 0:
            D1[0, :, 0, :] = x
        if edge == 1:
            D1[-1, :, 0, :] = x
        if edge == 2:
            D1[:, 0, 0, :] = x
        if edge == 3:
            D1[:, -1, 0, :] = x
        self.x = D1[:, :, :, 0]
        self.y = D1[:, :, :, 1]
        self.z = D1[:, :, :, 2]

    def get_edge_attr(self, edge):
        D1 = self.scalars["attr"]
        if edge == 0:
            points = D1[0, :, 0]
        if edge == 1:
            points = D1[-1, :, 0]
        if edge == 2:
            points = D1[:, 0, 0]
        if edge == 3:
            points = D1[:, -1, 0]
        return points

    def set_edge_attr(self, edge, x):
        D1 = self.scalars["attr"]
        if edge == 0:
            D1[0, :, 0] = x
        if edge == 1:
            D1[-1, :, 0] = x
        if edge == 2:
            D1[:, 0, 0] = x
        if edge == 3:
            D1[:, -1, 0] = x

    def _flip_block(self, di=0):
        D1 = self._block2arr()
        if di == 0:
            out = D1[::-1, :, :, :]
            for name, scalar in self.scalars.items():
                self.scalars[name] = scalar[::-1, :, :]
        if di == 1:
            out = D1[:, ::-1, :, :]
            for name, scalar in self.scalars.items():
                self.scalars[name] = scalar[:, ::-1, :]
        elif di == 2:
            out = D1[:, :, ::-1, :]
            for name, scalar in self.scalars.items():
                self.scalars[name] = scalar[:, :, ::-1]

        self.x = out[:, :, :, 0]
        self.y = out[:, :, :, 1]
        self.z = out[:, :, :, 2]

    def transpose(self, direction=(0, 1)):
        ni = self.nj
        nj = self.ni

        self.x = self.x.swapaxes(*direction)
        self.y = self.y.swapaxes(*direction)
        self.z = self.z.swapaxes(*direction)
        for name, var in self.scalars.items():
            self.scalars[name] = var.swapaxes(*direction)
        self.ni = ni
        self.nj = nj

    def extrude(self, coord=None, nk=None, facx=None, facy=None, distz=None):
        # Checking input
        if distz is None:
            raise ValueError("distz needs to be specified for extrude")
        elif len(distz) == 2 and isinstance(distz[0], (float, int)):
            distz = np.linspace(*distz, n=nk)
        elif isinstance(distz, list) and isinstance(distz[0], list):
            distz = distfunc(distz)

        if nk is None:
            nk = len(distz)
        elif len(distz) != nk:
            raise ValueError(
                "nk and len(distz) has to be the same (nk=%d, len(distz)=%d)"
                % (nk, len(distz))
            )

        if facx is None:
            facx = np.ones(nk)
        if facy is None:
            facy = np.ones(nk)

        # Initilizing array
        if self.ni == 1:
            direction = 0
            B = np.zeros((nk, self.nj, self.nk, 3))
        elif self.nj == 1:
            direction = 1
            B = np.zeros((self.ni, nk, self.nk, 3))
        elif self.nk == 1:
            direction = 2
            B = np.zeros((self.ni, self.nj, nk, 3))
        else:
            raise ValueError(
                "One of the dimensions needs to be 1 (ni=%d, nj=%d, nk=%d)"
                % (self.ni, self.nj, self.nk)
            )

        Borg = self._block2arr()

        for i in range(nk):
            B[:, :, i, 0] = Borg[:, :, 0, 0] * facx[i]
            B[:, :, i, 1] = Borg[:, :, 0, 1] * facy[i]
            B[:, :, i, 2] = Borg[:, :, 0, 2] + distz[i]

        Block.__init__(
            self, B[:, :, :, 0], B[:, :, :, 1], B[:, :, :, 2], name=self.name
        )

    def revolve(self, ang0, ang1, center, nk):
        B = np.zeros((self.ni, self.nj, nk, 3))

        Borg = self._block2arr()

        for i in range(nk):
            ang = ang0 + (ang1 - ang0) / float(nk - 1) * float(i)
            B[:, :, i, 0] = Borg[:, :, 0, 1] * np.sin(ang)
            B[:, :, i, 1] = Borg[:, :, 0, 1] * np.cos(ang)
            B[:, :, i, 2] = Borg[:, :, 0, 2]

        Block.__init__(
            self, B[:, :, :, 0], B[:, :, :, 1], B[:, :, :, 2], name=self.name
        )

    def plot_normals(self):
        b = self._block2arr()
        ip = self.ni // 2
        jp = self.nj // 2
        im = min(ip + 5, self.ni)
        jm = min(jp + 5, self.nj)
        v1 = b[ip, jp:jm, 0, :]
        v2 = b[ip:im, jp, 0, :]
        self.v1 = Curve(points=v1)
        self.v2 = Curve(points=v2)

        normal = np.cross(self.v1.dp[0], self.v2.dp[0])
        normal = (
            np.vstack([np.zeros(3), normal])
            * 0.5
            * (self.v1.smax + self.v2.smax)
        )
        normal += b[ip, jp, 0, :]
        self.normal = Curve(points=normal)

        self.v1.plot(color=(1, 0, 0))
        self.v2.plot(color=(0, 0, 1))
        self.normal.plot(color=(0, 1, 0))

    def plot_islice(self, islice, color=(0, 0, 0)):
        try:
            from mayavi import mlab
            from vtk import vtkStructuredGrid
        except:
            raise ImportError("install mayavi to plot: conda install mayavi")

        fig = mlab.figure(mlab, bgcolor=(1, 1, 1))
        xall = np.zeros((self.nj * self.nk, 3))
        xall[:, 0] = self.x[islice, :, :].swapaxes(0, 1).flatten()
        xall[:, 1] = self.y[islice, :, :].swapaxes(0, 1).flatten()
        xall[:, 2] = self.z[islice, :, :].swapaxes(0, 1).flatten()
        sgrid = vtkStructuredGrid(dimensions=(self.nj, self.nk, 1))
        sgrid.points = xall
        d = mlab.pipeline.add_dataset(sgrid)
        gx = mlab.pipeline.grid_plane(d, color=color, line_width=1.0)

    def plot_jslice(self, jslice, color=(0, 0, 0)):
        try:
            from mayavi import mlab
            from tvtk import tvtk
        except:
            raise ImportError("install mayavi to plot: conda install mayavi")

        fig = mlab.figure(mlab, bgcolor=(1, 1, 1))
        xall = np.zeros((self.ni * self.nk, 3))
        xall[:, 0] = self.x[:, jslice, :].swapaxes(0, 1).flatten()
        xall[:, 1] = self.y[:, jslice, :].swapaxes(0, 1).flatten()
        xall[:, 2] = self.z[:, jslice, :].swapaxes(0, 1).flatten()
        sgrid = tvtk.StructuredGrid(dimensions=(self.ni, self.nk, 1))
        sgrid.points = xall
        d = mlab.pipeline.add_dataset(sgrid)
        gx = mlab.pipeline.grid_plane(d, color=color, line_width=1.0)

    def plot_surface_grid(
        self,
        layer=0,
        mesh=True,
        edges=False,
        color=(1, 1, 1),
        scale=0.01,
        scalar=None,
        name=False,
    ):
        # try:
        from mayavi import mlab
        from tvtk.api import tvtk

        # except:
        #     raise ImportError("install mayavi to plot: conda install mayavi")

        fig = mlab.figure(mlab, bgcolor=(1, 1, 1))
        xall = np.zeros((self.ni * self.nj, 3))
        xall[:, 0] = self.x[:, :, layer].swapaxes(0, 1).flatten().real
        xall[:, 1] = self.y[:, :, layer].swapaxes(0, 1).flatten().real
        xall[:, 2] = self.z[:, :, layer].swapaxes(0, 1).flatten().real
        sgrid = tvtk.StructuredGrid(dimensions=(self.ni, self.nj, 1))
        sgrid.points = xall
        d = mlab.pipeline.add_dataset(sgrid)
        gx = mlab.pipeline.grid_plane(d, color=(0, 0, 0), line_width=1.0)
        if scalar is not None:
            surf = mlab.mesh(
                self.x[:, :, layer].real,
                self.y[:, :, layer].real,
                self.z[:, :, layer].real,
                scalars=scalar,
            )
        else:
            surf = mlab.mesh(
                self.x[:, :, layer].real,
                self.y[:, :, layer].real,
                self.z[:, :, layer].real,
                color=color,
            )
            # ,self.z[:,:,layer].real,scalars=self.x[:,:,layer].imag)
        if edges:
            mlab.plot3d(
                self.x[:, 0, layer].real,
                self.y[:, 0, layer].real,
                self.z[:, 0, layer].real,
                tube_radius=None,
                color=(0, 0, 1),
            )
            mlab.plot3d(
                self.x[:, -1, layer].real,
                self.y[:, -1, layer].real,
                self.z[:, -1, layer].real,
                tube_radius=None,
                color=(0, 0, 1),
            )
            mlab.plot3d(
                self.x[0, :, layer].real,
                self.y[0, :, layer].real,
                self.z[0, :, layer].real,
                tube_radius=None,
                color=(1, 0, 0),
            )
            mlab.plot3d(
                self.x[-1, :, layer].real,
                self.y[-1, :, layer].real,
                self.z[-1, :, layer].real,
                tube_radius=None,
                color=(1, 0, 0),
            )
        if name:
            pos = np.array(
                [
                    self.x[:, :, layer].mean(),
                    self.y[:, :, layer].mean(),
                    self.z[:, :, layer].mean(),
                ]
            ).real
            dx = self.x[:, :, layer].max() - self.x[:, :, layer].min()
            dy = self.y[:, :, layer].max() - self.y[:, :, layer].min()
            dz = self.z[:, :, layer].max() - self.z[:, :, layer].min()
            maxd = np.max([dx, dy, dz]).real
            width = np.min(
                np.max(0.1 * maxd, len(self.name) * 0.005 * maxd), 0.05
            )
            mlab.text3d(
                pos[0], pos[1], pos[2], self.name, scale=width, color=(1, 0, 0)
            )

    def plot_surface(
        self,
        layer=0,
        color=(60 / 255.0, 90 / 255.0, 230 / 255.0),
        offscreen=False,
    ):
        try:
            from mayavi import mlab
        except:
            raise ImportError("install mayavi to plot: conda install mayavi")

        fig = mlab.figure(mlab, bgcolor=(1, 1, 1))
        surf = mlab.mesh(
            self.x[:, :, layer],
            self.y[:, :, layer],
            self.z[:, :, layer],
            color=color,
            figure=fig,
        )


def read_ascii_grid(name):
    """read blade coordinates written in flattened ascii"""

    x = np.loadtxt(name + "_X.dat")
    y = np.loadtxt(name + "_Y.dat")
    z = np.loadtxt(name + "_Z.dat")

    b = Block(x, y, z)
    d = Domain()
    d.add_blocks(b)
    return d
