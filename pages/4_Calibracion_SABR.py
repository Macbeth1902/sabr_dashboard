"""
pages/4_Calibracion_SABR.py — Calibración SABR y superficie de volatilidad

"""
import streamlit as st
import numpy as np
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Calibración SABR", page_icon="🎯", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

from core.state import get_curve, get_calibration
from core.data import TENOR_LBL_SW, ATM_N
from core.sabr import sabr_ln_vol
from core.data import BETA, EXPIRY_FIX
from core.charts import (
    fig_vcub_heatmap,
    fig_calibration_params,
    fig_sabr_surface,
    fig_sabr_smile,
    fig_param_sensitivity,
)

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem 0;'>
    <div class='hero-subtitle'>Resultados</div>
    <h1 style='margin:0.3rem 0; font-size:2rem;'>Calibración SABR Anclada al ATM</h1>
    <p style='color:#94A3B8; max-width:700px; line-height:1.6;'>
        19 tenores calibrados contra la matriz VCUB de Bloomberg.
        β = 1 fijo; α anclado al ATM; (ρ, ν) optimizados sobre las alas.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Cálculos cacheados ──────────────────────────────────────────────────────
with st.spinner("Calibrando modelo SABR (primera ejecución puede tardar ~10 s)…"):
    curve  = get_curve()
    result = get_calibration()

calib    = result["calib"]
TEN_GRID = result["TEN_GRID"]
AL_GRID  = result["AL_GRID"]
RH_GRID  = result["RH_GRID"]
NU_GRID  = result["NU_GRID"]

# ── KPIs del tramo estable (1Yr–30Yr) ──────────────────────────────────────
rmse_stable = [calib[l]["rmse"] * 1e4 for l in TENOR_LBL_SW[4:]]
rho_stable  = [calib[l]["rho"]        for l in TENOR_LBL_SW[4:]]
nu_stable   = [calib[l]["nu"]         for l in TENOR_LBL_SW[4:]]

c1, c2, c3, c4 = st.columns(4)
kpis = [
    ("RMSE promedio (1Yr–30Yr)", f"{np.mean(rmse_stable):.1f} pb",  "Tramo estable"),
    ("ρ promedio (1Yr–30Yr)",    f"{np.mean(rho_stable):.3f}",       "Skew positivo"),
    ("ν promedio (1Yr–30Yr)",    f"{np.mean(nu_stable):.3f}",        "Curvatura moderada"),
    ("Tenores calibrados",        "19",                               "1Mo … 30Yr"),
]
for col, (label, value, sub) in zip([c1,c2,c3,c4], kpis):
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='label'>{label}</div>
            <div class='value'>{value}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️  Matriz VCUB",
    "📊  Parámetros calibrados",
    "🌊  Superficie SABR 3D",
    "🎛️  Análisis de sensibilidad",
    "🔧  Calibración"
])

