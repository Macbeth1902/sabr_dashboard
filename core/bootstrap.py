"""
core/bootstrap.py — Bootstrapping OIS directo sobre 390 nodos
"""
import numpy as np
import pandas as pd
from core.data import PAR_FULL, DC, N_TOTAL


def bootstrap_ois_directo(par_full: np.ndarray = PAR_FULL, dc: float = DC) -> np.ndarray:
    """
    Resuelve DF en cada nodo de 28 días por solución cerrada, nodo a nodo.
    DF[0]=1  (hoy)  …  DF[390]  (≈30.33 años)
    """
    n = len(par_full)
    DF = np.zeros(n + 1)
    DF[0] = 1.0
    A = 0.0
    for i in range(1, n + 1):
        S = par_full[i - 1]
        DF[i] = (1.0 - S * A) / (1.0 + S * dc)
        A += dc * DF[i]
    return DF


def build_curve(par_full: np.ndarray = PAR_FULL) -> dict:
    """
    Construye y devuelve la curva OIS completa como diccionario de arrays.
    """
    DF = bootstrap_ois_directo(par_full)
    idx   = np.arange(0, N_TOTAL + 1)
    days  = idx * 28
    years = days / 360.0

    with np.errstate(divide="ignore", invalid="ignore"):
        zero = np.where(years > 0, -np.log(DF) / np.maximum(years, 1e-12), np.nan)

    fwd28 = np.full_like(DF, np.nan)
    fwd28[1:] = (DF[:-1] / DF[1:] - 1.0) / DC

    df_curva = pd.DataFrame({
        "Periodo (28d)":         idx[1:].astype(int),
        "Plazo (días)":          days[1:].astype(int),
        "Plazo (años)":          years[1:],
        "DF":                    DF[1:],
        "Tasa cero cont. (%)":   zero[1:] * 100,
        "Fwd 28d (%)":           fwd28[1:] * 100,
    })

    return {"DF": DF, "years": years, "zero": zero, "fwd28": fwd28, "df": df_curva}


def fwd_swap_and_annuity(expiry_y: float, tenor_y: float, DF: np.ndarray) -> tuple:
    """
    Calcula el forward par swap y la anualidad para un swaption tex × tenor.
    a = nodo de inicio (expiry),  b = nodo final (expiry + tenor).
    """
    def coupons(t: float) -> int:
        return int(round(t * 360.0 / 28.0))

    a = coupons(expiry_y)
    b = min(a + coupons(tenor_y), N_TOTAL)
    A = DC * np.sum(DF[a + 1: b + 1])
    fwd = (DF[a] - DF[b]) / A
    return fwd, A, a, b
