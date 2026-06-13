"""
core/sabr.py — Fórmula de Hagan et al. (2002) y calibración anclada al ATM
"""
import numpy as np
from scipy.optimize import brentq, least_squares
from core.data import BETA


def sabr_ln_vol(K, f: float, T: float,
                alpha: float, beta: float,
                rho: float, nu: float) -> np.ndarray:
    """
    Volatilidad implícita log-normal de Black bajo SABR.
    Ec. (10) de Hagan, Kumar, Lesniewski & Woodward (2002). Vectorizada en K.
    """
    K   = np.asarray(K, float)
    Fb  = (f * K) ** ((1 - beta) / 2)
    L   = np.log(f / K)
    z   = (nu / alpha) * Fb * L
    sq  = np.sqrt(1 - 2 * rho * z + z * z)
    chi = np.log((sq + z - rho) / (1 - rho))
    chi_safe = np.where(np.abs(z) < 1e-7, 1.0, chi)
    ratio    = np.where(np.abs(z) < 1e-7, 1 - 0.5 * rho * z, z / chi_safe)
    den = Fb * (1
                + ((1 - beta) ** 2 / 24) * L ** 2
                + ((1 - beta) ** 4 / 1920) * L ** 4)
    B   = 1 + (
        ((1 - beta) ** 2 / 24) * alpha ** 2 / (f * K) ** (1 - beta)
        + 0.25 * rho * beta * nu * alpha / Fb
        + (2 - 3 * rho ** 2) / 24 * nu ** 2
    ) * T
    return alpha / den * ratio * B


def alpha_from_atm(sig_atm: float, f: float, T: float,
                   beta: float, rho: float, nu: float) -> float:
    """Resuelve alpha tal que sabr_ln_vol(f, f, ...) = sig_atm."""
    g = lambda a: float(sabr_ln_vol(f, f, T, a, beta, rho, nu)) - sig_atm
    return brentq(g, 1e-6, 5.0, xtol=1e-14)


def calibrate_anchored(strikes: np.ndarray, vols: np.ndarray,
                       f: float, T: float, sig_atm: float,
                       beta: float = BETA) -> dict:
    """
    Calibra (rho, nu); alpha se ancla al ATM.
    Minimiza residuales únicamente en strikes ≠ ATM.
    """
    strikes = np.asarray(strikes, float)
    vols    = np.asarray(vols, float)
    off = np.abs(strikes - f) > 1e-12
    Ko, Vo = strikes[off], vols[off]

    def resid(x):
        rho, nu = x
        a = alpha_from_atm(sig_atm, f, T, beta, rho, nu)
        return sabr_ln_vol(Ko, f, T, a, beta, rho, nu) - Vo

    sol = least_squares(resid, [0.0, 0.5],
                        bounds=([-0.999, 1e-4], [0.999, 5.0]),
                        max_nfev=20000, xtol=1e-12, ftol=1e-12)
    rho, nu = sol.x
    a = alpha_from_atm(sig_atm, f, T, beta, rho, nu)
    return dict(alpha=a, beta=beta, rho=rho, nu=nu,
                rmse=float(np.sqrt(np.mean(sol.fun ** 2))))


def run_full_calibration(DF: np.ndarray) -> dict:
    """
    Ejecuta la calibración SABR anclada para todos los 19 tenores de VCUB.
    Devuelve el diccionario de resultados y los grids de parámetros.
    """
    from core.data import TENOR_LBL_SW, TENOR_Y_SW, VOL_N, ATM_N, STRIKE_ABS, BETA
    from core.bootstrap import fwd_swap_and_annuity
    from core.data import EXPIRY_FIX

    BAND = 0.55

    calib = {}
    for lbl, Tt, row, atmn in zip(TENOR_LBL_SW, TENOR_Y_SW, VOL_N, ATM_N):
        f, A, a_, b_ = fwd_swap_and_annuity(EXPIRY_FIX, Tt, DF)
        Ks  = f + STRIKE_ABS
        valid = Ks > 0
        Ks, rr = Ks[valid], row[valid]
        sel = np.abs(Ks / f - 1) <= BAND
        Ka, Va = Ks[sel], rr[sel]
        ca = calibrate_anchored(Ka, Va, f, EXPIRY_FIX, atmn, BETA)
        calib[lbl] = dict(T=EXPIRY_FIX, tenor=Tt, f=f, A=A, **ca)

    TEN_GRID = np.array([calib[l]["tenor"] for l in TENOR_LBL_SW])
    AL_GRID  = np.array([calib[l]["alpha"] for l in TENOR_LBL_SW])
    RH_GRID  = np.array([calib[l]["rho"]   for l in TENOR_LBL_SW])
    NU_GRID  = np.array([calib[l]["nu"]    for l in TENOR_LBL_SW])

    return dict(calib=calib, TEN_GRID=TEN_GRID,
                AL_GRID=AL_GRID, RH_GRID=RH_GRID, NU_GRID=NU_GRID)


def sabr_params_interp(tenor: float, TEN_GRID, AL_GRID, RH_GRID, NU_GRID) -> tuple:
    """Interpolación lineal de (alpha, rho, nu) al tenor solicitado."""
    al  = float(np.interp(tenor, TEN_GRID, AL_GRID))
    rho = float(np.interp(tenor, TEN_GRID, RH_GRID))
    nu  = float(np.interp(tenor, TEN_GRID, NU_GRID))
    return al, rho, nu
