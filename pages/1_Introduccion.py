"""
pages/1_Introduccion.py — Marco teórico y fundamentos
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Introducción · SABR", page_icon="📖", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem 0;'>
    <div class='hero-subtitle'>Marco teórico</div>
    <h1 style='margin:0.3rem 0; font-size:2rem;'>Introducción y Fundamentos</h1>
    <p style='color:#94A3B8; max-width:700px; line-height:1.6;'>
        Conceptos para comprender la valuación de swaptions sobre la TIIE de Fondeo:
        de la tasa overnight al modelo de volatilidad estocástica.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── 1. Contexto ────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🇲🇽  TIIE de Fondeo",
    "📊  Swaptions",
    "⚫  Black-76",
    "📈  Smile de Volatilidad",
])

with tab1:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown("### De la TIIE 28 a la TIIE de Fondeo")
        st.markdown("""
        El Banco de México sustituyó la **TIIE 28** —basada en encuestas bancarias—
        por la **TIIE de Fondeo**, una tasa de referencia *overnight* construida
        a partir de operaciones de fondeo al mayoreo en pesos.

        **Diferencias fundamentales:**
        """)
        st.markdown("""
        | Característica | TIIE 28 | TIIE de Fondeo |
        |---|---|---|
        | Construcción | Encuestas | Operaciones reales |
        | Plazo base | 28 días | 1 día (*overnight*) |
        | Capitalización | Simple | Diaria compuesta |
        | Esquema de curva | Múltiples curvas | **OIS curva única** |
        """)

        st.markdown("### Consecuencia operativa clave")
        st.markdown("""
        Un **swap de TIIE de Fondeo** con cupones de 28 días paga, en cada periodo,
        la tasa overnight **compuesta diariamente** a lo largo de esos 28 días.

        Bajo el esquema OIS de **curva única**, la pata flotante *telescopea*:
        """)

        st.markdown("""
        <div class='formula-box'>
            <div style='font-size:1.1rem; color:#F1F5F9;'>
                ∑ [DF(T<sub>i−1</sub>) − DF(T<sub>i</sub>)] = 1 − DF(T<sub>n</sub>)
            </div>
            <div style='font-size:0.8rem; color:#94A3B8; margin-top:0.5rem;'>
                El valor presente de la pata flotante colapsa a una diferencia de factores
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info("**Convención Act/360:** fracción de año τ = 28/360 ≈ 0.0778 por cupón de 28 días.")

    with col2:
        st.markdown("### Nivel de tasas en la fecha de valuación")
        st.markdown("""
        <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                    padding:1.2rem; margin-top:0.5rem;'>
        """, unsafe_allow_html=True)

        datos_tasas = {
            "3 meses":  "6.55 %",
            "1 año":    "6.87 %",
            "2 años":   "7.42 %",
            "5 años":   "8.08 %",
            "10 años":  "8.48 %",
            "20 años":  "8.78 %",
            "30 años":  "8.75 %",
        }
        for tenor, tasa in datos_tasas.items():
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between;
                        padding:0.3rem 0; border-bottom:1px solid #1E2D45;'>
                <span style='color:#94A3B8; font-size:0.88rem;'>{tenor}</span>
                <span style='color:#14B8A6; font-weight:600; font-size:0.88rem;'>{tasa}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        </div>
        <div style='margin-top:1rem; font-size:0.8rem; color:#94A3B8;'>
            Fuente: Boletín MexDer/Asigna, 20-may-2026.<br>
            Tasas positivas y elevadas → <strong style='color:#14B8A6'>β = 1</strong>
            (backbone log-normal) es la elección apropiada.
        </div>
        """, unsafe_allow_html=True)


with tab2:
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("### ¿Qué es un Swaption?")
        st.markdown("""
        Un **swaption** es una opción cuyo subyacente es un *forward starting swap*
        (IRS). Otorga el **derecho, mas no la obligación**, de entrar en un IRS en
        la fecha de ejercicio *T_ex*, a cambio de una prima.
        """)

        st.markdown("""
        <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                    padding:1rem 1.5rem; margin:1rem 0;'>
            <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.08em; margin-bottom:0.8rem;'>Tipos</div>
            <div style='margin-bottom:0.8rem;'>
                <div style='color:#14B8A6; font-weight:600; font-size:0.9rem;'>
                    📤 Payer Swaption (Call sobre la tasa)
                </div>
                <div style='color:#94A3B8; font-size:0.82rem; margin-top:0.2rem;'>
                    Derecho a <em>pagar</em> tasa fija K y recibir la flotante.
                    Conviene ejercer si S(T_ex) > K.
                </div>
            </div>
            <div>
                <div style='color:#F59E0B; font-weight:600; font-size:0.9rem;'>
                    📥 Receiver Swaption (Put sobre la tasa)
                </div>
                <div style='color:#94A3B8; font-size:0.82rem; margin-top:0.2rem;'>
                    Derecho a <em>recibir</em> tasa fija K y pagar la flotante.
                    Conviene ejercer si S(T_ex) &lt; K.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Tasa par swap y anualidad")
        st.latex(r"""
        S(t) = \frac{P(t,T_a) - P(t,T_b)}{\sum_{i=a+1}^{b} \tau_i\, P(t,T_i)}
        = \frac{P(t,T_a) - P(t,T_b)}{A(t)}
        """)
        st.markdown("Donde **A(t)** es la **anualidad** (PV01 del swap), que actúa como *numéraire* natural del problema.")

    with col2:
        st.markdown("### Payoffs")
        st.markdown("""
        <div class='formula-box' style='margin-bottom:1rem;'>
            <div style='font-size:0.8rem; color:#14B8A6; margin-bottom:0.3rem;'>
                PAYER SWAPTION
            </div>
            <div style='font-size:1rem; color:#F1F5F9;'>
                Payoff = N · A(T_ex) · [S(T_ex) − K]<sup>+</sup>
            </div>
        </div>
        <div class='formula-box'>
            <div style='font-size:0.8rem; color:#F59E0B; margin-bottom:0.3rem;'>
                RECEIVER SWAPTION
            </div>
            <div style='font-size:1rem; color:#F1F5F9;'>
                Payoff = N · A(T_ex) · [K − S(T_ex)]<sup>+</sup>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### Moneyness")
        st.markdown("""
        | | K < f | K = f | K > f |
        |---|---|---|---|
        | **Payer** | ITM | ATM | OTM |
        | **Receiver** | OTM | ATM | ITM |

        Las opciones **ATM** son las más líquidas y sirven como referencia para cotizar volatilidad.
        """)


with tab3:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown("### Fórmula de Black-76")
        st.markdown("""
        Valuación de un swaption europeo suponiendo que la **tasa forward es log-normal**
        con volatilidad constante σ en [t, T]:
        """)
        st.latex(r"""
        V = N\,A_0\,w\bigl[f\,\mathcal{N}(w\,d_1) - K\,\mathcal{N}(w\,d_2)\bigr]
        """)
        st.latex(r"""
        d_1 = \frac{\ln(f/K) + \tfrac{1}{2}\sigma^2 t_{ex}}{\sigma\sqrt{t_{ex}}},
        \qquad
        d_2 = d_1 - \sigma\sqrt{t_{ex}}
        """)
        st.markdown("""
        donde **w = +1** para payer (call sobre la tasa) y **w = −1** para receiver (put).
        """)

        st.markdown("### Fundamento: medida swap")
        st.markdown("""
        La anualidad **A₀** actúa como *numéraire*. Bajo la **medida swap**
        (o medida anualidad), la tasa forward *f* es una **martingala**.
        El payoff descontado conduce exactamente a la expresión anterior.

        Esta fórmula es válida sin suponer normalidad en el mundo real —sólo
        requiere que *f* sea martingala bajo la medida anualidad.
        """)

    with col2:
        st.markdown("### Limitación central")
        st.markdown("""
        <div class='warning-box'>
            <div style='color:#F59E0B; font-weight:600; margin-bottom:0.3rem;'>
                ⚠️ Supuesto de volatilidad constante
            </div>
            <div style='color:#94A3B8; font-size:0.85rem; line-height:1.5;'>
                Black-76 asume σ constante para todos los strikes y plazos.
                En la práctica, la volatilidad implícita <em>varía sistemáticamente</em>
                con el strike (smile/skew) y el plazo — contradiciendo el supuesto.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:1rem; background:#131929; border:1px solid #1E2D45;
                    border-radius:10px; padding:1rem;'>
            <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.08em; margin-bottom:0.5rem;'>
                Black-76 en la práctica
            </div>
            <div style='font-size:0.85rem; color:#F1F5F9; line-height:1.5;'>
                Se usa como <strong>lenguaje de cotización</strong>: traduce primas a
                volatilidades implícitas (y viceversa) mediante Newton-Raphson,
                pero <em>no explica</em> por qué la volatilidad varía con el strike.
                Esa tensión es la que SABR resuelve.
            </div>
        </div>
        """, unsafe_allow_html=True)


with tab4:
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("### El smile / skew de volatilidad")
        st.markdown("""
        La **volatilidad implícita** es el σ que, sustituido en Black-76,
        reproduce el precio observado. Si se grafica vs. el strike para un plazo fijo,
        rara vez es plana:

        - **Smile:** mayor volatilidad en los extremos que en el centro
          (colas más gruesas que log-normal).
        - **Skew:** pendiente sistemática; en tasas de interés MXN se observa
          **skew positivo** (mayor vol en strikes altos → el mercado asigna
          más incertidumbre a escenarios de tasas elevadas).
        """)

        st.markdown("""
        <div class='step-box'>
            <strong style='color:#14B8A6;'>¿Por qué importa?</strong><br>
            <span style='font-size:0.85rem; color:#94A3B8;'>
            Una vol plana subvalúa/sobrevalúa sistemáticamente las opciones OTM e ITM.
            El error puede ser de decenas o cientos de miles de pesos en un contrato
            real de swaption.
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### La superficie de volatilidad")
        st.markdown("""
        La superficie completa es una **función de dos variables**: el strike
        (o moneyness K/f) y el plazo. Un modelo paramétrico adecuado debe ser:
        """)
        items = [
            ("🎯", "Fiel", "Reproduce las cotizaciones observadas"),
            ("〰️", "Suave", "Sin discontinuidades artificiales en las griegas"),
            ("⚖️", "Libre de arbitraje", "Compatible con la existencia de una medida de riesgo neutral"),
        ]
        for icon, title, desc in items:
            st.markdown(f"""
            <div style='display:flex; gap:0.8rem; align-items:flex-start;
                        padding:0.6rem 0; border-bottom:1px solid #1E2D45;'>
                <div style='font-size:1.1rem;'>{icon}</div>
                <div>
                    <div style='color:#F1F5F9; font-weight:600; font-size:0.9rem;'>{title}</div>
                    <div style='color:#94A3B8; font-size:0.82rem;'>{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:1rem; font-size:0.85rem; color:#94A3B8;'>
            Estas tres propiedades no se satisfacen con interpolación de vols crudas.
            Son la razón de ser de modelos como <strong style='color:#14B8A6;'>SABR</strong>.
        </div>
        """, unsafe_allow_html=True)
