"""
core/state.py — Cálculos costosos cacheados con st.cache_data
"""
import streamlit as st
from core.bootstrap import build_curve
from core.sabr import run_full_calibration


@st.cache_data(show_spinner=False)
def get_curve():
    """Curva OIS (bootstrapping sobre 390 nodos). Cacheado."""
    return build_curve()


@st.cache_data(show_spinner=False)
def get_calibration():
    """Calibración SABR anclada al ATM. Cacheado."""
    curve = get_curve()
    DF = curve["DF"]
    return run_full_calibration(DF)
