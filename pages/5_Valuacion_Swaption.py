"""
pages/5_Valuacion_Swaption.py — Calculadora interactiva de swaptions
"""
import streamlit as st
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Valuación Swaption · SABR", page_icon="💹", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

from core.state import get_curve, get_calibration
from core.valuation import valuar_swaption
from core.charts import fig_smile_comparison

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem 0;'>
    <div class='hero-subtitle'>Calculadora Interactiva</div>
    <h1 style='margin:0.3rem 0; font-size:2rem;'>Valuación del Swaption con SABR</h1>
    <p style='color:#94A3B8; max-width:700px; line-height:1.6;'>
        Elige tenor, strike y tipo de swaption. La volatilidad implícita se obtiene
        de la fórmula de Hagan et al. y se inserta en Black-76.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Cálculos cacheados ──────────────────────────────────────────────────────
with st.spinner("Cargando curva y calibración…"):
    curve  = get_curve()
    result = get_calibration()

DF       = curve["DF"]
TEN_GRID = result["TEN_GRID"]
AL_GRID  = result["AL_GRID"]
RH_GRID  = result["RH_GRID"]
NU_GRID  = result["NU_GRID"]

# ── Layout: controles izquierda / resultados derecha ───────────────────────
col_ctrl, col_res = st.columns([1, 1.6], gap="large")

with col_ctrl:
    st.markdown("""
    <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                letter-spacing:0.1em; margin-bottom:1rem;'>Parámetros del swaption</div>
    """, unsafe_allow_html=True)

    # ── Tipo de swaption ────────────────────────────────────────────────
    tipo = st.radio(
        "Tipo de swaption",
        options=["Receiver", "Payer"],
        horizontal=True,
        help="Receiver: derecho a recibir tasa fija (put sobre la tasa). "
             "Payer: derecho a pagar tasa fija (call sobre la tasa).",
    )
    payer = (tipo == "Payer")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Tenor del swap subyacente ──────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.8rem; color:#F1F5F9; font-weight:500;
                margin-bottom:0.2rem;'>Tenor del swap subyacente</div>
    """, unsafe_allow_html=True)

    TENORES_DISPONIBLES = [
        1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 7.5, 8.0,
        9.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0
    ]
    TENORES_LABELS = [
        "1A", "2A", "3A", "4A", "5A", "6A", "7A", "7.5A (interpolado)", "8A",
        "9A", "10A", "12A", "15A", "20A", "25A", "30A"
    ]

    tenor_label = st.select_slider(
        "Tenor",
        options=TENORES_LABELS,
        value="7.5A (interpolado)",
        label_visibility="collapsed",
        help="El tenor 7.5A fuerza la interpolación lineal entre los nodos 7Yr y 8Yr.",
    )
    tenor_y = TENORES_DISPONIBLES[TENORES_LABELS.index(tenor_label)]

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Nocional ─────────────────────────────────────────────────────────
    nocional_mill = st.number_input(
        "Nocional (millones MXN)",
        min_value=0.1, max_value=5_000.0, value=10.0, step=1.0,
        format="%.1f",
    )
    nocional = nocional_mill * 1_000_000

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # ── Strike ───────────────────────────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.8rem; color:#F1F5F9; font-weight:500;
                margin-bottom:0.2rem;'>Definición del strike</div>
    """, unsafe_allow_html=True)

    strike_modo = st.radio(
        "Modo de strike",
        options=["ATM", "Desplazamiento (pb)", "Tasa absoluta (%)"],
        label_visibility="collapsed",
        help="ATM: el strike coincide con el forward. "
             "Desplazamiento: strike = forward + Δ bps. "
             "Tasa absoluta: introduces la tasa directamente.",
    )

    if strike_modo == "ATM":
        strike_mode_code = "ATM"
        strike_value = 0.0
        st.info("Strike = Forward ATM (calculado de la curva OIS)")

    elif strike_modo == "Desplazamiento (pb)":
        strike_mode_code = "rel"
        desplazamiento_bp = st.slider(
            "Desplazamiento Δ (puntos base)",
            min_value=-300, max_value=300, value=50, step=5,
        )
        strike_value = desplazamiento_bp / 1e4
        signo = "+" if desplazamiento_bp >= 0 else ""
        st.caption(f"Strike = Forward {signo}{desplazamiento_bp} pb")

    else:  # Tasa absoluta
        strike_mode_code = "abs"
        strike_pct = st.number_input(
            "Tasa de strike (%)",
            min_value=0.10, max_value=25.0, value=9.17, step=0.01,
            format="%.4f",
        )
        strike_value = strike_pct / 100.0

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Botón de valuación ────────────────────────────────────────────────
    valuar_btn = st.button("⚡  Valuar swaption", use_container_width=True, type="primary")

    # ── Caso de estudio predefinido ───────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    with st.expander("📋  Cargar caso de estudio del proyecto"):
        st.markdown("""
        Reproduce el ejemplo del PDF: *receiver* swaption,
        tenor 7.5A (interpolado), nocional 10 MM MXN, con dos strikes:
        **ATM** y **+50 pb**.
        """)
        if st.button("Cargar caso de estudio", use_container_width=True):
            st.session_state["caso_estudio"] = True
            st.rerun()

