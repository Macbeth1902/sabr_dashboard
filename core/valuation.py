"""
core/valuation.py — Black-76 y valuación de swaptions con volatilidad SABR
"""
import numpy as np
from scipy.stats import norm
from core.data import BETA, EXPIRY_FIX
from core.bootstrap import fwd_swap_and_annuity
from core.sabr import sabr_ln_vol, sabr_params_interp


def black76_swaption(f: float, K: float, T: float, sigma: float,
                     annuity: float, notional: float = 1.0,
                     payer: bool = True) -> float:
    """Precio Black-76 de un swaption europeo."""
    d1 = (np.log(f / K) + 0.5 * sigma ** 2 * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if payer:
        core = f * norm.cdf(d1) - K * norm.cdf(d2)
    else:
        core = K * norm.cdf(-d2) - f * norm.cdf(-d1)
    return notional * annuity * core


def valuar_swaption(tenor: float, notional: float, payer: bool,
                    strike_mode: str, strike_value: float,
                    DF: np.ndarray,
                    TEN_GRID, AL_GRID, RH_GRID, NU_GRID) -> dict:
    """
    Valúa un swaption europeo.

    strike_mode: "ATM"  → K = forward
                 "rel"  → K = forward + strike_value  (strike_value en decimal)
                 "abs"  → K = strike_value  (tasa absoluta en decimal)
    """
    f0, A0, a_idx, b_idx = fwd_swap_and_annuity(EXPIRY_FIX, tenor, DF)

    if   strike_mode == "ATM": K = f0
    elif strike_mode == "rel": K = f0 + float(strike_value)
    elif strike_mode == "abs": K = float(strike_value)
    else: raise ValueError("strike_mode debe ser 'ATM', 'rel' o 'abs'")

    assert K > 0, "El strike debe ser positivo (modelo log-normal, beta=1)"

    al, rho, nu = sabr_params_interp(tenor, TEN_GRID, AL_GRID, RH_GRID, NU_GRID)
    sigma = float(sabr_ln_vol(K, f0, EXPIRY_FIX, al, BETA, rho, nu))
    prima = black76_swaption(f0, K, EXPIRY_FIX, sigma, A0, notional, payer)

    if payer:
        posicion = "OTM" if K > f0 else ("ITM" if K < f0 else "ATM")
    else:
        posicion = "ITM" if K > f0 else ("OTM" if K < f0 else "ATM")

    return dict(
        tenor=tenor, f=f0, A0=A0, K=K,
        alpha=al, rho=rho, nu=nu,
        sigma=sigma, prima=prima,
        payer=payer, posicion=posicion,
        notional=notional,
    )
