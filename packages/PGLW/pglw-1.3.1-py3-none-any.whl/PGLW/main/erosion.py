import numpy as np
from numpy import newaxis as na

from PGLW.main.geom_tools import act_tanh


def spectrum(u, dt, omega_max=15e3):
    """
    Calculate power sepctrum and spectral moments with kmax as cut_off wave number

    Parameters
    ----------
    u : 1D-array(float) [m]
        signal values u(t)

    dt : float [m]
        signal spacing or step between samples of u

    omega_max : float [rad/m]
        upper angular frequency limit for spectral moment computation

    Returns
    -------
    omega : 1D-array(float) [rad/m]
        angular wave frequency

    A : 1D-array(float) [m]
        FFT amplitudes

    S : float [m^3/rad]
        power spectrum

    S0 : float
        zeroth moment

    S2 : float
        second moment

    S4 : float
        fourth moment
    """
    # Make signal even if it should not be already
    L = len(u)
    if L % 2 != 0:
        u = np.delete(u, L - 1)
        L -= 1
    fN = 1.0 / (2 * dt)  # Nyquist frequency
    df = fN / (L / 2)  # Sampling frequency

    f = np.linspace(0, fN, L // 2 + 1)  # frequencies
    omega = 2 * np.pi * f  # angular frequency

    Y = (
        np.fft.rfft(u - np.mean(u)) / L
    )  # One sided discrete Fourier coefficients (m)
    # Harmonic amplitudes (m)
    A = np.abs(Y)  # get amplitude
    A[1:-1] = 2 * A[1:-1]  # as negative side discarded, double coefficients
    # S(omega)
    S = 0.5 * A**2 / (2 * np.pi * df)  # Energy density (m^2/(rad/s))
    # as this is not time but length here s becomes m and we get as units m^3/rad

    # Spectral moments, only until a certain cutoff
    iomegamax = np.where(omega > omega_max)[0]
    if not iomegamax.size > 0:
        iomegamax = len(omega) - 1
    else:
        iomegamax = iomegamax[0]
    # int_0_inf omega^n * S(omega) domega
    S0 = np.trapz(S[:iomegamax], omega[:iomegamax])  # (m^2)
    S2 = np.trapz(omega[:iomegamax] ** 2 * S[:iomegamax], omega[:iomegamax])
    S4 = np.trapz(omega[:iomegamax] ** 4 * S[:iomegamax], omega[:iomegamax])

    return omega, A, S, S0, S2, S4


def LER_spectrum(omega, stdev=0.2023e-3, lambda0=2.3023e-3, A=0.175, B=0.290):
    """
    Roughness power spectrum inspired from ocean wave theory.
    With default coefficient fitted to the phase 3 erosion surface data by
    Veraart et al. (2017).

    Parameters
    ----------
    omega : 1D-array(float) [rad/m]
        angular wave frequency

    stdev : float [m]
        LER specific standard deviation of surface perturbations

    lambda0 : float [m]
        LER specific 0-upcrossing wave length

    A : float
        universal spectral shape coefficient for high wave frequencies

    B : float
        universal spectral shape coefficient for low wave frequencies

    Returns
    -------
    S(omega) : float [m^3/rad]
        LER power spectrum as function of angular wave frequency
    """
    return (
        stdev**2.0
        * lambda0
        * A
        * np.sqrt(omega * lambda0)
        * np.exp(-B * omega * lambda0)
    )


def act_supergauss(x, sigma, p, flim=0.01):
    """
    Super-gaussian activation function
    """
    # rescale
    x = abs(x)
    x /= x.max()
    xlim = 2 * sigma * (-np.log(flim)) ** (1 / (2 * p))
    x *= xlim
    return np.exp(-(((x / (2.0 * sigma)) ** 2) ** p))


def ocean_erosion(
    domega=2 * np.pi / 203.7447e-3,
    fac_dxy_domega=2,
    Lx_in=203.7447e-3,
    Ly_in=203.7447e-3 / 10.0,
    Nomega=281,
    Ndirs=40,
    stdev=0.2023e-3,
    lambda0=2.3023e-3,
    mu=-0.4693e-3,
    damage_limits=[-1.5e-3, 0.0],
    A=0.175,
    B=0.290,
    seed=0,
    wavedir="2D",
    scale=True,
    avgfit_c0=0.4021,
    avgfit_c1=1.5361,
    stdfit_c0=0.3968,
    stdfit_c1=1.4084,
    edge_smooth=0.1,
):
    """
    Create 2D surface patch of superimposed waves mimicing the eroded
    leading edge on wind turbines. The method is inspired by ocean
    wave modelling.
    With default coefficient fitted to the phase 3 erosion surface data by
    Veraart et al. (2017).

    In the following lines the recommended units are given for certain
    inputs inbetween [], however that's not fixed.

    Parameters
    ----------
    domega : float [rad/m]
        resolution of the angular wave frequencies

    fac_dxy_domega : int
        the ration between the spatial resolution of the patch and the
        resolution of the wave angular frequencies. Should be at least
        2, otherwise the resolution is not sufficient to capture the
        highest frequency. So one could think of it as the sampling
        frequency, which by Nyquist sould be at least 2*fmax.
        dxy = 2pi/(fac_dxy_domega*domega*Nomega)

    Lx_in : float [m]
        erosion patch length along main wave propagation direction. For
        a wind turbine blade this corresponds to the spanwise direction.
        Note that Lx_in is modified such that it is always divisible by
        dxy.

    Ly_in : float [m]
        erosion patch length in cross wave propagation direction. For
        a wind turbine blade it would correspond to the distance along
        the aerofoil spline. Note that Lx_in is modified such that it
        is always divisible by dxy.

    Nomega : int
        no. of angular frequency bins to simulate

    Ndirs : int
        only used if wavedir=='2D'. No. of wave directions to simulate.
        Discretizes directional space from -pi/2 to pi/2.
        If not uneven it will be made uneven such that the main wave
        direction is resolved ie theta=0.

    stdev : float [m]
        LER specific standard deviation of surface perturbations

    lambda0 : float [m]
        LER specific 0-upcrossing wave length

    mu : float [m]
        mean value of perturbations

    damage_limits : list(float) or None
        lower and upper limit to surface perturbations. All values exceeding
        these limits are set to respective limit value.

    A : float
        universal spectral shape coefficient for high wave frequencies

    B : float
        universal spectral shape coefficient for low wave frequencies

    Nomega : float
        Universal spectral shape coefficient for low wave frequencies

    seed : int
        turbulent seed used in random number generation

    wavedir : string ('1D'/'2D')
        create waves in a single direction ('1D') or all directions ('2D').

    scale: bool
        scale the mean and standard deviation as function of the cross direction,
        such that they become zero towards the edges. This allows a smooth transition
        into a clean aerofoil and observed on rain erosion tests as well. The
        scaling is performed by a super-gaussian.

    avgfit_c0
        super-gauss constant for mean erosion level scaling

    avgfit_c1
        super-gauss constant for mean erosion level scaling

    stdfit_c0
        super-gauss constant for erosion level standard deviation scaling

    stdfit_c1
        super-gauss constant for erosion level standard deviation scaling

    edge_smooth
        fraction of Ly over which edge smoothing is applied, only active
        with scaling enabled. Towards each edge in y a hyperbolic tangent
        scaling function ensures that the erosion is going smoothly
        towards 0. It is active for abs(y) > (Ly/2 - edge_smooth*Ly).

    Returns
    -------
    patch : dict
        output dictionary containing all outputs

    patch['dxy'] : float [m]
        spatial resolution, uniform in both directions

    patch['x'] : 1D-array(float) [m]
        erosion patch discretisation in main wave propagation direction

    patch['y'] : 1D-array(float) [m]
        erosion patch discretisation in cross main propagation direction

    patch['Lx'] : float [m]
        erosion patch length along main wave propagation direction

    patch['Ly'] : float [m]
        erosion patch length in cross wave propagation direction

    patch['omega_e'] : 1D-array(float) [rad/m]
        angular wave frequency bin edges

    patch['dn'] : 2D-array(float) [m]
        final patch normal surface perturbations ie. erosion pattern

    patch['dn_unistat'] : 2D-array(float) [m]
        patch normal surface perturbations, intermediate output
        without scaling and damage limit enforcement

    patch['dn_varstat'] : 2D-array(float) [m]
        patch normal surface perturbations with scaling in y, but
        without damage limit enforcement

    patch['dth'] = dth
        only if wavedir=='2D', directional resolution of wave pattern

    patch['th'] = th
        only if wavedir=='2D', simulated wave directions

    """

    # sample frequency (rad/s or for spatial coordinates rad/m)
    omega_sf = Nomega * domega

    # spatial resolution, directly connected to sample frequency
    dxy = 1.0 / fac_dxy_domega * np.pi / (omega_sf)

    # number of grid points in x and y, ensuring the Lx and Ly are
    # divisible by dxy
    nx, ny = int(np.ceil(Lx_in / dxy)) + 1, int(np.ceil(Ly_in / dxy)) + 1

    # linear spacing in frequencies
    # frequency bin edges
    omega_e = np.linspace(0.0, omega_sf, Nomega + 1)
    # frequency bin centres
    omega_c = 0.5 * (omega_e[1:] + omega_e[:-1])

    # Anders spectral energy model for roughness (m^3/rad)
    Svar = LER_spectrum(omega_c, stdev=stdev, lambda0=lambda0, A=A, B=B)
    # amplitudes (m)
    amp = np.sqrt(2.0 * Svar * domega)

    # spatial dicretization
    # erosion patch discretisation in main wave propagation direction
    x = np.linspace(0, (nx - 1) * dxy, nx) - (nx - 1) * dxy / 2.0
    Lx = x[-1] - x[0]
    # erosion patch discretisation in cross main propagation direction
    y = np.linspace(0, (ny - 1) * dxy, ny) - (ny - 1) * dxy / 2.0
    Ly = y[-1] - y[0]
    xx, yy = np.meshgrid(x, y)
    # normal to plane surface perturbations
    dn = np.zeros_like(xx)

    # create surface
    # ensures the surface is reproducable by setting the seed
    np.random.seed(seed)
    patch = {}
    if wavedir == "1D":
        # random phase shifts
        phases = np.random.rand(Nomega) * 2.0 * np.pi

        # superpose sine waves to simulate roughness perturbations
        dn_arr = amp[:, na, na] * np.sin(
            omega_c[:, na, na] * xx[na, :, :] + phases[:, na, na]
        )
        dn = dn_arr.sum(axis=0)

    elif wavedir == "2D":
        # directional discretization
        # ensure Ndirs is uneven so theta=0 is included
        Ndirs = 2 * (Ndirs // 2) + 1
        dth = np.pi / Ndirs
        # also capture perpendicular wave, however only once
        th = np.linspace(0, 1, Ndirs + 1) * np.pi - np.pi / 2
        th = 0.5 * (th[1:] + th[:-1])
        # scaling factor
        # fth = np.ones_like(th)/(np.pi)
        fth = 2.0 / np.pi * (np.cos(th)) ** 2

        # random phase shifts
        phases = (np.random.rand(Nomega * Ndirs) * 2.0 * np.pi).reshape(
            Nomega, Ndirs
        )

        # superpose sine waves to simulate roughness perturbations
        for i in range(Nomega):
            for j in range(Ndirs):
                dn += (
                    amp[i]
                    * np.sqrt(fth[j] * dth)
                    * np.sin(
                        omega_c[i] * (xx * np.cos(th[j]) + yy * np.sin(th[j]))
                        + phases[i, j]
                    )
                )
            print(
                "Percentage completed: {:.1f}%".format(
                    (i * j + i + 1) / (Nomega * Ndirs) * 1e2
                )
            )
        # dn_arr = amp[:, na, na, na] * np.sqrt(fth * dth)[na, :, na, na] *
        #          np.sin(omega_c[:, na, na, na] *
        #          (xx[na, na, :, :] * np.cos(th)[na, :, na, na] +
        #           yy[na, na, :, :] * np.sin(th)[na, :, na, na]) +
        #           phases[:, :, na, na])
        # dn = (dn_arr.sum(axis=0)).sum(axis=0)
        patch["th"] = th
        patch["dth"] = dth

    # 2D homogenous roughness
    patch["dn_unistat"] = dn + mu

    # scaling of mean and standard deviation in y
    if scale:
        # get stats
        dn_avg = np.mean(dn, axis=1)
        # get flactuations and scale, remove the mean and add afterwards
        # to ensure continuity
        frat = act_supergauss(y, stdfit_c0, stdfit_c1, flim=0.1)
        dnf = ((dn - dn_avg[:, na]) * frat[:, na]) + dn_avg[:, na]
        # add the mean on top
        frat = act_supergauss(y, avgfit_c0, avgfit_c1, flim=0.1)
        dn = dnf + mu * frat[:, na]
        # further smoothing towards the edges, so it can simply be added
        # to a surface in a smooth manner
        ff = np.zeros_like(y)
        # smoothing length scale
        smooth_len = edge_smooth * Ly
        # y > 0 edge
        ii = np.where(y >= (y[-1] - smooth_len))[0][0]
        fedge = act_tanh(y[ii:], smooth_len, y[-1])
        dn[ii:, :] -= fedge[:, na] * dn[ii:, :]
        # ensure edge point to be zero
        dn[-1, :] = 0.0
        # smooth at negative y edge
        ii = np.where(y <= (y[0] + smooth_len))[0][-1]
        fedge = act_tanh(abs(y[: ii + 1]), smooth_len, abs(y[0]))
        ff[: ii + 1] = fedge
        dn[: ii + 1, :] -= fedge[:, na] * dn[: ii + 1, :]
        # ensure edge point to be zero
        dn[0, :] = 0.0
        patch["dn_varstat"] = dn.copy()

    # impose upper and lower damage limits
    if damage_limits:
        dn[dn > damage_limits[1]] = damage_limits[1]
        dn[dn < damage_limits[0]] = damage_limits[0]

    # store data
    patch["dn"] = dn
    patch["dxy"] = dxy
    patch["x"] = x
    patch["y"] = y
    patch["Lx"] = Lx
    patch["Ly"] = Ly
    patch["omega_e"] = omega_e

    return patch