# ── Ejecutar valuación ──────────────────────────────────────────────────────
if "caso_estudio" in st.session_state and st.session_state["caso_estudio"]:
    # Caso del proyecto: ATM y +50pb
    try:
        res_atm  = valuar_swaption(7.5, 10_000_000, False, "ATM", 0.0,
                                   DF, TEN_GRID, AL_GRID, RH_GRID, NU_GRID)
        res_50   = valuar_swaption(7.5, 10_000_000, False, "rel", 0.005,
                                   DF, TEN_GRID, AL_GRID, RH_GRID, NU_GRID)
        resultados = [res_atm, res_50]
    except Exception as e:
        st.error(f"Error en la valuación: {e}")
        resultados = []
elif valuar_btn:
    try:
        res = valuar_swaption(
            tenor_y, nocional, payer,
            strike_mode_code, strike_value,
            DF, TEN_GRID, AL_GRID, RH_GRID, NU_GRID,
        )
        resultados = [res]
    except Exception as e:
        st.error(f"Error en la valuación: {e}")
        resultados = []
else:
    # Carga inicial: muestra el caso de estudio por defecto
    try:
        res_atm = valuar_swaption(7.5, 10_000_000, False, "ATM", 0.0,
                                  DF, TEN_GRID, AL_GRID, RH_GRID, NU_GRID)
        res_50  = valuar_swaption(7.5, 10_000_000, False, "rel", 0.005,
                                  DF, TEN_GRID, AL_GRID, RH_GRID, NU_GRID)
        resultados = [res_atm, res_50]
    except Exception as e:
        resultados = []

