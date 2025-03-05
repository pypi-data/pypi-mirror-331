"""Stomatal conductance."""

from ecoflux.physchem.sat_vap import p_sat_h2o


def ball_berry_predictor(A_n, E, pressure, T_leaf, stom_cond, bl_cond, co2):
    r"""
    Calculate the Ball–Berry predictor (A * h_s / co2_s) from leaf flux data.

    Note: This function is used for processing leaf-level gas-exchange data. It
    does not describe a forward model for stomatal conductance.

    Parameters
    ----------
    A_n : array_like
        CO2 assimilation rate [µmol m\ :sup:`–2` s\ :sup:`–1`].
    E : array_like
        Transpiration rate [mol m\ :sup:`–2` s\ :sup:`–1`].
    pressure : array_like
        Ambient pressure [Pa].
    T_leaf : array_like
        Leaf temperature [C].
    stom_cond : array_like
        Stomatal conductance to water vapor [mol m\ :sup:`–2` s\ :sup:`–1`].
    bl_cond : array_like
        Boundary layer conductance to water vapor
        [mol m\ :sup:`–2` s\ :sup:`–1`].
    co2 : array_like
        Ambient CO2 concentration [µmol mol\ :sup:`–1`].

    Returns
    -------
    array_like
        Ball-Berry predictor ``(A * h_s / co2_s)``
        [mol m\ :sup:`–2` s\ :sup:`–1`]. Note that this is not the Ball–Berry
        slope, but a regressor used to determine the Ball–Berry slope.

    """
    # This follows roughly the algorithm in the LI6400-XT manual (page 15-37),
    # but uses a more accurate e_sat function and bl_cond ratio.
    h_s = 1.0 - (E * pressure) / (p_sat_h2o(T_leaf) * stom_cond)
    co2_s = co2 - A_n * 1.37 / bl_cond
    return A_n * h_s / co2_s
