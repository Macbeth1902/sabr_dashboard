"""
pages/3_Curva_OIS.py — Construcción de la curva OIS por bootstrapping
"""
import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Curva OIS · SABR", page_icon="📉", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

from core.state import get_curve
from core.data import NODES_REP, PAR_REP, TENOR_LBL_REP
from core.charts import fig_curva_ois, fig_forward_curve

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem 0;'>
    <div class='hero-subtitle'>Metodología</div>
    <h1 style='margin:0.3rem 0; font-size:2rem;'>Curva OIS por Bootstrapping Directo</h1>
    <p style='color:#94A3B8; max-width:700px; line-height:1.6;'>
        390 precios de liquidación del Boletín MexDer/Asigna → factores de descuento
        nodo a nodo, sin interpolación.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Cálculo (cacheado) ──────────────────────────────────────────────────────
with st.spinner("Construyendo curva OIS…"):
    curve = get_curve()

DF    = curve["DF"]
years = curve["years"]
zero  = curve["zero"]
fwd28 = curve["fwd28"]
df_curva = curve["df"]

# ── KPIs rápidos ────────────────────────────────────────────────────────────
st.markdown("""
<div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
            letter-spacing:0.08em; margin-bottom:0.8rem;'>Resumen de la curva</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    ("Nodos", "390", "de 28 a 10,920 días"),
    ("DF (1 año)", f"{DF[13]:.6f}", "nodo 13F1"),
    ("Tasa cero (1A)", f"{zero[13]*100:.4f}%", "continua anual"),
    ("Tasa cero (10A)", f"{zero[130]*100:.4f}%", "continua anual"),
    ("DF (30A)", f"{DF[390]:.6f}", "≈ 30.33 años"),
]
for col, (label, value, sub) in zip([c1,c2,c3,c4,c5], kpis):
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
#tab1, tab2, tab3 = st.tabs([
#    "📊  Gráficas de la curva",
#    "🔢  Matemática del bootstrapping",
#    "📋  Tabla de resultados",
#])

tab1, tab2 = st.tabs([
    "🔢  Matemática del bootstrapping",
    "📋  Tabla de resultados",
])

#with tab1:
#    st.plotly_chart(
#        fig_curva_ois(years, zero, fwd28, NODES_REP, PAR_REP),
#        use_container_width=True,
#    )
#    st.markdown("<br>", unsafe_allow_html=True)
#    st.plotly_chart(
#        fig_forward_curve(years, fwd28),
#        use_container_width=True,
#    )

#    st.markdown("""
#    <div class='warning-box' style='margin-top:0.5rem;'>
#        <strong style='color:#F59E0B;'>Interpretación:</strong>
#        <span style='color:#94A3B8; font-size:0.85rem;'>
#        La tasa cero continua es <em>enteramente ascendente</em>: parte de 6.54 % en el plazo
#        más corto, alcanza un máximo cercano a 9.05 % en torno a los 20 años y desciende
#        ligeramente hacia el extremo de 30 años (8.84 %). Los puntos negros señalan los
#        nodos representativos del boletín.
#        </span>
#    </div>
#    """, unsafe_allow_html=True)

with tab1:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown("### Fórmula de bootstrapping directo")
        st.markdown("""
        Cada nodo *nF1* es un swap de TIIE de Fondeo con *n* cupones de 28 días.
        Bajo curva única OIS, la pata flotante **telescopea**:
        """)
        st.latex(r"""
        \sum_{i=1}^{n}\bigl[DF(T_{i-1}) - DF(T_i)\bigr] = 1 - DF(T_n)
        """)

        st.markdown("Igualando pata fija (a tasa par Sₙ) con pata flotante:")
        st.latex(r"""
        S_n \sum_{i=1}^{n} \tau\,DF(T_i) = 1 - DF(T_n)
        """)

        st.markdown("Separando el último término y resolviendo para DF(Tₙ):")
        st.latex(r"""
        \boxed{DF(T_n) = \frac{1 - S_n\,A_{n-1}}{1 + S_n\,\tau}}
        """)
        st.markdown("""
        donde **A_{n−1} = Σ τ·DF(T_i)** es la anualidad acumulada de los *n−1* cupones
        anteriores, ya conocida en la recursión.

        **Tasas derivadas:**
        """)
        st.latex(r"""
        r(T_n) = -\frac{\ln DF(T_n)}{T_n}, \qquad
        f^{28}_n = \frac{1}{\tau}\!\left(\frac{DF(T_{n-1})}{DF(T_n)}-1\right)
        """)

    with col2:
        st.markdown("### Justificación de los 390 nodos")
        items = [
            ("Problema de liquidez puntual",
             "El boletín del 20-may-2026 registró sólo 4 operaciones concentradas en 3 nodos. "
             "Usar sólo nodos con operación dejaría el tramo largo indeterminado."),
            ("Curva oficial y libre de arbitraje",
             "Los 390 precios los calcula Asigna/MexDer con su metodología oficial, "
             "que sustenta la liquidación de posiciones de toda la cámara. "
             "Es suave y libre de arbitraje por construcción."),
            ("Bootstrapping directo sin interpolación",
             "Un precio par por nodo → un DF por nodo → solución cerrada. "
             "No se introducen hipótesis discrecionales en tramos intermedios."),
        ]
        for title, desc in items:
            st.markdown(f"""
            <div class='step-box' style='margin-bottom:0.6rem;'>
                <strong style='color:#14B8A6; font-size:0.88rem;'>{title}</strong><br>
                <span style='color:#94A3B8; font-size:0.81rem; line-height:1.4;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)


with tab2:
    st.markdown("### Nodos representativos de la curva OIS")

    import pandas as pd
    df_rep = pd.DataFrame({
        "Tenor":          TENOR_LBL_REP,
        "Nodo nF1":       NODES_REP,
        "Tasa par (%)":   PAR_REP,
        "DF":             [DF[n] for n in NODES_REP],
        "Tasa cero (%)":  [-np.log(DF[n])/(n*28/360)*100 for n in NODES_REP],
    })
    st.dataframe(
        df_rep.style
              .format({"Tasa par (%)": "{:.2f}", "DF": "{:.6f}", "Tasa cero (%)": "{:.4f}"})
              .background_gradient(subset=["DF"], cmap="Blues_r")
              .background_gradient(subset=["Tasa cero (%)"], cmap="YlOrRd"),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Primeras y últimas filas (todos los nodos)")

    df_show = pd.concat([df_curva.head(8), df_curva.tail(5)])
    st.dataframe(
        df_show.style.format({
            "Plazo (años)": "{:.4f}",
            "DF":           "{:.6f}",
            "Tasa cero cont. (%)": "{:.4f}",
            "Fwd 28d (%)": "{:.4f}",
        }),
        use_container_width=True,
        hide_index=True,
    )