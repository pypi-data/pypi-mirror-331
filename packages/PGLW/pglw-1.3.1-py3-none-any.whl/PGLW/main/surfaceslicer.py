#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 11:14:23 2018

@author: antariksh
"""
import time

import numpy as np
from scipy.interpolate import InterpolatedUnivariateSpline
from scipy.sparse import coo_matrix

from PGLW.main.distfunc import distfunc
from PGLW.main.domain import Block, Domain
from PGLW.main.geom_tools import discrete_length, surface_normal


class SlicedLoftedSurface(object):
    """
    Slices the generated lofted blade surface in parallel Z = 0 planes in the
    radial direction (ie along the Z-axis) from the blade root.

    The number of required spanwise and chordwise sections can be specified.
    It is reccomended that the required spanwise and chordwise sections be less
    than or equal to that of the lofted blade surface.

    Parameters
    ----------
    surface: ndarray
        The lofted blade surface as input having shape (chord_sections,
        span_sections, 3)
    ni_span : int
        The required spanwise sections which are less than or equal to the
        spanwise sections of the input surface
    ni_slice: int
        The number of points on the required slice. Or can be also regarded as
        the number of chordwise sections, which are less than or equal to that
        of the input surface.
    alpha_tol: float
        Tolerance for the minimum achievable value of the relaxation factor in
        the newton iteration.
    tol: float
        Tolerance for the residual of the newton iteration marking the
        attainment of the desired solution.
    include_tip: bool
        Flag if True includes the end-point in the radial direction
        representing the tip of the blade.
    blade_length: float
        The radial blade length in [m].
    span_low: int
        Optional argument for the spanwise section from which the slicing
        should begin. Default value is 0.
    span_high: int
        Optional argument for the spanwise section until which the slicing
        should end. Default value is Ns ie the required span locations.

    dist: list
        Optional argument for list of control points with the form

        | [[s0, ds0, n0], [s1, ds1, n1], ... [s<n>, ds<n>, n<n>]]

        | where

            | s<n> is the curve fraction at each control point,
            | ds<n> is the cell size at each control point,
            | n<n> is the cell count at each control point.
    s: array
        optional normalized distribution of blade.

    Returns
    -------
    sliced_surface: ndarray
        The sliced blade surface in parallel Z=0 planes of the shape:
        (chord_sections, span_sections, 3)

    """

    def __init__(self, **kwargs):
        self.surface = np.array([])
        self.ni_span = 100  # spanwise sections
        self.ni_slice = 100  # chordwise sections
        self.tol = 1.0e-5  # tolerance for residual in [m]
        self.include_tip = True  # flag for including tip
        self.blade_length = 1.0  # blade length
        self.alpha_tol = 1.0e-6  # Optional : tolerance for min. alpha
        self.span_low = 0  # Optional: starting span section for slicing
        self.span_high = 0  # optional: end span section for slicing
        self.dist = np.array([])  # Optional
        self.s = None  # Optional

        for (
            k,
            w,
        ) in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, w)

        self.sliced_surface = np.array([])
        self.flag_open = False
        self.perturb = 1.0e-5  # open the trailing edge
        self.close_surface = False  # Optional: flag to close the surface
        self.verbose = True

    def update(self):
        """
        Generates the final sliced surface.

        """
        # record the start time
        t0 = time.time()
        # call the main function
        self.main()

        t1 = time.time()
        t_elapsed = t1 - t0

        print(
            "\nGeometry built from Z = %3.4f m to Z = %3.4f m \n"
            % (self.zc_vec[self.span_low], self.zc_vec[self.span_high - 1])
        )
        print("Time taken = %3.4f s \n" % t_elapsed)

        if self.delspan_ind and self.verbose:
            print("Interpolated spanwise sections:\n")
            for i, e in enumerate(self.delspan_ind):
                print(
                    "%i) Section %i at Z = %3.4f m\n"
                    % (i + 1, e, self.zc_vec[e])
                )

    def main(self):
        """
        Calls the relevant methods to generate the sliced surface.

        """
        # -----------------------Initialization of class variables--------------
        # required spanwise sections
        Ns = int(self.ni_span)
        # set the span_high and span_low
        span_low = min(max(int(self.span_low), 0), Ns - 1)
        span_high = int(self.span_high)
        # check for span_high greater than the required sections
        if (span_high > Ns) or (span_high == 0):
            span_high = Ns

        # required points on the slice
        n_points = int(self.ni_slice)
        # blade length
        blade_length = self.blade_length
        # -------------------------------------------------------------------
        # --------------------------------------------------------------------
        # pre-process
        surface_orig = self._preprocess(self.surface)
        # scale surface by blade_length
        surface_orig *= blade_length
        # generate the Z plane position vector
        self._span_dist()
        zc_vec = self.zc_vec
        # initialize the array for the final surface being generated
        surface_new = np.zeros((Ns, n_points, 3), dtype=float)
        # initialize the initial state vector--> S_i, T_i, S_(i+1), T_(i+1)
        Pk_in = np.zeros(2 * n_points + 1, dtype=float)
        # initialize the intended S points indices in state vector
        ind_sin = np.arange(0, 2 * n_points, 2)
        # initialize the intended T points indices in state vector
        ind_tin = np.arange(1, 2 * n_points, 2)
        # -------------------------------------------------------------------
        # ------------------------------------------------------------------
        # spanwise sections in original grid
        Ns_orig = surface_orig.shape[0]
        # chordwise sections in original grid
        Nc_orig = surface_orig.shape[1]
        # generate the extended parametric grid and the corresponding surface
        grid_s, grid_t, surface_ext = self._extend_grid(surface_orig)
        # ------------------------------------------------------------------
        # -------initialize list and arrays to store state data of iterations---
        count_store = np.zeros(
            Ns, dtype=int
        )  # stores the iterations per section
        # list to store the state (S,T) data for each section and iteration
        state_store = []
        # sore the span index for uncoverged sections
        delspan_ind = []
        # -------------------------------------------------------------------
        # initialize the intended initial S points on slice
        sin = np.linspace(0, Ns_orig - 1, Ns, endpoint=True)
        # initialize the intended initial T points on slice
        tin = np.linspace(0, Nc_orig - 1, n_points, endpoint=True)
        # generate the intial surface with points closely arranged to z-zc=0 planes
        surface_in, param_map_in = self._search_plane(
            sin, tin, Ns, n_points, surface_ext, zc_vec
        )
        #
        for i in range(span_low, span_high):
            # flag for exiting the while loop
            exit_flag = 1

            # inititalize the list to store state at each iteration
            Pk_store = []

            # store initial zc
            zc = zc_vec[i]

            # store the current span value
            Pk_in[ind_sin] = param_map_in[i, :, 0]
            # store the slice t-value
            Pk_in[ind_tin] = param_map_in[i, :, 1]
            # calculate the distances in the initial guess
            D_in = discrete_length(
                surface_in[i, :, 0], surface_in[i, :, 1], surface_in[i, :, 2]
            )

            # calculate the initial constant distance
            dc_in = np.sum(D_in) / (n_points - 1)

            # initial guess for dc
            Pk_in[-1] = dc_in

            # initial guess for each span-wise section
            Pk = Pk_in

            # store the initial guess of state
            Pk_store.append(Pk)

            # initialize while loop counter
            count = 0
            # initialize the Residual norm
            R_norm_prev = 1
            # set the value of alpha
            # execute the Newton - iteration
            while exit_flag == 1:
                # store s and t
                S = Pk[ind_sin]
                T = Pk[ind_tin]
                # adjust for boundary correction in t
                # S, T = boundary_correction(S, T, Ns_orig, Nc_orig)
                # interpolate on the parametric space of the original fine grid
                Q, grid_map, val_map = self.bilinear_surface(
                    surface_ext, grid_s, grid_t, S, T
                )

                # calculate the distance between consecutive points
                D = discrete_length(Q[:, 0], Q[:, 1], Q[:, 2])

                # size of D vector (if flag = True, then n_D = n_points)
                n_D = D.shape[0]

                # jacobian as a sparse matrix for Q-->(x,y,z) wrt P-->(s,t) of size 3Nx2N
                jac_qp, _, _, _, _, dZds, dZdt = self._jacobian_Q(
                    S, T, grid_map, val_map
                )

                # jacobian as a sparse matrix for D-->(di) wrt Q-->(x,y,z) of size (N-1)x3N
                jac_dq = self._jacobian_D(Q, D, n_D, n_points)

                # jacobian as a sparse matrix for D-->(di) wrt P-->(s,t) of size (N-1)x2N
                jac_dp = jac_dq * jac_qp

                # construct the final jacobian matrix of order (2N+1)x(2N+1) with
                # d-dc, z-zc, t-tc partials
                jac_main = self._jacobian_main(
                    dZds, dZdt, jac_dp, n_points, n_D
                )

                # update dc
                dc = Pk[-1]

                # construct the residual vector
                R = self._build_residual(T, Q, D, zc, dc, tin, n_D, n_points)
                # take max of residual
                R_max = np.max(np.abs(R))

                # check to exit newton iteration
                if R_max < self.tol:
                    # set exit flag as False
                    exit_flag = 0
                    # store the last Q(x,y,z) points as the final section
                    surface_new[i, :, 0] = Q[:, 0]
                    surface_new[i, :, 1] = Q[:, 1]
                    surface_new[i, :, 2] = Q[:, 2]
                    break

                # obtain the updated state and status of iteration health
                (
                    Pk,
                    alpha,
                    R_norm,
                    delta_norm,
                    jac_main_cond,
                ) = self._newton_iteration(Pk, jac_main, R, Nc_orig, n_points)
                if self.verbose:
                    # print the health of the iteration
                    print(
                        "------------------------------------------------------"
                    )
                    print(
                        "\n Span location: S = %i, radius = %3.4f m\n"
                        % (i, zc)
                    )
                    print(
                        "\n Iteration = %i, dc = %3.6f m, Main jac cond = %e"
                        % (count, dc, jac_main_cond)
                    )
                    print(
                        "\n Residual : R_max = %3.7f\n"
                        "            R_norm = %3.7f\n"
                        "            R_new/R_prev = %3.5f \n"
                        % (R_max, R_norm, R_norm / R_norm_prev)
                    )
                    print("\n Relaxation factor : alpha = %3.7f \n" % (alpha))
                    print(
                        "\n Delta vector : delta_norm= %3.7f \n" % (delta_norm)
                    )
                    print(
                        "------------------------------------------------------"
                    )

                # increase count
                count += 1
                # store the current norm of R
                R_norm_prev = R_norm
                # store the state
                Pk_store.append(Pk)

                # escape clause for very low alphas and oscillating sections
                if alpha < self.alpha_tol or count > 1e3:
                    # escape the section
                    delspan_ind.append(i)
                    if self.verbose:
                        # print
                        print(
                            "\n\n Skipping section %i, radius = %3.2f\n\n"
                            % (i, zc)
                        )
                    # time.sleep(0.1)
                    # set exit flag as False
                    exit_flag = 0

            # store the count every iteration
            count_store[i] = count
            # store the states per section
            state_store.append(Pk_store)

        # interpolated across the missing surfaces

        if delspan_ind:
            # get the concatenated surface
            surface_concat = self._concat_surface(surface_new, delspan_ind)
        # the end missing surfaces near the tip are currently extruded
        for i in delspan_ind:
            surface_new[i, :, :] = self._interp_surface(
                surface_concat, zc_vec[i], i
            )

        # store the new surface
        self.sliced_surface = self._postprocess(surface_new)
        self.domain = Domain()
        self.domain.add_blocks(
            Block(
                self.sliced_surface[:, :, 0],  # x
                self.sliced_surface[:, :, 1],  # y
                self.sliced_surface[:, :, 2],
            )
        )  # z
        # store the S,T parametric spaces
        self.state_store = state_store
        # store the interpolated spanwise section
        self.delspan_ind = delspan_ind

    def _span_dist(self):
        """
        Obtain the spanwise distribution according to the required spanwise
        points.

        """
        if len(self.dist) > 0:
            zc_vec = distfunc(self.dist)
        elif isinstance(self.s, np.ndarray):
            zc_vec = self.s
        else:
            zc_vec = np.linspace(0, 1, self.ni_span, endpoint=self.include_tip)

        # for length of distribtuion either less or more than required span sec
        if zc_vec.shape[0] is not self.ni_span:
            import warnings

            warnings.warn(
                "Spanwise discretization not equal to the required."
                " Re-interpolating to match required discretization",
                RuntimeWarning,
            )
            # interp1D functions
            f = InterpolatedUnivariateSpline(
                np.linspace(0, 1, zc_vec.shape[0]), zc_vec, k=1
            )
            zc_vec = f(np.linspace(0, 1, self.ni_span))

        # multiply by blade length
        zc_vec *= self.blade_length
        # store as class variable
        self.zc_vec = zc_vec

    def _reshape(self, surface_tmp):
        """
        Reshape the surface array from shape (M, N, 3) to (N, M, 3).

        Parameters
        ----------
        surface_tmp: ndarray
            Numpy array of shape (M, N, 3)

        Returns
        -------
        surface: ndarray
            Numpy array of shape (N, M, 3)
        """
        # restructure it from [M, N, 3] to [N, M, 3]
        M = surface_tmp.shape[0]
        N = surface_tmp.shape[1]
        # intialize surface array
        surface = np.zeros((N, M, 3), dtype=float)
        for i in range(N):
            surface[i, :, 0] = surface_tmp[:, i, 0]
            surface[i, :, 1] = surface_tmp[:, i, 1]
            surface[i, :, 2] = surface_tmp[:, i, 2]
        # return the surface
        return surface

    def _extend_grid(self, surface_orig, flag=False):
        """
        The grid is extended by the extrapolated value of z_root and z_tip
        to the left of the root and right of the tip respectively.
        The extension is by one span location in either direction
        a) root extension: blade is extrapolated
        b) tip extension: blade is protruded along the normal.

        Parameters
        ----------
        surface_orig: ndarray
            Numpy array of shape (span_sections, chord_sections, 3)

        Returns
        -------
        grid_sext: ndarray
            Meshgrid of the S, T parametric space

        grid_text: ndarray
            Meshgrid of the S, T parametric space

        surface_ext: ndarray
            Extend lofted blade surface of shape (span_sections+2,
            chord_Sections, 3)

        """
        # spanwise sections in the imported surface
        Ns_orig = surface_orig.shape[0]
        # chordwise sections in the imported surface
        Nc_orig = surface_orig.shape[1]
        # S original
        S_orig = np.arange(0, Ns_orig)
        # generate the extended grid
        grid_sext, grid_text = np.mgrid[-1 : Ns_orig + 1, 0:Nc_orig]
        # extend S
        S_ext = grid_sext[:, 0]
        # extend the surface accordingly
        Ns_ext = grid_sext.shape[0]
        Nc_ext = grid_text.shape[1]
        surface_ext = np.zeros((Ns_ext, Nc_ext, 3), dtype=float)

        # assign the original surface for S,T: ie S-->[0, Ns-1] and T-->[0, Nc-1]
        surface_ext[1 : Ns_orig + 1, :, 0] = surface_orig[:, :, 0]  # X
        surface_ext[1 : Ns_orig + 1, :, 1] = surface_orig[:, :, 1]  # Y
        surface_ext[1 : Ns_orig + 1, :, 2] = surface_orig[:, :, 2]  # Z

        # extrapolate the root by 1 section using linear interpolation
        ind = np.zeros(3, dtype=int)
        ind[0] = S_orig[2]
        ind[1] = S_orig[1]
        ind[2] = S_orig[0]

        # extrapolate
        Xroot, Yroot, Zroot = self._extrapolate_surface(
            S_ext, surface_orig, ind
        )

        # build the extrapolated surface at the root
        surface_ext[0, :, 0] = Xroot
        surface_ext[0, :, 1] = Yroot
        surface_ext[0, :, 2] = Zroot

        # extrude the tip
        ind[0] = S_orig[Ns_orig - 3]
        ind[1] = S_orig[Ns_orig - 2]
        ind[2] = S_orig[Ns_orig - 1]

        # obtain the normal vector for the tip surface
        norm = surface_normal(surface_orig[Ns_orig - 1, :, :])

        # check the z-direction of the norm and appropriately reverse orientation
        if norm[2] < 0:
            norm *= -1

        # get the distances of each point on tip to corr. point on prev. section
        ln = np.sqrt(
            np.power(
                surface_orig[Ns_orig - 1, :, 0]
                - surface_orig[Ns_orig - 2, :, 0],
                2,
            )
            + np.power(
                surface_orig[Ns_orig - 1, :, 1]
                - surface_orig[Ns_orig - 2, :, 1],
                2,
            )
            + np.power(
                surface_orig[Ns_orig - 1, :, 2]
                - surface_orig[Ns_orig - 2, :, 2],
                2,
            )
        )

        # construct the extension vector
        ln_vec = np.mean(ln) * norm

        for i in range(Nc_orig):
            # construct the extended tip
            surface_ext[Ns_ext - 1, i, :] = (
                surface_orig[Ns_orig - 1, i, :] + ln_vec
            )

        if flag:
            grid_sext, grid_text = np.mgrid[0:Ns_orig, 0:Nc_orig]
            surface_ext = surface_orig

        return grid_sext, grid_text, surface_ext

    def _extrapolate_surface(self, S, surface, ind):
        """
        Linearly extrapolates the surface near the tip and the root

        """
        # ind0 = ind[0] # index of the third span from the edge
        ind1 = ind[1]  # index of the second span from edge
        ind2 = ind[2]  # index of last span
        # define X1
        X1 = surface[ind1, :, 0]
        # X2
        X2 = surface[ind2, :, 0]
        # Y1
        Y1 = surface[ind1, :, 1]
        # Y2
        Y2 = surface[ind2, :, 1]
        # Z1
        Z1 = surface[ind1, :, 2]
        # Z2
        Z2 = surface[ind2, :, 2]
        # distance l2
        l2 = np.sqrt(
            np.power(X2 - X1, 2) + np.power(Y2 - Y1, 2) + np.power(Z2 - Z1, 2)
        )
        # calculate unit direction vectors of l2
        # calculate the gradient del(l)/del(x), del(l)/del(y) and del(l)/del(z)
        dXdl = np.divide(X2 - X1, l2)
        dYdl = np.divide(Y2 - Y1, l2)
        dZdl = np.divide(Z2 - Z1, l2)

        # X0 = surface[ind0, :, 0]
        # Y0 = surface[ind0, :, 1]
        # Z0 = surface[ind0, :, 2]
        # calculate the distance l1
        # l1 = np.sqrt(np.power(X1-X0, 2) + np.power(Y1-Y0, 2) + np.power(Z1-Z0, 2))
        # calculate del(l)/del(s)
        dlds_x = (l2) / (S[ind2 - 1] - S[ind1 - 1])
        dlds_y = (l2) / (S[ind2 - 1] - S[ind1 - 1])
        dlds_z = (l2) / (S[ind2 - 1] - S[ind1 - 1])
        # calculate del(X)/del(s), del(Y)/ del(s) and del(Z)/ del(S)
        dXds = np.multiply(dXdl, dlds_x)
        dYds = np.multiply(dYdl, dlds_y)
        dZds = np.multiply(dZdl, dlds_z)
        # obtain the extrapolated position
        X3 = X2 + dXds * (S[ind2 - 1] - S[ind1 - 1])
        Y3 = Y2 + dYds * (S[ind2 - 1] - S[ind1 - 1])
        Z3 = Z2 + dZds * (S[ind2 - 1] - S[ind1 - 1])

        return X3, Y3, Z3

    def _search_plane(self, sin, tin, Ns, Nc, surface_orig, zc_vec):
        """
        Searches for the best initial guess for S and T in the loftedsurface
        geometry. This acts as a starting point for the Newton iteration.

        Parameters
        ----------
        sin: ndarray
            Intended initial parametric spanwise S points on slice.

        tin: ndarray
            Intended initial parametric chordwise T points on slice.

        Ns: int
            The required spanwise sections

        Nc: int
            The require chordwise sections

        surface_orig: ndarray
            The reshaped lofted surface array

        zc_vec: ndarray
            Z = c planes where the slices are required

        Returns
        -------
        surface_in: ndarray
            Surface as the initial guess for the newton iteration

        param_map_in: ndarray
            Parametric S and T points of the original lofted surface
            corresponding to the initial guess.

        """

        # Initialize the initial guess of the surface
        surface_in = np.zeros((Ns, Nc, 3), dtype=float)
        param_map_in = np.zeros((Ns, Nc, 2), dtype=int)
        t_ind = np.empty(0, dtype=int)
        Nc_orig = surface_orig.shape[1]
        tspace_orig = np.arange(0, Nc_orig)

        # search in t direction and find closest t in original grid
        for j in range(Nc):
            delt = np.abs(tin[j] - tspace_orig)
            # t - index from the original grid where the search should occur
            t_ind = np.append(t_ind, np.argmin(delt))

        for i in range(Ns):
            for j in range(Nc):
                # vector that gives the minimum z-distance to the requested z plane
                delz = np.abs(zc_vec[i] - surface_orig[:, t_ind[j], 2])
                # for equidistant values take the value which is lower than current z-coordinate
                # this is automatically taken care of by the np.argmin() method
                # Find the corresponding S-index
                s_ind = np.argmin(delz)
                # Use the (s_ind,t) value to obtain the (x,y,z) coordinate
                x = surface_orig[s_ind, t_ind[j], 0]
                y = surface_orig[s_ind, t_ind[j], 1]
                z = surface_orig[s_ind, t_ind[j], 2]
                # and assign it to the new Surface matrix
                surface_in[i, j, 0] = x
                surface_in[i, j, 1] = y
                surface_in[i, j, 2] = z
                # store the S,T info from the original surface
                param_map_in[i, j, 0] = s_ind
                param_map_in[i, j, 1] = t_ind[j]

        return surface_in, param_map_in

    def bilinear_surface(self, surface_orig, grid_s, grid_t, S, T):
        """
        Performs bilinear interpolation on the input lofted surface in order
        to obtain the slice in a Z = c plane.

        Parameters
        ----------
        surface_orig: ndarray
            Floating point array of shape (Ns, Nc, 3), comprising of the
            extended lofted surface

        grid_s: ndarray

        grid_t: ndarray

        S: ndarray

        T: ndarray


        """
        # values in main body co-ordinate system atached at the root centre
        values_x = surface_orig[:, :, 0]  # chordwise value
        values_y = surface_orig[:, :, 1]  # from pressure side to suction side
        values_z = surface_orig[:, :, 2]  # blade radius

        # ---------------------- perform bilinear interpolation----------------------
        # 1) find the 4 known data points closest to the point to be interpolated
        Ncs_desired = T.shape[0]
        # stores the positions of the four neighbourhood points for each corresponding
        # interpolant grid location
        grid_map = np.empty((Ncs_desired), dtype=object)
        val_map = np.empty((Ncs_desired), dtype=object)

        for i in range(Ncs_desired):
            # store the x-coordinate of the desired point
            x = S[i]
            # store the y-coordinate of the desired point
            y = T[i]
            # obtain the closest index of the x-coordinate in the original grid
            idx = (np.abs(x - grid_s)).argmin(axis=0)[0]
            # obtain the closest index of the y-coordinate in the desired grid
            idy = (np.abs(y - grid_t).argmin(axis=1))[0]
            # dictionary for storing indicies
            indices_x = {}
            indices_y = {}

            # point in the known grid closest to the desired point
            Px1 = grid_s[idx, idy]
            Py1 = grid_t[idx, idy]

            # store indices
            indices_x[Px1] = [idx, idy]
            indices_y[Py1] = [idx, idy]

            # obtain the neighbourhood
            up_bound_x = np.max(grid_s)
            up_bound_y = np.max(grid_t)

            # obtain the second y-coordinate
            if Py1 == up_bound_y or y < Py1:
                Py2 = grid_t[idx, idy - 1]
                indices_y[Py2] = [idx, idy - 1]

            else:
                Py2 = grid_t[idx, idy + 1]
                indices_y[Py2] = [idx, idy + 1]
            # obtain the second x-coordinate
            if Px1 == up_bound_x or x < Px1:
                Px2 = grid_s[idx - 1, idy]
                indices_x[Px2] = [idx - 1, idy]
            else:
                # print('(Px1=%i, Py1=%i), (Px2=%i, Py2=%i)'%(Px1, Py1, Px2, Py2))
                Px2 = grid_s[idx + 1, idy]
                indices_x[Px2] = [idx + 1, idy]

            # sort the neighbourhood in ascending order
            x1 = min(Px1, Px2)
            ind_x1 = indices_x[x1][0]
            x2 = max(Px1, Px2)
            ind_x2 = indices_x[x2][0]
            y1 = min(Py1, Py2)
            ind_y1 = indices_y[y1][1]
            y2 = max(Py1, Py2)
            ind_y2 = indices_y[y2][1]

            grid_map[i] = [(x1, y1), (x1, y2), (x2, y1), (x2, y2)]
            val_map[i] = [
                (
                    values_x[ind_x1, ind_y1],
                    values_y[ind_x1, ind_y1],
                    values_z[ind_x1, ind_y1],
                ),
                (
                    values_x[ind_x1, ind_y2],
                    values_y[ind_x1, ind_y2],
                    values_z[ind_x1, ind_y2],
                ),
                (
                    values_x[ind_x2, ind_y1],
                    values_y[ind_x2, ind_y1],
                    values_z[ind_x2, ind_y1],
                ),
                (
                    values_x[ind_x2, ind_y2],
                    values_y[ind_x2, ind_y2],
                    values_z[ind_x2, ind_y2],
                ),
            ]

        # obtain the corresponding values
        Q = np.zeros((Ncs_desired, 3), dtype=float)
        for i in range(Ncs_desired):
            x1 = grid_map[i][0][0]
            y1 = grid_map[i][0][1]
            x2 = grid_map[i][3][0]
            y2 = grid_map[i][3][1]

            A = np.array(
                [
                    [1, x1, y1, x1 * y1],
                    [1, x1, y2, x1 * y2],
                    [1, x2, y1, x2 * y1],
                    [1, x2, y2, x2 * y2],
                ]
            )
            # X- values
            X = np.array(
                [
                    [val_map[i][0][0]],
                    [val_map[i][1][0]],
                    [val_map[i][2][0]],
                    [val_map[i][3][0]],
                ]
            )
            # Y-values
            Y = np.array(
                [
                    [val_map[i][0][1]],
                    [val_map[i][1][1]],
                    [val_map[i][2][1]],
                    [val_map[i][3][1]],
                ]
            )
            # Z-values
            Z = np.array(
                [
                    [val_map[i][0][2]],
                    [val_map[i][1][2]],
                    [val_map[i][2][2]],
                    [val_map[i][3][2]],
                ]
            )

            # Coefficient matrix for X-values
            Bx = np.linalg.solve(A, X)[:, 0]
            # Coefficient matrix for Y-values
            By = np.linalg.solve(A, Y)[:, 0]
            # Coefficient matrix for Z-values
            Bz = np.linalg.solve(A, Z)[:, 0]

            x_desired = S[i]
            y_desired = T[i]
            # X-value for the new cross-sectional surface
            Q[i, 0] = (
                Bx[0]
                + Bx[1] * x_desired
                + Bx[2] * y_desired
                + Bx[3] * x_desired * y_desired
            )
            # Y-value for the new cross-sectional surface
            Q[i, 1] = (
                By[0]
                + By[1] * x_desired
                + By[2] * y_desired
                + By[3] * x_desired * y_desired
            )

            # Z-value for the new cross-sectional surface
            Q[i, 2] = (
                Bz[0]
                + Bz[1] * x_desired
                + Bz[2] * y_desired
                + Bz[3] * x_desired * y_desired
            )

        return Q, grid_map, val_map

    def _jacobian_Q(self, S, T, grid_map, val_map):
        """
        Stores the jacobians of the obtained X,Y,Z points with respect to the
        parametric s-t space (s= spanwise location, t= chordwise location).
        The jacobian is calculated using analytic gradients derived from
        bilinear interpolation function.

        Parameters
        ----------
        S: ndarray
            Numpy array of the s (spanwise) coordinate of the desired
            constant z- point in the s-t parametric space

        T: ndarray
            Numpy array of the t (chordwise) coordinate of the desired
            constant z- point in the s-t parametric space

        grid_map: scipy.sparse.coo.coo_matrix
            Numpy array sequence with size equal to the number of
            points on the slice. Each point index has a sequence of 4 dependent
            points from the original s-t space in the order (s1,t1), (s1,t2),
            (s2,t1), (s2, t2) as required by the bilinear interpolation.

        val_map: scipy.sparse.coo.coo_matrix
            Numpy array sequence with size equal to th number of points in the
            slice. Each slice point index has a sequence of cartesian
            (X,Y,Z) values of at the 4 dependent points from the original s-t
            space in the order Q(s1,t1), Q(s1,t2), Q(s2,t1), Q(s2, t2) as
            required by the bilinear interpolation.

        Returns
        -------
        jac_q: ndarray
            A sparse array of size 3Nx2N where N is the number of points on
            the slice consisting of jacobians of the (x,y,z) with respect to s-t
            space.

        dXds: ndarray
            Gradient of cartesian co-ordinate X wrt to the parametric space
            variable S

        dXdt: ndarray
            Gradient of cartesian co-ordinate X wrt to the parametric space
            variable T

        dYds: ndarray
            Gradient of cartesian co-ordinate Y wrt to the parametric space
            variable S

        dYdt: ndarray
            Gradient of cartesian co-ordinate Y wrt to the parametric space
            variable T

        dZds: ndarray
            Gradient of cartesian co-ordinate Z wrt to the parametric space
            variable S

        dZdt: ndarray
            Gradient of cartesian co-ordinate Z wrt to the parametric space
            variable T

        """
        # number of points in the slice
        n_points = S.shape[0]

        # store dxds, dxdt, dyds, dydt, dzds, dzdt in that order
        # for every 1 point there will be 6 non-zero partials, for N --> 6*N
        data = np.zeros(6 * n_points, dtype=float)
        row = np.zeros(6 * n_points, dtype=int)
        col = np.zeros(6 * n_points, dtype=int)

        # initialize the numpy arrays for the partials
        dXds = np.zeros(n_points, dtype=float)
        dXdt = np.zeros(n_points, dtype=float)
        dYds = np.zeros(n_points, dtype=float)
        dYdt = np.zeros(n_points, dtype=float)
        dZds = np.zeros(n_points, dtype=float)
        dZdt = np.zeros(n_points, dtype=float)

        for i in range(n_points):
            s = S[i]
            t = T[i]

            s1 = grid_map[i][0][0]
            t1 = grid_map[i][0][1]
            s2 = grid_map[i][3][0]
            t2 = grid_map[i][3][1]

            # X- values
            X11 = val_map[i][0][0]
            X12 = val_map[i][1][0]
            X21 = val_map[i][2][0]
            X22 = val_map[i][3][0]

            # Y-values
            Y11 = val_map[i][0][1]
            Y12 = val_map[i][1][1]
            Y21 = val_map[i][2][1]
            Y22 = val_map[i][3][1]

            # Z-values
            Z11 = val_map[i][0][2]
            Z12 = val_map[i][1][2]
            Z21 = val_map[i][2][2]
            Z22 = val_map[i][3][2]

            # store partial derivatives of X wrt s and t
            dXds[i] = ((t - t2) * (X11 - X21) + (t - t1) * (X22 - X12)) / (
                (s2 - s1 * (t2 - t1))
            )
            dXdt[i] = ((s - s2) * (X11 - X12) + (s - s1) * (X22 - X21)) / (
                (s2 - s1 * (t2 - t1))
            )

            # store partial derivatives of Y wrt s and t
            dYds[i] = ((t - t2) * (Y11 - Y21) + (t - t1) * (Y22 - Y12)) / (
                (s2 - s1 * (t2 - t1))
            )
            dYdt[i] = ((s - s2) * (Y11 - Y12) + (s - s1) * (Y22 - Y21)) / (
                (s2 - s1 * (t2 - t1))
            )

            # store partial derivatives of Z wrt s and t
            dZds[i] = ((t - t2) * (Z11 - Z21) + (t - t1) * (Z22 - Z12)) / (
                (s2 - s1 * (t2 - t1))
            )
            dZdt[i] = ((s - s2) * (Z11 - Z12) + (s - s1) * (Z22 - Z21)) / (
                (s2 - s1 * (t2 - t1))
            )

        # store the partial derivatives in a vector as input to a sparse matrix
        # store the partial derivatives
        ind = np.arange(0, 6 * n_points, 6)

        # store the partial derivatives in the data vector
        data[ind] = dXds
        data[ind + 1] = dXdt
        data[ind + 2] = dYds
        data[ind + 3] = dYdt
        data[ind + 4] = dZds
        data[ind + 5] = dZdt

        # store the row indices of corresponding partials
        row_x = np.arange(0, 3 * n_points, 3)
        row_y = np.arange(1, 3 * n_points, 3)
        row_z = np.arange(2, 3 * n_points, 3)

        row[ind] = row_x
        row[ind + 1] = row_x
        row[ind + 2] = row_y
        row[ind + 3] = row_y
        row[ind + 4] = row_z
        row[ind + 5] = row_z

        # store the coloumn indices of corrsponding partials
        col_s = np.arange(0, 2 * n_points, 2)
        col_t = np.arange(1, 2 * n_points, 2)

        col[ind] = col_s
        col[ind + 1] = col_t
        col[ind + 2] = col_s
        col[ind + 3] = col_t
        col[ind + 4] = col_s
        col[ind + 5] = col_t

        # store the jacobian in the COO sparse format
        jac_q = coo_matrix(
            (data, (row, col)), shape=(3 * n_points, 2 * n_points)
        )

        return jac_q, dXds, dXdt, dYds, dYdt, dZds, dZdt

    def _jacobian_D(self, Q, D, n_D, n_points, flag=False):
        """
        Stores the jacobian of the distances between consecutive points on the
        cross-sectional slice with respect to the dependent cartesian coordiantes.
        The partial derivatives are calculated from analytic gradients.

        Parameters
        ----------
        Q: float
            Floating point numpy array of the x,y,z coordinate points for the
            sampled surface in the s-t parametric space.
        D: ndarray
            Floating point numpy array of discrete lengths between consecutive
            points on the slice boundary.
        n_D: int
            Size of the discrete length array.
        n_points: int
            Number of points on the cross-sectional slice

        Returns
        -------
        jac_d: ndarray
             A floating point sparse array of size n_Dx3N where N is the number
             of points on the slice, consisting of jacobians of the discrete
             lengths of the slice boundary with respect to the cartesian space.

        """
        # extract the x,y,z coordinates of the slice points
        x = Q[:, 0]
        y = Q[:, 1]
        z = Q[:, 2]

        # store the differences P(i+1)- P(i)
        delta_x = x[1:] - x[0:-1]
        delta_y = y[1:] - y[0:-1]
        delta_z = z[1:] - z[0:-1]

        if flag:
            # add the last element such that P(N+1) = P(0)
            delta_x = np.append(delta_x, x[0] - x[-1])
            delta_y = np.append(delta_y, y[0] - y[-1])
            delta_z = np.append(delta_z, z[0] - z[-1])

        # calculate the partials
        dDdX1 = -np.divide(delta_x, D)
        dDdX2 = -dDdX1

        dDdY1 = -np.divide(delta_y, D)
        dDdY2 = -dDdY1

        dDdZ1 = -np.divide(delta_z, D)
        dDdZ2 = -dDdZ1

        # total sizeof the jacobian
        # size= 3*(n_points**2)
        # store dxds, dxdt, dyds, dydt, dzds, dzdt in that order
        # for every 1 distance, there will be 6 non-zero partials
        data = np.zeros(6 * n_D, dtype=float)
        row = np.zeros(6 * n_D, dtype=int)
        col = np.zeros(6 * n_D, dtype=int)

        # store the partial derivatives
        ind = np.arange(0, 6 * n_D, 6)

        # store the partial derivatives in the data vector
        data[ind] = dDdX1
        data[ind + 1] = dDdY1
        data[ind + 2] = dDdZ1
        data[ind + 3] = dDdX2
        data[ind + 4] = dDdY2
        data[ind + 5] = dDdZ2

        # store the row indices of corresponding partials
        row_d = np.arange(0, n_D, 1)
        row[ind] = row_d
        row[ind + 1] = row_d
        row[ind + 2] = row_d
        row[ind + 3] = row_d
        row[ind + 4] = row_d
        row[ind + 5] = row_d

        col_x = np.arange(0, 3 * n_D, 3)
        col_y = np.arange(1, 3 * n_D, 3)
        col_z = np.arange(2, 3 * n_D, 3)

        col[ind] = col_x
        col[ind + 1] = col_y
        col[ind + 2] = col_z
        col[ind + 3] = col_x + 3
        col[ind + 4] = col_y + 3
        col[ind + 5] = col_z + 3

        if flag:
            # overwriting the final three indices to close the loop
            col[-1] = 2  # del(dn)/del(z1)
            col[-2] = 1  # del(dn)/del(z2)
            col[-3] = 0  # del(dn)/del(z3)

        # construct the jacobian
        jac_d = coo_matrix((data, (row, col)), shape=(n_D, 3 * n_points))

        return jac_d

    def _jacobian_main(self, dZds, dZdt, jac_dp, n_points, n_D, flag=False):
        """Constructs the main jacobian matrix of size 2N x (2N+1)

        Parameters
        ----------
        dZds: ndarray
            Floating point numpy array of gradient of cartesian co-ordinate
            Z wrt to the parametric space variable S

        dZdt: ndarray
            Floating point numpy array of gradient of cartesian co-ordinate Z
            wrt to the parametric space variable

        jac_dp: ndarray
            Sparse array of Jacobian of the discrete lenghts between slice
            points wrt the parametric space (S,T)

        n_points: int
            Number of points on the slice

        n_D: int
            Number of discrete lengths. Determines if the surface boundary is
            closed or open.

        flag: bool
            Flag which if True the surface boundary is considered closed.

        Returns
        -------
        jac_main: ndarray
            Sparse array of main jacobian used in the Newton iteration of
            shape 2N X (2N+1), where N is the number of points on the slice

        """

        # format: first fill in jac_dp (Nx2N), then jac(Z) (Nx2N) followed by grad(t-tc) (1X2N)
        # and lastly grad(dc) (2N+1 X 1)

        data = jac_dp.data

        row = jac_dp.nonzero()[0]
        col = jac_dp.nonzero()[1]  # ind= 0 to ind 2N-1

        # adding delz/delP
        ind_dzdp = np.arange(0, 2 * n_points, 2)
        row_dzdp = np.zeros(2 * n_points, dtype=int)
        col_dzdp = np.zeros(2 * n_points, dtype=int)
        data_dzdp = np.zeros(2 * n_points, dtype=float)
        # fill in data
        data_dzdp[ind_dzdp] = dZds
        data_dzdp[ind_dzdp + 1] = dZdt
        # fill in row
        row_ind_dzdp = np.arange(n_D, 2 * n_D + 1 * (n_points - n_D), 1)
        row_dzdp[ind_dzdp] = row_ind_dzdp
        row_dzdp[ind_dzdp + 1] = row_ind_dzdp
        # fill in column
        col_ind_dzds = np.arange(0, 2 * n_points, 2)
        col_ind_dzdt = np.arange(1, 2 * n_points, 2)
        col_dzdp[ind_dzdp] = col_ind_dzds
        col_dzdp[ind_dzdp + 1] = col_ind_dzdt
        # append it to the main jacobian row, column and data
        data = np.append(data, data_dzdp)
        row = np.append(row, row_dzdp)
        col = np.append(col, col_dzdp)

        # fill in the gradient of (d-dc) wrt to (dc) = -1
        data_dc = np.zeros(n_D, dtype=float)
        row_dc = np.zeros(n_D, dtype=int)
        col_dc = np.zeros(n_D, dtype=int)
        # fill in data
        data_dc[:] = -1
        # fill in row indices
        row_ind_dDdp = np.arange(0, n_D)
        row_dc = row_ind_dDdp
        # fill in column indices
        col_dc[:] = 2 * n_points
        # append it to the main jacobian row, column and data
        data = np.append(data, data_dc)
        row = np.append(row, row_dc)
        col = np.append(col, col_dc)

        # make the del(t1-tc)/del(P). only add non zero entities.
        data_dt1dp = 1.0
        row_dt1dp = 2 * n_D + 1 * (n_points - n_D)
        col_dt1dp = 1
        # append it to the main jacobian row, column and data
        data = np.append(data, data_dt1dp)
        row = np.append(row, row_dt1dp)
        col = np.append(col, col_dt1dp)

        if not flag:
            # make the del(tn-tc)/del(P). only add non zero entities.
            data_dtNdp = 1.0
            row_dtNdp = 2 * n_points
            col_dtNdp = 2 * n_points - 1
            # append it to the main jacobian row, column and data
            data = np.append(data, data_dtNdp)
            row = np.append(row, row_dtNdp)
            col = np.append(col, col_dtNdp)
            # construct the main jacobian
        jac_main = coo_matrix(
            (data, (row, col)), shape=(2 * n_points + 1, 2 * n_points + 1)
        )

        return jac_main

    def _build_residual(self, T, Q, D, zc, dc, tin, n_D, n_points, flag=False):
        """
        Constructs the residual vector.

        Parameters
        ----------
        D: ndarray
            A floating point 1D numpy array of the distances in cartesian space.
        Q: ndarray
            A floating point 2D numpy array of the cartesian space.
        T: ndarray
            A floating point 1D numpy array of the t-coordinates in the
            parametric space.
        zc: float
            Constant z plane where the cross-section is being constructed.
        dc: float
            Constant distance between consecutive points on the cross-
            sectional slice, being calculated by the Newton iteration.
        tc: int
            The starting point of the slice in parametric space.
        n_points: int
            Number of points on the cross-sectional slice.

        Returns
        -------
        R: ndarray
            A floating point 1D numpy array of the residual terms.

        """

        R = np.zeros((2 * n_points + 1), dtype=float)

        # fill up the distance function di-dc
        # update dc
        R[:n_D] = D - dc
        # fill up the z coordinate function z-zc
        R[n_D : 2 * n_D + 1 * (n_points - n_D)] = Q[:, 2] - zc
        # fill up the t1-tc function
        R[2 * n_D + 1 * (n_points - n_D)] = T[0] - tin[0]
        #
        if not flag:
            R[2 * n_points] = T[-1] - tin[-1]

        return R

    def _newton_iteration(self, Pk, jac_main, R, Nc_orig, n_points):
        """
        Outputs the updated state vector and status of various parameters
        essential to determining the health of the iteration.

        Parameters
        ----------
        Pk: ndarray
            A floating point (2n+1) numpy array representing the state of the
            problem at the kth stage.
        jac_main: ndarray
            A floating point sparse array of size (2n+1) X (2n+1) representing
            the jacobian of the state Pk.
        R: ndarray
            A floating point numpy array of size (2n+1) representing the
            residual of the problem.
        Nc_orig: int
            The number of cross-sectional points in the input surface.
        n_points: int
            The number of cross-sectional points in the final desired output.

        Returns
        -------
        Pk1: ndarray
            A floating point numpy array of size (2n+1) representing the state
            at the (k+1)th iteration.
        R_norm : float
            Second norm of the residual.
        delta_norm : float
            Second norm of the state change.
        jac_main_cond : float
            Condition number of the main jacobian.
        alpha : float
            Relaxation factor

        """
        # convert the main jacobian from sparse to dense
        jac_main_array = jac_main.toarray()
        # solve the change in state delta(P)= P(k+1) - Pk
        delta = -np.linalg.solve(jac_main_array, R)
        #
        alpha = self._adaptive_alpha(Pk, delta, Nc_orig, n_points)

        # update the state
        Pk1 = Pk + alpha * delta

        # print out the norm of residual, iteration and norm of delta
        R_norm = np.linalg.norm(R)
        delta_norm = np.linalg.norm(delta)
        jac_main_cond = np.linalg.cond(jac_main_array)

        return Pk1, alpha, R_norm, delta_norm, jac_main_cond

    def _adaptive_alpha(self, Pk, delta, Nc_orig, n_points):
        """
        Value for alpha is obtained that maintains the order of t-space ie
        t0 < t1 < t2 .....< tn and ensures that 0<= t <= tn.

        Parameters
        ----------
            Pk: ndarray
                The state vector comprising of [Si,Ti, S(i+1), T(i+1)] values.
            delta: ndarray
                The change in state vector for the newton step.

        Returns
        -------
            alpha: float
                A floating point value of the relaxation factor between 0 and 1.

        """
        tin = np.arange(1, 2 * n_points, 2)
        # T space at the kth iteration
        Tk = Pk[tin]
        # change in the T-space
        delta_T = delta[tin]

        # specify the T-limits
        T0 = 0
        Tend = Nc_orig - 1

        #  alpha limits
        alpha_max = 1

        # initialize alpha
        alpha = alpha_max

        # --------------Part1-----------------------------------------------------
        # while loop with conditions to satisfy t+delta*alpha<100 and t+delta*alpha>0
        # initialize T_high and T_low
        T_high = Tk + alpha * delta_T
        T_low = Tk - alpha * delta_T

        while max(T_high) > Tend or min(T_low) < T0:
            # decrease alpha by 10%
            alpha -= 0.1 * alpha
            # re-evaluate T_high and T_low
            T_high = Tk + alpha * delta_T
            T_low = Tk - alpha * delta_T

        # ---------------------Part2----------------------------------------------
        # ensure that no points cross over each other

        diff_Tk = Tk[1:] - Tk[0:-1]
        diff_deltaT = delta_T[1:] - delta_T[0:-1]

        diff_deltaT_Tk = alpha * np.abs(diff_deltaT) - diff_Tk

        for i in range(n_points - 1):
            if diff_deltaT[i] < 0 and diff_deltaT_Tk[i] > 0:
                alpha_max = diff_Tk[i] / abs(diff_deltaT[i])
                if alpha > alpha_max:
                    alpha = 0.5 * alpha_max

        return alpha

    def _concat_surface(self, surface_new, span_ind):
        """
        Stores the new surface without the unfilled section.

        Parameters
        ----------
        surface_new: ndarray
            Cross-sectional surface definition of order NsXNcX3

        span_ind: int
            Spanwise index of the un-solved cross-section

        Returns
        -------
        surf_concat: ndarray
            Numpy array of interpolated cross-sectional co-ordinates at the
            requested spanwise section

        """
        # get the number of spanwise indices that need to be filled
        size = len(span_ind)
        # desired spanwise sections
        Ns = surface_new.shape[0]
        # desired chordwise sections
        Nc = surface_new.shape[1]
        # spanwise sections in the concatenated surface
        Ns_concat = Ns - size
        # initialise the concatenated surface
        surf_concat = np.zeros((Ns_concat, Nc, 3), dtype=float)
        # stores previous index to be excluded
        ind_prev = 0
        # stores previous index for the concatenated surface
        indc_prev = 0
        for ind in span_ind:
            # update the number of spanwise elements between two unfilled sections
            indc_len = ind - ind_prev
            indc_new = indc_prev + indc_len
            # concatenate the surface
            surf_concat[indc_prev:indc_new, :, :] = surface_new[
                ind_prev:ind, :, :
            ]
            # update the previous indices
            indc_prev = indc_new
            ind_prev = ind + 1

        # fill in the last index
        surf_concat[indc_prev:, :, :] = surface_new[ind_prev:, :, :]

        return surf_concat

    def _interp_surface(self, surface, zc, span_ind, interp_order=3):
        """
        Interpolates at the unfilled spanwise section of the final surface

        Parameters
        ----------
        surface: ndarray
            Cross-sectional surface definition of order NsXNcX3
        zc: float
            The spanwise z-location where the x,y co-ordiantes are to be
            obtained
        span_ind: int
            Spanwise index of the un-solved cross-section
        interp_order: int
            Interpolation order with 1: linear, 2: quadratic, 3: cubic (default)

        Returns
        -------
        surf: ndarray
            Interpolated cross-sectional co-ordinates at the requested section

        """
        # chordwise sections
        Nc = surface.shape[1]
        # initialize output surf
        surf = np.zeros((Nc, 3), dtype=float)

        for i in range(Nc):
            # spanwise x and y as function of z
            x = surface[:, i, 0]
            y = surface[:, i, 1]
            z = surface[:, i, 2]

            # interp1D functions for x, y, z
            fx = InterpolatedUnivariateSpline(z, x, k=interp_order)
            fy = InterpolatedUnivariateSpline(z, y, k=interp_order)

            # obtain the interpolated x and y
            # obtain the interpolated x, y,z spanwise vectors
            surf[i, 0] = fx(zc)
            surf[i, 1] = fy(zc)
            surf[i, 2] = zc

        return surf

    def _preprocess(self, surface_in):
        """
        Pre-processes the input surface.

        Parameters
        ----------
        surface_in: ndarray
            Lofted blade surface of shape (Nc, Ns, 3)

        Returns:
        -------
        surface_out: ndarray
            Lofted blade surface with trailing edge opened and shape
            (Ns, Nc, 3)

        """
        # call the function to set the min. perturb distance
        self._set_perturb()
        # open the trailing edge by removing the last point
        Ns = surface_in.shape[1]
        for i in range(Ns):
            points = surface_in[:, i, :]
            points = self._open_slice(points)
            surface_in[:, i, :] = points

        # reshape the opened lofted surface
        surface_out = self._reshape(surface_in)

        return surface_out

    def _set_perturb(self):
        """
        Sets the length by which the closed trailing edge is opened.

        """
        surface = self.surface
        d_end = np.sqrt(
            np.power(surface[-1, :, 0] - surface[-2, :, 0], 2)
            + np.power(surface[-1, :, 1] - surface[-2, :, 1], 2)  # x
            + np.power(surface[-1, :, 2] - surface[-2, :, 2], 2)  # y
        )  # z

        d_begin = np.sqrt(
            np.power(surface[1, :, 0] - surface[0, :, 0], 2)
            + np.power(surface[1, :, 1] - surface[0, :, 1], 2)  # x
            + np.power(surface[1, :, 2] - surface[0, :, 2], 2)  # y
        )  # z

        # 1% of the minimum distance
        self.perturb = min(min(np.minimum(d_begin, d_end)) * 0.01, 1e-5)

    def _open_slice(self, points):
        """
        Opens the cross-section by perturbing the final and first point
        of the cross-section provided they are co-incident.

        Parameters
        ----------
        points: ndarray
            Floating point array consisting of cartesian coordinates of the
            the lofted blade surface's cross-section at a certain spanwise
            location.

        Returns
        -------
        points: ndarray
            Floating point array comprising of the lofted surface cross-section
            with opened trailing edge.

        """
        t = np.sqrt(
            np.power(points[-1, 0] - points[0, 0], 2)
            + np.power(points[-1, 1] - points[0, 1], 2)
            + np.power(points[-1, 2] - points[0, 2], 2)
        )

        if t == 0.0:
            # calculate the direction vector between the last and second last point
            d = points[-2, :] - points[-1, :]
            d_last_unit = d / np.linalg.norm(d)

            # calculate the direction vector from the first point to the second point
            d = points[1, :] - points[0, :]
            d_first_unit = d / np.linalg.norm(d)

            # perturb by a small distance along the direction vectors
            x_begin = points[0, :] + d_first_unit * self.perturb

            # perturb by a small distance along the direction vectors
            x_end = points[-1, :] + d_last_unit * self.perturb

            # rewrite the first and last points
            points[0, :] = x_begin
            points[-1, :] = x_end

            # open_flag to know that this was triggered
            self.flag_open = True

        return points

    def _postprocess(self, surface):
        """
        Post-processes the generated sliced surface.

        Parameters
        ----------
        surface_in: ndarray
            Lofted blade surface of shape (Ns, Nc, 3)

        Returns:
        -------
        surface_out: ndarray
            Lofted blade surface with trailing edge opened and shape
            (Nc, Ns, 3)

        """
        # reshape the opened lofted surface
        surface_out = self._reshape(surface)

        # open the trailing edge by removing the last point
        if self.close_surface:
            Ns = surface_out.shape[1]
            for i in range(Ns):
                points = surface_out[:, i, :]
                points = self._close_slice(points)
                surface_out[:, i, :] = points

        return surface_out

    def _close_slice(self, points):
        """
        Closes the cross-section by two methods:
            1) if the cross-section was opened by the program, the closure is
               performed using a similar method and by the same length

            2) if an open cross-section was provided then the closure is
               done by setting the T.E. as the mid-point between the First and
               the last points along the direction vector between the two.

        Parameters
        ----------
        points: ndarray
            Floating point array consisting of cartesian coordinates of the
            the lofted blade surface's cross-section at a certain spanwise
            location.

        Returns
        -------
        points: ndarray
            Floating point array comprising of the lofted surface cross-section
            with closed trailing edge.

        """
        if self.flag_open:
            # calculate the direction vector between the last and second last point
            d = points[-1, :] - points[-2, :]
            d_last_unit = d / np.linalg.norm(d)

            # calculate the direction vector from the first point to the second point
            d = points[0, :] - points[1, :]
            d_first_unit = d / np.linalg.norm(d)

            # perturb by a small distance along the direction vectors
            x_begin = points[0, :] + d_first_unit * self.perturb

            # perturb by a small distance along the direction vectors
            x_end = points[-1, :] + d_last_unit * self.perturb

            # rewrite the first and last points
            points[0, :] = x_begin
            points[-1, :] = x_end

        else:
            # distance between the last and the first point
            t = np.sqrt(
                np.power(points[-1, 0] - points[0, 0], 2)
                + np.power(points[-1, 1] - points[0, 1], 2)
                + np.power(points[-1, 2] - points[0, 2], 2)
            )

            # perturbation for T.E. at the mid-point
            perturb = t / 2.0

            ## calculate the direction vector between the last and second last point
            d = points[0, :] - points[-1, :]
            d_unit = d / np.linalg.norm(d)

            # perturb by a small distance along the direction vectors
            x_begin = points[0, :] - d_unit * perturb

            # perturb by a small distance along the direction vectors
            x_end = points[-1, :] + d_unit * perturb

            # rewrite the first and last points
            points[0, :] = x_begin
            points[-1, :] = x_end

        return points
