"""
pages/6_Conclusiones.py — Conclusiones e interpretaciones
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Conclusiones · SABR", page_icon="📝", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem 0;'>
    <div class='hero-subtitle'>Cierre del proyecto</div>
    <h1 style='margin:0.3rem 0; font-size:2rem;'>Conclusiones e Interpretaciones</h1>
    <p style='color:#94A3B8; max-width:720px; line-height:1.6;'>
        Síntesis de los hallazgos, implicaciones para la práctica de mercado
        y extensiones futuras del modelo.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

# ── Caso de estudio — números clave ────────────────────────────────────────
st.markdown("""
<div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
            letter-spacing:0.1em; margin-bottom:0.8rem;'>
    Caso de estudio · Receiver Swaption 1A × 7.5A · Nocional 10 MM MXN
</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
kpis_caso = [
    ("Forward ATM",   "8.6662 %",     "interpolado entre 7Yr y 8Yr"),
    ("Vol ATM (SABR)","14.8050 %",    "σ_B(f, f) con β = 1"),
    ("Prima ATM",     "$263,098 MXN", "receiver, K = f"),
    ("Prima +50 pb",  "$428,584 MXN", "receiver, K = f + 0.005"),
    ("Diferencia",    "+$165,486 MXN","efecto moneyness + skew"),
]
for col, (label, value, sub) in zip([c1,c2,c3,c4,c5], kpis_caso):
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='label'>{label}</div>
            <div class='value' style='font-size:1.15rem;'>{value}</div>
            <div class='sub'>{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Conclusiones principales ────────────────────────────────────────────────
conclusiones = [
    {
        "icon": "📈",
        "titulo": "SABR supera a la volatilidad constante",
        "color": "#14B8A6",
        "texto": (
            "El modelo SABR resuelve la limitación central del supuesto de volatilidad constante "
            "de Black-76: la dependencia de la volatilidad implícita respecto del strike. "
            "Mientras que una volatilidad plana subvalúa o sobrevalúa sistemáticamente las opciones "
            "fuera del ATM, SABR reproduce el <strong style='color:#F1F5F9;'>skew</strong> y el "
            "<strong style='color:#F1F5F9;'>smile</strong> observados en el mercado."
        ),
        "destacado": (
            "En el caso de estudio, ignorar el skew habría implicado un error de valuación "
            "de ~$165,000 MXN en el strike de +50 pb, donde la volatilidad de mercado es "
            "casi 60 pb superior a la ATM."
        ),
    },
    {
        "icon": "⚓",
        "titulo": "El anclaje al ATM es un acierto metodológico",
        "color": "#60A5FA",
        "texto": (
            "El anclaje al ATM garantiza que el dato más líquido y confiable se reproduzca "
            "exactamente por construcción, reduciendo el problema a sólo dos parámetros libres "
            "(ρ, ν). Esto estabiliza la optimización y produce dos regímenes bien diferenciados: "
            "el tramo corto (1Mo–9Mo) con ν > 1 y RMSE de 27–30 pb, que debe tratarse con cautela; "
            "y el tramo medio-largo (1Yr–30Yr) con ρ ∈ [0.32, 0.37], ν ≈ 0.50–0.52 "
            "y RMSE de 6–8 pb."
        ),
        "destacado": (
            "La estabilidad de los parámetros en el tramo 1Yr–30Yr justifica interpolar "
            "linealmente sin re-optimización, a diferencia de trabajos con mallas de vencimiento más pobres."
        ),
    },
    {
        "icon": "🇲🇽",
        "titulo": "Pertinencia del modelo para la TIIE de Fondeo",
        "color": "#F59E0B",
        "texto": (
            "En mercados muy líquidos con numerosos strikes cotizando, SABR pierde ventaja "
            "relativa. En el caso de la TIIE de Fondeo, cuya superficie de swaptions no presenta "
            "gran profundidad —el Boletín MexDer registró apenas 4 operaciones en el día analizado—, "
            "<strong style='color:#F1F5F9;'>SABR es la elección adecuada</strong>: genera una "
            "sonrisa completa a partir de pocos datos de mercado."
        ),
        "destacado": (
            "La decisión de adoptar los 390 nodos de la curva oficial de MexDer, en lugar de "
            "los pocos nodos con operación, fue determinante para disponer de un tramo largo "
            "bien definido sin introducir hipótesis discrecionales."
        ),
    },
    {
        "icon": "🔄",
        "titulo": "Impacto de la transición TIIE 28 → TIIE de Fondeo",
        "color": "#F472B6",
        "texto": (
            "La transición no es un mero cambio de nombre: reconfigura la curva de descuento "
            "hacia un esquema OIS de curva única que simplifica el bootstrapping a una recursión "
            "cerrada gracias al colapso telescópico de la pata flotante. El backbone log-normal "
            "(β = 1) es coherente con el régimen actual de tasas positivas y elevadas; en un "
            "eventual escenario de tasas muy bajas o negativas, la convención apropiada sería β = 0."
        ),
        "destacado": (
            "La metodología es robusta y adaptable a la nueva infraestructura de tasas del mercado mexicano."
        ),
    },
]

for con in conclusiones:
    col_icon, col_text = st.columns([1, 11], gap="small")
    with col_icon:
        st.markdown(f"""
        <div style='width:44px; height:44px; background:rgba(20,184,166,0.1);
                    border:1px solid {con["color"]}44; border-radius:10px;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.3rem; margin-top:0.2rem;'>
            {con["icon"]}
        </div>
        """, unsafe_allow_html=True)
    with col_text:
        st.markdown(f"""
        <div style='background:#131929; border:1px solid #1E2D45; border-left:3px solid {con["color"]};
                    border-radius:0 10px 10px 0; padding:1rem 1.5rem; margin-bottom:1rem;'>
            <div style='font-size:1rem; font-weight:600; color:#F1F5F9;
                        margin-bottom:0.5rem;'>{con["titulo"]}</div>
            <div style='font-size:0.85rem; color:#94A3B8; line-height:1.6;
                        margin-bottom:0.6rem;'>{con["texto"]}</div>
            <div style='font-size:0.82rem; color:#F1F5F9; background:rgba(20,184,166,0.06);
                        border:1px solid rgba(20,184,166,0.2); border-radius:6px;
                        padding:0.5rem 0.8rem; line-height:1.5;'>
                💡 {con["destacado"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Referencias ────────────────────────────────────────────────────────────
with st.expander("📚  Referencias bibliográficas"):
    refs = [
        ("[1]", "Hagan, P. S., Kumar, D., Lesniewski, A. S. & Woodward, D. E. (2002). "
                "<em>Managing Smile Risk</em>. Wilmott Magazine, pp. 84–108."),
        ("[2]", "Cortés González, L. (2017). <em>Modelo SABR para la estimación de la volatilidad "
                "en una opción de TIIE28</em>. Tesis de licenciatura en Actuaría, UNAM."),
        ("[3]", "Black, F. & Scholes, M. (1973). <em>The Pricing of Options and Corporate Liabilities</em>. "
                "Journal of Political Economy, 81(3), pp. 637–654."),
        ("[4]", "Banco de México / BMV. <em>Swap de TIIE de Fondeo y conversión de tasas</em> "
                "(convención overnight compuesta, 28 días, Act/360)."),
        ("[5]", "MexDer / Asigna (2026). <em>Boletín de Swaps: Precios e Interés Abierto</em>, "
                "20 de mayo de 2026. 390 precios de liquidación de swaps de TIIE de Fondeo."),
        ("[6]", "Bloomberg L.P. <em>VCUB — MXN TIIE-F RFR BVOL Cube</em> "
                "(matriz de volatilidades, índice 1D, vista de vencimiento 1YR)."),
        ("[7]", "Del Castillo Spíndola, J. H. <em>Superficies de Volatilidad para TIIE — SABR para TIIE</em>. "
                "Mesa de Volatilidad de Tasas, Mercados Globales, BBVA Bancomer; "
                "1.er Congreso de Riesgos, Facultad de Ciencias, UNAM, 2016."),
    ]
    for num, ref in refs:
        st.markdown(f"""
        <div style='display:flex; gap:0.8rem; padding:0.5rem 0; border-bottom:1px solid #1E2D45;'>
            <div style='color:#14B8A6; font-weight:600; font-size:0.82rem;
                        flex-shrink:0; width:28px;'>{num}</div>
            <div style='color:#94A3B8; font-size:0.82rem; line-height:1.5;'>{ref}</div>
        </div>
        """, unsafe_allow_html=True)
