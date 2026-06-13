"""
app.py — Portada del dashboard
Streamlit multi-page app: este archivo es la página de inicio (Portada).
"""
import streamlit as st
import os, sys

# ── Asegura que el directorio raíz esté en sys.path ──────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

# ── Config de la app (debe ir antes de cualquier otro st.call) ────────────────
st.set_page_config(
    page_title="SABR · TIIE de Fondeo",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS global ────────────────────────────────────────────────────────────────
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

from core.data import TEAM_MEMBERS

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <div style='font-size:0.7rem; color:#94A3B8; text-transform:uppercase;
                    letter-spacing:0.1em; margin-bottom:0.3rem;'>Proyecto Final</div>
        <div style='font-size:1.05rem; font-weight:700; color:#F1F5F9;
                    line-height:1.3;'>Derivados Avanzados</div>
        <div style='font-size:0.8rem; color:#14B8A6; margin-top:0.2rem;'>FC · UNAM · 2026</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("""
    <div style='font-size:0.75rem; color:#94A3B8; margin-bottom:0.6rem;
                text-transform:uppercase; letter-spacing:0.08em;'>Navegación</div>
    """, unsafe_allow_html=True)

# ── Contenido de la portada ───────────────────────────────────────────────────
col_main, col_right = st.columns([3, 2], gap="large")

with col_main:
    st.markdown("""
    <div style='padding: 2.5rem 0 1rem 0;'>
        <div class='hero-subtitle'>Seminario Avanzado de Derivados · Proyecto Final</div>
        <div class='hero-title' style='margin: 0.8rem 0 1rem 0;'>
            Valuación Estocástica de Opciones sobre Swaps de TIIE de Fondeo
        </div>
        <div style='font-size:1.1rem; color:#94A3B8; font-weight:400; line-height:1.6;
                    max-width:560px;'>
            Calibración del modelo <strong style='color:#F1F5F9'>SABR</strong>
            sobre la superficie de volatilidad Bloomberg VCUB,
            construcción de la curva OIS por <em>bootstrapping</em> directo
            sobre 390 nodos MexDer, y valuación con la fórmula
            <strong style='color:#F1F5F9'>Black-76</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Badges metodológicos
#st.markdown("""
#<div style='margin: 1rem 0 2rem 0;'>
#    <span class='badge'>Curva OIS · 390 nodos</span>
#    <span class='badge'>SABR Hagan et al. (2002)</span>
#    <span class='badge'>Black-76</span>
#    <span class='badge'>Bloomberg VCUB</span>
#    <span class='badge'>TIIE de Fondeo</span>
#    <span class='badge'>β = 1 · Log-normal</span>
#</div>
#""", unsafe_allow_html=True)

    # Datos del proyecto
    st.markdown("""
    <div style='display:flex; gap:1.5rem; flex-wrap:wrap; margin-bottom:2rem;'>
        <div>
            <div style='font-size:0.7rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.08em;'>Fecha de valuación</div>
            <div style='font-size:1rem; color:#F1F5F9; font-weight:600;'>20 de mayo de 2026</div>
        </div>
        <div>
            <div style='font-size:0.7rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.08em;'>Fecha de exposición</div>
            <div style='font-size:1rem; color:#F1F5F9; font-weight:600;'>11 de junio de 2026</div>
        </div>
        <div>
            <div style='font-size:0.7rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.08em;'>Mercado</div>
            <div style='font-size:1rem; color:#F1F5F9; font-weight:600;'>MXN · TIIE de Fondeo</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                padding:1rem 1.5rem; max-width:520px;'>
        <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                    letter-spacing:0.08em; margin-bottom:0.5rem;'>Profesor</div>
        <div style='font-size:1rem; color:#F1F5F9; font-weight:600;'>
        Jorge Humberto del Castillo Spíndola
        </div>
        <div style='font-size:0.85rem; color:#94A3B8; margin-top:0.2rem;'>
            Facultad de Ciencias · Universidad Nacional Autónoma de México
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div style='padding-top:2.5rem;'>
        <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                    letter-spacing:0.1em; margin-bottom:1rem;'>Integrantes del equipo</div>
    """, unsafe_allow_html=True)

    for name, num in TEAM_MEMBERS:
        st.markdown(f"""
        <div class='team-card'>
            <div style='width:32px; height:32px; background:rgba(20,184,166,0.15);
                        border-radius:50%; display:flex; align-items:center;
                        justify-content:center; flex-shrink:0;'>
                <span style='font-size:0.8rem; color:#14B8A6; font-weight:700;'>
                    {name[0]}
                </span>
            </div>
            <div>
                <div style='font-size:0.88rem; color:#F1F5F9; font-weight:500;
                            line-height:1.3;'>{name}</div>
                <div style='font-size:0.72rem; color:#94A3B8;'>{num}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── Divisor y resumen del contenido ──────────────────────────────────────────
st.divider()

st.markdown("""
<div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
            letter-spacing:0.1em; margin-bottom:1rem;'>Estructura del dashboard</div>
""", unsafe_allow_html=True)

cols = st.columns(5, gap="small")
pages_info = [
    ("📖", "Introducción", "Marco teórico: swaptions, Black-76 y la necesidad de SABR"),
    ("⚙️", "Modelo SABR",  "Dinámica estocástica, parámetros y fórmula de Hagan et al."),
    ("📉", "Curva OIS",    "Bootstrapping directo sobre 390 nodos MexDer"),
    ("🎯", "Calibración",  "Calibración SABR anclada al ATM · Superficie de volatilidad"),
    ("💹", "Valuación",    "Calculadora interactiva: elije tenor y strike libremente"),
]

for col, (icon, title, desc) in zip(cols, pages_info):
    with col:
        st.markdown(f"""
        <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                    padding:1rem; height:100%;'>
            <div style='font-size:1.5rem; margin-bottom:0.4rem;'>{icon}</div>
            <div style='font-size:0.9rem; font-weight:600; color:#F1F5F9;
                        margin-bottom:0.4rem;'>{title}</div>
            <div style='font-size:0.78rem; color:#94A3B8; line-height:1.45;'>{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Resumen ejecutivo ─────────────────────────────────────────────────────────
with st.expander("📋  Resumen del proyecto", expanded=False):
    st.markdown("""
    Se desarrolla la **valuación de un swaption europeo** sobre la TIIE de Fondeo
    mediante el modelo de volatilidad estocástica **SABR** (Stochastic Alpha-Beta-Rho),
    calibrado con información de mercado del 20 de mayo de 2026. El estudio integra tres componentes:

    1. **Curva OIS por bootstrapping directo** sobre los 390 precios de liquidación publicados por
       MexDer/Asigna, sin necesidad de interpolación en tramos intermedios.

    2. **Calibración SABR anclada al ATM** empleando la matriz de volatilidades VCUB de Bloomberg
       para el cubo *MXN TIIE-F RFR BVOL*. El anclaje garantiza que el punto más líquido
       (la volatilidad ATM) se reproduzca exactamente por construcción.

    3. **Valuación con Black-76** donde la volatilidad implícita se obtiene de la aproximación
       analítica de Hagan et al. (2002), permitiendo capturar el *skew* y el *smile* que el
       supuesto de volatilidad constante ignora.

    **Resultado clave:** para un *receiver swaption* 1A × 7.5A con nocional de 10 MM MXN,
    la prima ATM asciende a **$263,098 MXN** y sube a **$428,584 MXN** al desplazar el strike
    +50 pb. La diferencia de ~$165,000 MXN ilustra el valor económico de incorporar el *skew*.
    """)

st.markdown("""
<div style='text-align:center; padding:2rem 0 0.5rem 0;
            font-size:0.75rem; color:#475569;'>
    UNAM · Facultad de Ciencias · Seminario Avanzado de Derivados · 2026
</div>
""", unsafe_allow_html=True)
