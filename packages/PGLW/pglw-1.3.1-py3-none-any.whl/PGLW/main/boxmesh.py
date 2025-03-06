import numpy as np
import sys

try:
    import matplotlib.pyplot as plt
except ImportError:
    print("matplotlib package not found, please install it")
from PGLW.main.distfunc import distfunc
from PGLW.main.domain import Domain, Block


class BoxMesh(Domain):
    """Python implementation of the boxf90_attr fortran code adapted from Clemens Zengler
    Stitched together from boxf90_attr, boxf90, PGL, and StaggerBcCyclic.

    # General
    Primary usage is for domain generation for precursors, but can also be used for any other
    block meshes. Only staggered option is precursor-specific.

    # Staggered
    When applying cyclic boundary conditions, staggered=True shifts the outlet block attributes
    relative to the inlet block attributes. Respective attributes must be set to 501 in
    the function arguments.
    Assumption: x -> flow direction
                y -> lateral direction
                z -> vertical direction
    """

    def __init__(
        self,
        n,
        size,
        shift,
        bc,
        dist=None,
        bsize=32,
        filename="grid.x3dunf",
        staggered=False,
        printscreen=True,
    ):
        """
        Parameters
        ----------
        n : list[int]
            Number of cells in x, y, z. Not used at the moment.
        size : list[float]
            Domain length in x, y z.
        shift : list[float]
            Offset in x, y, z.
        bc : list[int]
            Boundary conditions [x0,x1,y0,y1,z0,z1]
        dist : list[list]
            List containing the cell distributions in each dimension.
        bsize : int, optional
            Block size, by default 32
        filename : str, optional
            Name of grid, by default 'grid.x3dunf'
        staggered : bool or int, optional
            If True, cyclic BC remapping is used with 1 block shift.
            Default False means no shift. If set to non-zero integer
            then a shift size of this number of blocks is applied.
        printscreen:
            Print final grid parameters to screen similar to boxf90
        """
        Domain.__init__(self)
        self.bc = bc
        if dist is None:
            dist = [None, None, None]
        # Compute the distributions
        self.dists = [None] * 3
        for p in range(3):
            if dist[p] is not None:
                self.dists[p] = distfunc(dist[p])
            else:
                self.dists[p] = np.linspace(0, 1, n[p])
            self.dists[p] = self.dists[p] * size[p] + shift[p]
        self.bsize = bsize
        self.filename = filename
        self.staggered = staggered
        self.printscreen = printscreen

    def run(self):
        # Set up the block structure
        X, Y, Z = np.meshgrid(
            self.dists[0], self.dists[1], self.dists[2], indexing="ij"
        )

        # Set boundary conditions (we need to sort for the corner values!)
        attr = np.ones(np.shape(X))
        order = np.argsort(-np.asarray(self.bc))
        for i in range(6):
            if order[i] == 0:
                attr[0, :, :] = self.bc[order[i]]
            elif order[i] == 1:
                attr[-1, :, :] = self.bc[order[i]]
            elif order[i] == 2:
                attr[:, 0, :] = self.bc[order[i]]
            elif order[i] == 3:
                attr[:, -1, :] = self.bc[order[i]]
            elif order[i] == 4:
                attr[:, :, 0] = self.bc[order[i]]
            elif order[i] == 5:
                attr[:, :, -1] = self.bc[order[i]]

        # Find suitable block size (if the given one does not work)
        ni, nj, nk = X.shape
        rest = (
            np.mod(ni - 1, self.bsize)
            + np.mod(nj - 1, self.bsize)
            + np.mod(nk - 1, self.bsize)
        )
        while rest != 0 and self.bsize >= 3:
            print("Changing block size")
            print("Old block size: ", self.bsize)
            self.bsize = int(self.bsize / 2)
            rest = (
                np.mod(ni - 1, self.bsize)
                + np.mod(nj - 1, self.bsize)
                + np.mod(nk - 1, self.bsize)
            )
            print("New block size: ", self.bsize)

        nbi, nbj, nbk = (
            int((ni - 1) / self.bsize),
            int((nj - 1) / self.bsize),
            int((nk - 1) / self.bsize),
        )
        nbm = nbi * nbj * nbk

        # Print info about final structure
        if self.printscreen:
            # Computational resources
            n_cores_per_node = 32
            n_cells_per_core = 50000
            tot_cores = nbm * self.bsize**3 / n_cells_per_core
            tot_nodes = tot_cores / n_cores_per_node

            # Cell sizes
            self.delta = [0.0] * 3
            for p in range(3):
                self.delta[p] = self.dists[p][1:] - self.dists[p][:-1]
            print("*******************************************************")
            print("size of multidomaine blocks         : ", self.bsize)
            print("number of block in xi direction     : ", nbi)
            print("number of block in eta direction    : ", nbj)
            print("number of block in zeta direction   : ", nbk)
            print("total number of blocks              : ", nbm)
            print("number of recommended cores         : ", tot_cores)
            print("number of recommended nodes         : ", tot_nodes)
            print(
                "min/max cell sizes in x             :  {:.4f} {:.4f}".format(
                    self.delta[0].min(), self.delta[0].max()
                )
            )
            print(
                "min/max cell sizes in y             :  {:.4f} {:.4f}".format(
                    self.delta[1].min(), self.delta[1].max()
                )
            )
            print(
                "min/max cell sizes in z             :  {:.4f} {:.4f}".format(
                    self.delta[2].min(), self.delta[2].max()
                )
            )
            print("*******************************************************")

        # Generate blocks and domain (we add every block individually to keep track of the names!)
        for k in range(nbk):
            for j in range(nbj):
                for i in range(nbi):
                    start_i, end_i = (
                        i * self.bsize,
                        i * self.bsize + self.bsize + 1,
                    )
                    start_j, end_j = (
                        j * self.bsize,
                        j * self.bsize + self.bsize + 1,
                    )
                    start_k, end_k = (
                        k * self.bsize,
                        k * self.bsize + self.bsize + 1,
                    )

                    attr_i = attr[start_i:end_i, start_j:end_j, start_k:end_k]
                    X_i = X[start_i:end_i, start_j:end_j, start_k:end_k]
                    Y_i = Y[start_i:end_i, start_j:end_j, start_k:end_k]
                    Z_i = Z[start_i:end_i, start_j:end_j, start_k:end_k]

                    b_n = str(k) + "_" + str(j) + "_" + str(i)
                    b_i = Block(X_i, Y_i, Z_i, attr_i, name=b_n)
                    self.add_blocks(b_i)

        # Add shift (assume z-direction is ground and top)
        if int(self.staggered) != 0:
            if nbj > 96:
                print(
                    "ERROR: the number of blocks in y-dir is",
                    nbj,
                    "but cannot be more than 96 when staggered=True.",
                )
                sys.exit()
            for k in range(nbk):
                for j in range(nbj):
                    in_ind = nbj + 1 - j - 1
                    out_ind = ((nbj - j - int(self.staggered) - 1) % nbj) + 1
                    in_ind = 501 + in_ind
                    out_ind = 501 + out_ind
                    in_name = str(k) + "_" + str(j) + "_0"
                    out_name = str(k) + "_" + str(j) + "_" + str(int(nbi - 1))
                    self.blocks[in_name].scalars["attr"][0, :, :][
                        self.blocks[in_name].scalars["attr"][0, :, :] == 501
                    ] = in_ind
                    self.blocks[out_name].scalars["attr"][-1, :, :][
                        self.blocks[out_name].scalars["attr"][-1, :, :] == 501
                    ] = out_ind

        # Get requested file type and write file
        if self.filename is not None:
            filetype = self.filename.split(".")[-1]
            if filetype == "xyz":
                print("Writing plot3d file {:}".format(self.filename))
                self.write_plot3d(filename=self.filename, bcs="ellipsys")
            elif filetype == "x3dunf":
                print("Writing x3dunf file {:}".format(self.filename))
                self.write_x3dunf(filename=self.filename, add_ghosts=True)
            elif filetype == "x3d":
                print("Writing x3d file {:}".format(self.filename))
                with open(self.filename, "w") as f:
                    f.write(
                        "          {:d}          {:d}\n".format(
                            self.bsize, nbm
                        )
                    )
                    for bname in self.blocks.keys():
                        temp = np.empty(((self.bsize + 1) ** 3, 4))
                        temp[:, 0] = (
                            self.blocks[bname].scalars["attr"].flatten()
                        )
                        temp[:, 1] = self.blocks[bname].x.flatten()
                        temp[:, 2] = self.blocks[bname].y.flatten()
                        temp[:, 3] = self.blocks[bname].z.flatten()
                        np.savetxt(
                            f,
                            temp,
                            fmt="%d     %14.10f     %14.10f     %14.10f",
                        )
            else:
                raise ValueError(
                    "File type {:} not recognized. Available types are .xyz, .x3d, .x3dunf".format(
                        filetype
                    )
                )

    def write_dist(self):
        coords = ["x", "y", "z"]
        for p in range(3):
            if self.dists[p] is not None:
                f = open("%sDistribution.dat" % coords[p], "w")
                for i in range(1, len(self.dists[p])):
                    f.write(
                        "%20.12f%20.12f\n"
                        % (
                            self.dists[p][i],
                            self.dists[p][i] - self.dists[p][i - 1],
                        )
                    )
                f.close()

    def plot_dist(self, plot_name="dist.png"):
        fig, axs = plt.subplots(3, 1, gridspec_kw={"hspace": 0.5, "top": 0.95})
        xlabels = ["x [m]", "y [m]", "z [m]"]
        ylabels = ["dx [m]", "dy [m]", "dz [m]"]
        for p in range(3):
            axs[p].plot(self.dists[p][:-1], self.delta[p])
            axs[p].set_xlabel(xlabels[p])
            axs[p].set_ylabel(ylabels[p])
            axs[p].grid()
        fig.savefig(plot_name)


if __name__ == "__main__":
    n = [65, 65, 33]
    size = [100, 100, 100]
    shift = [0, 0, 0]
    bc = [501, 501, 599, 599, 601, 601]
    dist = [None, None, [[0, 0.001, 1], [1, -1, 33]]]
    boxmesh = BoxMesh(n, size, shift, bc, dist, 16, staggered=False)
    boxmesh.run()
    boxmesh.write_dist()
    boxmesh.plot_dist()