# ── Panel de resultados ─────────────────────────────────────────────────────
with col_res:
    if not resultados:
        st.info("Configura los parámetros y presiona **Valuar swaption**.")
    else:
        # Título del panel
        es_caso = (len(resultados) == 2 and
                   not resultados[0]["payer"] and
                   abs(resultados[0]["tenor"] - 7.5) < 0.01)
        if es_caso and "caso_estudio" in st.session_state:
            st.markdown("""
            <div style='font-size:0.75rem; color:#14B8A6; text-transform:uppercase;
                        letter-spacing:0.1em; margin-bottom:0.8rem;'>
                📋 Caso de estudio del proyecto
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.1em; margin-bottom:0.8rem;'>
                Resultados de la valuación
            </div>
            """, unsafe_allow_html=True)

        # ── Tarjetas de resultado ──────────────────────────────────────────
        for i, res in enumerate(resultados):
            tipo_txt  = "Payer" if res["payer"] else "Receiver"
            pos_color = {"ITM": "#34D399", "ATM": "#14B8A6", "OTM": "#F59E0B"}
            prima_fmt = f"{res['prima']:,.2f}"

            st.markdown(f"""
            <div style='background:#131929; border:1px solid #1E2D45; border-radius:12px;
                        padding:1.2rem 1.5rem; margin-bottom:1rem;'>
                <div style='display:flex; justify-content:space-between;
                            align-items:center; margin-bottom:1rem;'>
                    <div>
                        <span style='color:#94A3B8; font-size:0.75rem; text-transform:uppercase;
                                     letter-spacing:0.08em;'>
                            {tipo_txt} Swaption · tex = 1A · Tenor {res["tenor"]:.1f}A
                        </span>
                    </div>
                    <div style='background:rgba(20,184,166,0.15); border:1px solid rgba(20,184,166,0.4);
                                border-radius:20px; padding:0.15rem 0.7rem;
                                font-size:0.75rem; font-weight:600; color:#14B8A6;'>
                        {res["posicion"]}
                    </div>
                </div>
                <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:1rem;
                            margin-bottom:1rem;'>
                    <div>
                        <div style='font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                    letter-spacing:0.06em;'>Forward ATM</div>
                        <div style='font-size:1.1rem; font-weight:600; color:#F1F5F9;'>
                            {res["f"]*100:.4f}%
                        </div>
                    </div>
                    <div>
                        <div style='font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                    letter-spacing:0.06em;'>Strike K</div>
                        <div style='font-size:1.1rem; font-weight:600; color:#F1F5F9;'>
                            {res["K"]*100:.4f}%
                        </div>
                    </div>
                    <div>
                        <div style='font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                    letter-spacing:0.06em;'>Anualidad A₀</div>
                        <div style='font-size:1.1rem; font-weight:600; color:#F1F5F9;'>
                            {res["A0"]:.4f}
                        </div>
                    </div>
                </div>
                <div style='display:grid; grid-template-columns:repeat(3,1fr); gap:1rem;'>
                    <div>
                        <div style='font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                    letter-spacing:0.06em;'>σ Black (SABR)</div>
                        <div style='font-size:1.3rem; font-weight:700; color:#14B8A6;'>
                            {res["sigma"]*100:.4f}%
                        </div>
                    </div>
                    <div style='grid-column:span 2;'>
                        <div style='font-size:0.72rem; color:#94A3B8; text-transform:uppercase;
                                    letter-spacing:0.06em;'>Prima (MXN)</div>
                        <div style='font-size:1.7rem; font-weight:700; color:#14B8A6;'>
                            ${prima_fmt}
                        </div>
                    </div>
                </div>
                <div style='margin-top:0.8rem; padding-top:0.8rem;
                            border-top:1px solid #1E2D45; font-size:0.78rem; color:#64748B;'>
                    α = {res["alpha"]:.4f} · ρ = {res["rho"]:.3f} · ν = {res["nu"]:.3f}
                    · Nocional: ${res["notional"]:,.0f} MXN
                </div>
            </div>
            """, unsafe_allow_html=True)

        # ── Gráfica smile + strikes ────────────────────────────────────────
        st.plotly_chart(
            fig_smile_comparison(resultados),
            use_container_width=True,
        )

        # ── Tabla comparativa (si hay >1 resultado) ────────────────────────
        if len(resultados) > 1:
            st.markdown("### Comparativa de valuaciones")
            rows_cmp = []
            for res in resultados:
                despl_bp = (res["K"] - res["f"]) * 1e4
                rows_cmp.append({
                    "Strike K (%)":     round(res["K"] * 100, 4),
                    "Δ (pb)":           round(despl_bp, 1),
                    "Moneyness":        res["posicion"],
                    "σ Black (%)":      round(res["sigma"] * 100, 4),
                    "Prima (MXN)":      round(res["prima"], 2),
                    "Prima (pb nocional)": round(res["prima"] / res["notional"] * 1e4, 1),
                })
            df_cmp = pd.DataFrame(rows_cmp)
            st.dataframe(
                df_cmp.style.format({
                    "Strike K (%)": "{:.4f}",
                    "Δ (pb)": "{:.1f}",
                    "σ Black (%)": "{:.4f}",
                    "Prima (MXN)": "{:,.2f}",
                    "Prima (pb nocional)": "{:.1f}",
                }),
                use_container_width=True,
                hide_index=True,
            )

            # Diferencia entre valuaciones
            if len(resultados) == 2:
                diff = resultados[-1]["prima"] - resultados[0]["prima"]
                diff_sigma = (resultados[-1]["sigma"] - resultados[0]["sigma"]) * 1e4
                st.markdown(f"""
                <div style='background:rgba(20,184,166,0.08); border:1px solid rgba(20,184,166,0.3);
                            border-radius:10px; padding:1rem 1.5rem; margin-top:0.5rem;'>
                    <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                                letter-spacing:0.08em; margin-bottom:0.5rem;'>
                        Diferencia entre strikes
                    </div>
                    <div style='display:flex; gap:2rem; flex-wrap:wrap;'>
                        <div>
                            <div style='font-size:0.8rem; color:#94A3B8;'>Δ Prima</div>
                            <div style='font-size:1.3rem; font-weight:700; color:#14B8A6;'>
                                ${diff:,.2f} MXN
                            </div>
                        </div>
                        <div>
                            <div style='font-size:0.8rem; color:#94A3B8;'>Δ Volatilidad</div>
                            <div style='font-size:1.3rem; font-weight:700; color:#F59E0B;'>
                                {diff_sigma:+.1f} pb
                            </div>
                        </div>
                    </div>
                    <div style='font-size:0.82rem; color:#94A3B8; margin-top:0.8rem;
                                line-height:1.5;'>
                        El incremento de prima se debe a dos efectos que se suman:
                        el <strong style='color:#F1F5F9;'>efecto moneyness</strong>
                        (la opción receiver se vuelve más ITM al subir K) y el
                        <strong style='color:#F1F5F9;'>efecto volatilidad</strong>
                        (el skew positivo eleva σ al desplazarse del ATM).
                        Una valuación con vol. constante igual a la ATM habría
                        <strong style='color:#F87171;'>subvaluado</strong> el strike desplazado.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # ── Reset ──────────────────────────────────────────────────────────
        if "caso_estudio" in st.session_state:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button("🔄  Nueva valuación (limpiar caso de estudio)"):
                del st.session_state["caso_estudio"]
                st.rerun()