# ── Tab 1: Heatmap VCUB ────────────────────────────────────────────────────
with tab1:
    st.image("images/bloomberg.jpeg", width="stretch")
    # st.plotly_chart(fig_vcub_heatmap(), use_container_width=True)

    st.markdown("""
    <div style='display:flex; gap:1rem; flex-wrap:wrap; margin-top:0.5rem;'>
        <div class='step-box' style='flex:1; min-width:220px;'>
            <strong style='color:#14B8A6; font-size:0.88rem;'>Vencimiento fijo</strong><br>
            <span style='color:#94A3B8; font-size:0.82rem;'>
            tex = 1 año para toda la matriz.
            </span>
        </div>
        <div class='step-box' style='flex:1; min-width:220px;'>
            <strong style='color:#14B8A6; font-size:0.88rem;'>Filas → Tenor del swap</strong><br>
            <span style='color:#94A3B8; font-size:0.82rem;'>
            1Mo, 3Mo, …, 30Yr (19 nodos).
            </span>
        </div>
        <div class='step-box' style='flex:1; min-width:220px;'>
            <strong style='color:#14B8A6; font-size:0.88rem;'>Columnas → Moneyness</strong><br>
            <span style='color:#94A3B8; font-size:0.82rem;'>
            −300 pb a +300 pb respecto al forward ATM.
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Tab 2: Parámetros calibrados ───────────────────────────────────────────
with tab2:
    # Tabla de calibración
    rows = []
    for lbl, atmn in zip(TENOR_LBL_SW, ATM_N):
        c = calib[lbl]
        atm_fit = float(sabr_ln_vol(c["f"], c["f"], c["T"], c["alpha"], BETA, c["rho"], c["nu"]))
        rows.append({
            "Tenor":        lbl,
            "Fwd (%)":      round(c["f"] * 100, 3),
            "ATM Mkt (%)":  round(atmn * 100, 2),
            "α":            round(c["alpha"], 4),
            "ρ":            round(c["rho"], 3),
            "ν":            round(c["nu"], 3),
            "RMSE (pb)":    round(c["rmse"] * 1e4, 2),
            "ATM Fit (%)":  round(atm_fit * 100, 3),
        })

    df_calib = pd.DataFrame(rows)

    def highlight_rmse(val):
        if val > 15:
            return "color: #F87171"
        elif val > 8:
            return "color: #F59E0B"
        else:
            return "color: #34D399"

    st.dataframe(
        df_calib.style
                .map(highlight_rmse, subset=["RMSE (pb)"])
                .format({
                    "Fwd (%)": "{:.3f}",
                    "ATM Mkt (%)": "{:.2f}",
                    "α": "{:.4f}",
                    "ρ": "{:.3f}",
                    "ν": "{:.3f}",
                    "RMSE (pb)": "{:.2f}",
                    "ATM Fit (%)": "{:.3f}",
                }),
        use_container_width=True,
        hide_index=True,
        height=560,
    )

    st.markdown("""
    <div style='margin-top:0.5rem; font-size:0.8rem; color:#94A3B8;'>
        🟢 RMSE ≤ 8 pb · 🟡 8–15 pb · 🔴 > 15 pb (tramo corto con iliquidez)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # st.plotly_chart(fig_calibration_params(calib), use_container_width=True)
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.markdown("""
    #     <div class='warning-box'>
    #         <strong style='color:#F59E0B;'>Tramo corto (1Mo–9Mo)</strong><br>
    #         <span style='color:#94A3B8; font-size:0.83rem;'>
    #         ν > 1 y RMSE de 27–30 pb. La sonrisa observada es muy pronunciada,
    #         posiblemente afectada por iliquidez. Estos nodos son los menos estables.
    #         </span>
    #     </div>
    #     """, unsafe_allow_html=True)
    # with col2:
    #     st.markdown("""
    #     <div class='result-highlight'>
    #         <strong style='color:#14B8A6;'>Tramo medio-largo (1Yr–30Yr)</strong><br>
    #         <span style='color:#94A3B8; font-size:0.83rem;'>
    #         ρ ∈ [0.32, 0.37], ν ≈ 0.50–0.52 y RMSE de 6–8 pb.
    #         La estabilidad de los parámetros permite interpolar linealmente
    #         sin re-optimización para tenores intermedios.
    #         </span>
    #     </div>
    #     """, unsafe_allow_html=True)


# ── Tab 3: Superficie 3D ───────────────────────────────────────────────────
with tab3:
    st.image("images/sabr.png", width=800)
    # st.plotly_chart(fig_sabr_surface(calib), use_container_width=True)

    st.markdown("""
    <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                padding:1rem 1.5rem; margin-top:0.5rem;'>
        <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                    letter-spacing:0.08em; margin-bottom:0.5rem;'>
            Interpretación de la superficie
        </div>
        <div style='color:#F1F5F9; font-size:0.88rem; line-height:1.6;'>
            La superficie es <strong>suave</strong> en el tramo de tenores medios y largos
            (1Yr–30Yr), con niveles de volatilidad de 13 % a 17 %, formando un "valle" estable.
            El tramo corto no se muestra para mayor claridad. La pendiente positiva
            en el eje de moneyness refleja el <strong style='color:#14B8A6;'>skew positivo</strong>
            calibrado (ρ > 0): a mayor strike, mayor volatilidad.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Tab 4: Sensibilidad ────────────────────────────────────────────────────
with tab4:
    st.markdown("### Efecto aislado de cada parámetro SABR")
    st.markdown("""
    Se varía un parámetro a la vez manteniendo los demás en sus valores calibrados.
    Selecciona un tenor de referencia y el parámetro a analizar.
    """)

    # Selector de tenor (tramo estable)
    tenores_estables = TENOR_LBL_SW[4:]  # desde 1Yr
    col_sel1, col_sel2, _ = st.columns([1, 1, 2])
    with col_sel1:
        tenor_ref = st.selectbox(
            "Tenor de referencia",
            options=tenores_estables,
            index=tenores_estables.index("10Yr"),
            key="sens_tenor",
        )
    with col_sel2:
        param_sel = st.selectbox(
            "Parámetro a variar",
            options=["rho", "nu", "alpha"],
            format_func=lambda x: {"rho": "ρ  (skew / inclinación)",
                                   "nu":  "ν  (smile / curvatura)",
                                   "alpha": "α  (nivel via vol ATM)"}[x],
            key="sens_param",
        )

    st.plotly_chart(
        fig_param_sensitivity(calib, tenor_ref, param_sel),
        use_container_width=True,
    )

    # Smile calibrado vs. mercado
    st.markdown("### Smile SABR vs. datos de mercado")
    col_s1, col_s2, _ = st.columns([1, 1, 2])
    with col_s1:
        tenor_smile = st.selectbox(
            "Tenor del smile",
            options=TENOR_LBL_SW,
            index=TENOR_LBL_SW.index("10Yr"),
            key="smile_tenor",
        )

    st.plotly_chart(
        fig_sabr_smile(calib, tenor_smile),
        use_container_width=True,
    )

    c = calib[tenor_smile]
    rmse_bp = c["rmse"] * 1e4
    color_rmse = "#34D399" if rmse_bp <= 8 else ("#F59E0B" if rmse_bp <= 15 else "#F87171")
    st.markdown(f"""
    <div style='display:flex; gap:1.5rem; flex-wrap:wrap; margin-top:0.5rem;'>
        <div>
            <span style='color:#94A3B8; font-size:0.8rem;'>α = </span>
            <span style='color:#14B8A6; font-weight:600;'>{c['alpha']:.4f}</span>
        </div>
        <div>
            <span style='color:#94A3B8; font-size:0.8rem;'>ρ = </span>
            <span style='color:#F59E0B; font-weight:600;'>{c['rho']:.3f}</span>
        </div>
        <div>
            <span style='color:#94A3B8; font-size:0.8rem;'>ν = </span>
            <span style='color:#60A5FA; font-weight:600;'>{c['nu']:.3f}</span>
        </div>
        <div>
            <span style='color:#94A3B8; font-size:0.8rem;'>RMSE = </span>
            <span style='color:{color_rmse}; font-weight:600;'>{rmse_bp:.2f} pb</span>
        </div>
        <div>
            <span style='color:#94A3B8; font-size:0.8rem;'>Forward = </span>
            <span style='color:#F1F5F9; font-weight:600;'>{c['f']*100:.3f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Tab 5: Calibración ────────────────────────────────────────────────────
with tab5:
     col1, col2 = st.columns([3, 2], gap="large")
     with col1:
         st.markdown("### Algoritmo de calibración anclada al ATM")
         st.markdown("""
         La práctica de mercado (Hagan et al. 2002, Cortés González 2017) es **fijar β**
         y luego calibrar los tres parámetros restantes. Para swaptions, conviene
         **reparametrizar en σ_ATM**, reduciendo el problema a sólo **dos parámetros libres**.
         """)

         steps = [
             ("1", "Forward y anualidad",
              "Se calculan f y A₀ del swap 1Y × tenor con la curva OIS."),
             ("2", "Strikes absolutos",
              "K_i = f + Δ_i. Se descartan K_i ≤ 0 y se filtra la banda |K_i/f − 1| ≤ 0.55."),
             ("3", "Anclaje de α",
              "Para cada par (ρ, ν), se resuelve σ_B(f,f;α,β,ρ,ν) = σ_ATM^MKT con Brent. "
              "Garantiza que el ATM se reproduzca exactamente."),
             ("4", "Residuales OTM/ITM",
              "Se evalúa σ_B(K_i,f) − σ_i^MKT sólo en strikes ≠ ATM (el ATM ya está fijo)."),
             ("5", "Minimización",
              "min_{ρ,ν} Σ_{K≠ATM} (σ_B − σ^MKT)² con least_squares (Trust Region Reflective), "
              "ρ ∈ [−0.999, 0.999], ν ∈ [10⁻⁴, 5]."),
         ]

         for num, title, desc in steps:
             st.markdown(f"""
             <div style='display:flex; gap:1rem; padding:0.7rem 0;
                         border-bottom:1px solid #1E2D45;'>
                 <div style='color:#14B8A6; font-weight:700; font-size:0.9rem;
                             flex-shrink:0; width:18px;'>{num}.</div>
                 <div>
                     <div style='color:#F1F5F9; font-weight:600; font-size:0.88rem;'>{title}</div>
                     <div style='color:#94A3B8; font-size:0.82rem; line-height:1.4;
                                 margin-top:0.15rem;'>{desc}</div>
                 </div>
             </div>
             """, unsafe_allow_html=True)

     with col2:
         st.markdown("### Elección de β = 1")
         st.markdown("""
         <div class='result-highlight' style='margin-bottom:1rem;'>
             <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                         letter-spacing:0.08em; margin-bottom:0.4rem;'>Justificación</div>
             <div style='font-size:0.85rem; color:#F1F5F9; line-height:1.5;'>
                 La TIIE de Fondeo presenta niveles <strong>positivos y elevados</strong>
                 (6.5 % – 8.8 % a lo largo de la curva). El backbone log-normal (β = 1)
                 es coherente con tasas que no pueden volverse negativas en este régimen.
             </div>
         </div>
         """, unsafe_allow_html=True)

         st.markdown("### Ventaja del anclaje")
         st.markdown("""
         <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                     padding:1.2rem;'>
             <div style='font-size:0.85rem; color:#F1F5F9; line-height:1.5;'>
                 El anclaje convierte un problema de <strong style='color:#14B8A6;'>3 parámetros</strong>
                 en uno de <strong style='color:#14B8A6;'>2 parámetros libres</strong>.
             </div>
             <div style='margin-top:0.8rem;'>
                 <div style='font-size:0.8rem; color:#94A3B8; margin-bottom:0.3rem;'>Consecuencias:</div>
                 <div style='font-size:0.82rem; color:#34D399;'>
                     ✓ El dato más líquido (ATM) se reproduce exactamente
                 </div>
                 <div style='font-size:0.82rem; color:#34D399; margin-top:0.2rem;'>
                     ✓ ρ y ν se ocupan sólo de capturar skew y curvatura
                 </div>
                 <div style='font-size:0.82rem; color:#34D399; margin-top:0.2rem;'>
                     ✓ Optimización más estable y rápida
                 </div>
             </div>
         </div>
         """, unsafe_allow_html=True)
