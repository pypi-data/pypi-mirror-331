"""Canopy radiative transfer."""

import numpy as np


def diffuse_fraction(trans: float, theta: float) -> float:
    """
    Calculate the fraction of diffuse radiation.

    Parameters
    ----------
    trans : float
        Atmospheric transmissivity (0 to 1).
    theta : float
        Solar zenith angle in radians. Must be within [0, pi / 2).

    Returns
    -------
    float
        The fraction of diffuse radiation.

    References
    ----------
    .. [STG86] Spitters, C. J. T., Toussaint, H. A. J. M., & Goudriaan, J.
        (1986). Separating the diffuse and direct component of global radiation
        and its implications for modeling canopy photosynthesis Part I.
        Components of incoming radiation. _Agricultural and Forest
        Meteorology_, 38(1--3), 217--229.
        <https://doi.org/10.1016/0168-1923(86)90060-2>

    """
    if trans <= 0.22:
        return 1.0
    elif 0.22 < trans <= 0.35:
        return 1.0 - 6.4 * (trans - 0.22) ** 2
    else:
        r = 0.847 - 1.61 * np.cos(theta) + 1.04 * np.cos(theta) ** 2
        k = (1.47 - r) / 1.66
        if 0.35 < trans <= k:
            return 1.47 - 1.66 * trans
        else:
            return r


def extinc_coef(theta, chi):
    """
    Calculate the extinction coefficient of the plant canopy.

    Parameters
    ----------
    theta : float or array_like
        Solar zenith angle in radians. Must be within [0, pi / 2).
    chi : float or array_like
        Leaf shape parameter for light extinction.

    Returns
    -------
    float or array_like
        The light extinction coefficient of the canopy [m^2 m^-2].

    """
    return np.sqrt(chi * chi + np.tan(theta) ** 2) / (
        chi + 1.774 * (chi + 1.182) ** (-0.733)
    )
