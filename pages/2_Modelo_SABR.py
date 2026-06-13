"""
pages/2_Modelo_SABR.py — El modelo SABR
"""
import streamlit as st
import numpy as np
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(page_title="Modelo SABR", page_icon="⚙️", layout="wide")

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css()

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:1.5rem 0 0.5rem 0;'>
    <div class='hero-subtitle'>Volatilidad Estocástica</div>
    <h1 style='margin:0.3rem 0; font-size:2rem;'>El Modelo SABR</h1>
    <p style='color:#94A3B8; max-width:700px; line-height:1.6;'>
        Hagan, Kumar, Lesniewski & Woodward (2002) — el modelo de volatilidad
        estocástica más utilizado en mercados de tasas de interés.
    </p>
</div>
""", unsafe_allow_html=True)
st.divider()

#tab1, tab2, tab3, tab4 = st.tabs([
#    "🔬  Dinámica estocástica",
#    "🎛️  Parámetros",
#    "📐  Fórmula de Hagan",
#    "🔧  Calibración",
#])

tab1, tab2, tab3 = st.tabs([
    "🔬  Dinámica estocástica",
    "🎛️  Parámetros",
    "📐  Fórmula de Hagan",
])

# ── Tab 1: Dinámica ────────────────────────────────────────────────────────
with tab1:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown("### Sistema de EDEs — SABR")
        st.markdown("""
        El modelo SABR propone una **dinámica conjunta** para la tasa forward
        *F̂(t)* y su volatilidad estocástica *α̂(t)* bajo la medida swap
        (en la que *F̂* es martingala):
        """)
        st.latex(r"""
        d\hat{F} = \hat{\alpha}\,\hat{F}^{\beta}\,dW_1,
        \qquad \hat{F}(0) = f > 0,\quad \beta\in[0,1]
        """)
        st.latex(r"""
        d\hat{\alpha} = \nu\,\hat{\alpha}\,dW_2,
        \qquad \hat{\alpha}(0) = \alpha > 0,\quad \nu > 0
        """)
        st.latex(r"""
        dW_1\,dW_2 = \rho\,dt, \qquad \rho\in(-1,1)
        """)

        st.markdown("### Dos propiedades estructurales clave")
        props = [
            ("Sin término de deriva en dF̂",
             "No es accidental: F̂ se modela bajo la medida anualidad donde es martingala. "
             "Garantiza consistencia con la valoración libre de arbitraje."),
            ("Volatilidad como browniano geométrico sin reversión",
             "El modelo renuncia a capturar la estructura temporal de la vol-vol "
             "a cambio de tratabilidad analítica. Esto habilita la fórmula cerrada de Hagan, "
             "evitando integración numérica (como en Heston)."),
        ]
        for title, desc in props:
            st.markdown(f"""
            <div class='step-box' style='margin-bottom:0.5rem;'>
                <strong style='color:#14B8A6; font-size:0.9rem;'>{title}</strong><br>
                <span style='color:#94A3B8; font-size:0.83rem; line-height:1.5;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### SABR vs. Volatilidad Local")
        st.markdown("""
        <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
                    padding:1.2rem;'>
        """, unsafe_allow_html=True)

        comparacion = [
            ("Backbone (skew vs. forward)",
             "❌ Dirección incorrecta", "✅ Dirección correcta"),
            ("Coberturas dinámicas",
             "❌ Inestables en renta fija", "✅ Estables"),
            ("Parsimonia",
             "Función compleja (inf. params.)", "4 parámetros interpretables"),
            ("Solución analítica",
             "Sí (vol local)", "Aproximación asintótica"),
            ("Libre de arbitraje",
             "Sí", "Sí (en aprox. de Hagan)"),
        ]

        st.markdown("""
        <div style='font-size:0.72rem; display:grid; grid-template-columns:2fr 1.2fr 1.2fr;
                    gap:0.4rem; color:#94A3B8; text-transform:uppercase; letter-spacing:0.05em;
                    margin-bottom:0.5rem;'>
            <div>Propiedad</div><div>Vol. Local</div><div>SABR</div>
        </div>
        """, unsafe_allow_html=True)

        for prop, local, sabr_val in comparacion:
            bg = "rgba(20,184,166,0.06)" if "✅" in sabr_val else "transparent"
            st.markdown(f"""
            <div style='font-size:0.82rem; display:grid;
                        grid-template-columns:2fr 1.2fr 1.2fr;
                        gap:0.4rem; padding:0.35rem 0;
                        border-bottom:1px solid #1E2D45; background:{bg};
                        border-radius:4px;'>
                <div style='color:#F1F5F9;'>{prop}</div>
                <div style='color:#F87171;'>{local}</div>
                <div style='color:#34D399;'>{sabr_val}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:1rem; padding:0.8rem; background:rgba(20,184,166,0.08);
                    border-radius:8px; border:1px solid rgba(20,184,166,0.3);
                    font-size:0.82rem; color:#94A3B8; line-height:1.5;'>
            <strong style='color:#14B8A6;'>¿Por qué SABR para TIIE de Fondeo?</strong><br>
            Mercado con superficie poco profunda (4 operaciones en el día de valuación).
            SABR genera una sonrisa completa con pocos datos de mercado.
        </div>
        """, unsafe_allow_html=True)


# ── Tab 2: Parámetros ──────────────────────────────────────────────────────
with tab2:
    st.markdown("### Los cuatro parámetros del modelo SABR")
    st.markdown("Cada parámetro tiene una **interpretación geométrica directa** sobre la curva de volatilidad.")

    params_info = [
        ("β", "Exponente del backbone", "#60A5FA",
         "Determina la distribución del subyacente y la forma del backbone.",
         [("β = 1", "Log-normal · Tasas positivas y elevadas ✅ (nuestra elección)"),
          ("β = 0", "Normal · Tasas que pueden ser negativas (mercado europeo)"),
          ("β = ½", "Tipo CIR · Intermedio")],
         "Por convención de mercado, β se fija *a priori* antes de calibrar los demás."),

        ("α", "Nivel de volatilidad", "#14B8A6",
         "Controla el nivel general de la volatilidad ATM.",
         [("α grande", "Toda la curva se desplaza hacia niveles superiores"),
          ("α pequeño", "Toda la curva se desplaza hacia niveles inferiores")],
         "Un cambio en α desplaza la curva verticalmente sin alterar su forma."),

        ("ρ", "Correlación / Skew", "#F59E0B",
         "Gobierna la inclinación de la curva (skew).",
         [("ρ > 0", "Mayor vol en strikes altos → skew positivo"),
          ("ρ < 0", "Mayor vol en strikes bajos → skew negativo"),
          ("ρ = 0", "Smile simétrico")],
         "En TIIE de Fondeo se observa ρ ≈ +0.35 (skew positivo persistente)."),

        ("ν", "Volatilidad de la volatilidad", "#F472B6",
         "Controla la curvatura o convexidad de la curva (smile).",
         [("ν grande", "Sonrisa pronunciada, alas muy altas"),
          ("ν pequeño", "Sonrisa casi plana")],
         "ν actúa sobre la curvatura sin desplazar el nivel central."),
    ]

    cols = st.columns(4, gap="small")
    for col, (sym, name, color, desc, vals, note) in zip(cols, params_info):
        with col:
            st.markdown(f"""
            <div style='background:#131929; border:1px solid #1E2D45; border-radius:12px;
                        padding:1.2rem; height:100%;'>
                <div style='font-size:2.2rem; font-weight:700; color:{color};
                            font-family:serif; line-height:1;'>{sym}</div>
                <div style='font-size:0.85rem; color:#F1F5F9; font-weight:600;
                            margin:0.5rem 0 0.3rem 0;'>{name}</div>
                <div style='font-size:0.78rem; color:#94A3B8; line-height:1.4;
                            margin-bottom:0.8rem;'>{desc}</div>
            """, unsafe_allow_html=True)
            for v_name, v_desc in vals:
                st.markdown(f"""
                <div style='font-size:0.75rem; padding:0.25rem 0;
                            border-top:1px solid #1E2D45;'>
                    <span style='color:{color}; font-weight:600;'>{v_name}</span>
                    <span style='color:#94A3B8;'> — {v_desc}</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style='font-size:0.73rem; color:#64748B; margin-top:0.8rem;
                            font-style:italic; line-height:1.4;'>{note}</div>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 3: Fórmula de Hagan ────────────────────────────────────────────────
with tab3:
    col1, col2 = st.columns([3, 2], gap="large")
    with col1:
        st.markdown("### Aproximación asintótica de Hagan et al. (2002)")
        st.markdown("""
        La aportación central de Hagan et al. es una **aproximación asintótica cerrada**
        para la volatilidad implícita de Black σ_B(K, f) que reproduce los precios
        del modelo SABR. Esta fórmula permite usar SABR **sin recurrir a simulación**.
        """)

        st.latex(r"""
        \sigma_B(K,f) = \frac{\alpha}{(fK)^{(1-\beta)/2}
        \bigl[1 + \tfrac{(1-\beta)^2}{24}\ln^2\tfrac{f}{K}
              + \tfrac{(1-\beta)^4}{1920}\ln^4\tfrac{f}{K}\bigr]}
        \cdot \frac{z}{\chi(z)} \cdot \mathcal{B}
        """)

        st.latex(r"""
        z = \frac{\nu}{\alpha}(fK)^{(1-\beta)/2}\ln\frac{f}{K},
        \qquad
        \chi(z) = \ln\!\left(\frac{\sqrt{1-2\rho z+z^2}+z-\rho}{1-\rho}\right)
        """)

        st.latex(r"""
        \mathcal{B} = 1 + \!\left[\frac{(1-\beta)^2}{24}\frac{\alpha^2}{(fK)^{1-\beta}}
        + \frac{\rho\beta\nu\alpha}{4(fK)^{(1-\beta)/2}}
        + \frac{2-3\rho^2}{24}\nu^2\right]\!t_{ex}
        """)

        st.markdown("### Límite ATM (f = K)")
        st.markdown("Cuando f = K, z → 0 y z/χ(z) → 1, simplificando a:")
        st.latex(r"""
        \sigma_{ATM} = \frac{\alpha}{f^{1-\beta}}
        \left\{1 + \left[\frac{(1-\beta)^2}{24}\frac{\alpha^2}{f^{2-2\beta}}
        + \frac{\rho\beta\alpha\nu}{4f^{1-\beta}}
        + \frac{2-3\rho^2}{24}\nu^2\right]t_{ex}\right\}
        """)

        st.info("**Con β = 1** (nuestra elección): los términos en (1−β) se anulan y:")
        st.image("images/beta.png", width="stretch")
    
    with col2:
        st.markdown("### Flujo de uso en la práctica")
        steps = [
            ("1", "Calibrar (α, ρ, ν) con datos de mercado", "#14B8A6"),
            ("2", "Evaluar σ_B(K, f) con la fórmula de Hagan", "#60A5FA"),
            ("3", "Insertar σ_B en Black-76 para obtener la prima", "#F59E0B"),
        ]
        for num, desc, color in steps:
            st.markdown(f"""
            <div style='display:flex; gap:0.8rem; align-items:center;
                        padding:0.8rem; background:#131929; border:1px solid #1E2D45;
                        border-radius:8px; margin-bottom:0.5rem;'>
                <div style='width:28px; height:28px; background:{color};
                            border-radius:50%; display:flex; align-items:center;
                            justify-content:center; flex-shrink:0;'>
                    <span style='font-weight:700; color:#0B0F1A; font-size:0.85rem;'>{num}</span>
                </div>
                <div style='color:#94A3B8; font-size:0.85rem; line-height:1.4;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:1rem;'>
            <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
                        letter-spacing:0.08em; margin-bottom:0.5rem;'>Propiedades de la fórmula</div>
        """, unsafe_allow_html=True)

        props_formula = [
            ("Exacta en ATM", "por construcción del ancla"),
            ("Libre de arbitraje", "en la aproximación asintótica"),
            ("Analítica", "no requiere simulación numérica"),
            ("Captura skew y smile", "mediante ρ y ν respectivamente"),
        ]
        for prop, detail in props_formula:
            st.markdown(f"""
            <div style='padding:0.3rem 0; border-bottom:1px solid #1E2D45;
                        font-size:0.83rem;'>
                <span style='color:#34D399; margin-right:0.4rem;'>✓</span>
                <span style='color:#F1F5F9;'>{prop}</span>
                <span style='color:#94A3B8;'> — {detail}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# # ── Tab 4: Calibración ─────────────────────────────────────────────────────
# with tab4:
#     col1, col2 = st.columns([3, 2], gap="large")
#     with col1:
#         st.markdown("### Algoritmo de calibración anclada al ATM")
#         st.markdown("""
#         La práctica de mercado (Hagan et al. 2002, Cortés González 2017) es **fijar β**
#         y luego calibrar los tres parámetros restantes. Para swaptions, conviene
#         **reparametrizar en σ_ATM**, reduciendo el problema a sólo **dos parámetros libres**.
#         """)

#         steps = [
#             ("1", "Forward y anualidad",
#              "Se calculan f y A₀ del swap 1Y × tenor con la curva OIS."),
#             ("2", "Strikes absolutos",
#              "K_i = f + Δ_i. Se descartan K_i ≤ 0 y se filtra la banda |K_i/f − 1| ≤ 0.55."),
#             ("3", "Anclaje de α",
#              "Para cada par (ρ, ν), se resuelve σ_B(f,f;α,β,ρ,ν) = σ_ATM^MKT con Brent. "
#              "Garantiza que el ATM se reproduzca exactamente."),
#             ("4", "Residuales OTM/ITM",
#              "Se evalúa σ_B(K_i,f) − σ_i^MKT sólo en strikes ≠ ATM (el ATM ya está fijo)."),
#             ("5", "Minimización",
#              "min_{ρ,ν} Σ_{K≠ATM} (σ_B − σ^MKT)² con least_squares (Trust Region Reflective), "
#              "ρ ∈ [−0.999, 0.999], ν ∈ [10⁻⁴, 5]."),
#         ]

#         for num, title, desc in steps:
#             st.markdown(f"""
#             <div style='display:flex; gap:1rem; padding:0.7rem 0;
#                         border-bottom:1px solid #1E2D45;'>
#                 <div style='color:#14B8A6; font-weight:700; font-size:0.9rem;
#                             flex-shrink:0; width:18px;'>{num}.</div>
#                 <div>
#                     <div style='color:#F1F5F9; font-weight:600; font-size:0.88rem;'>{title}</div>
#                     <div style='color:#94A3B8; font-size:0.82rem; line-height:1.4;
#                                 margin-top:0.15rem;'>{desc}</div>
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)

#     with col2:
#         st.markdown("### Elección de β = 1")
#         st.markdown("""
#         <div class='result-highlight' style='margin-bottom:1rem;'>
#             <div style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase;
#                         letter-spacing:0.08em; margin-bottom:0.4rem;'>Justificación</div>
#             <div style='font-size:0.85rem; color:#F1F5F9; line-height:1.5;'>
#                 La TIIE de Fondeo presenta niveles <strong>positivos y elevados</strong>
#                 (6.5 % – 8.8 % a lo largo de la curva). El backbone log-normal (β = 1)
#                 es coherente con tasas que no pueden volverse negativas en este régimen.
#             </div>
#         </div>
#         """, unsafe_allow_html=True)

#         st.markdown("### Ventaja del anclaje")
#         st.markdown("""
#         <div style='background:#131929; border:1px solid #1E2D45; border-radius:10px;
#                     padding:1.2rem;'>
#             <div style='font-size:0.85rem; color:#F1F5F9; line-height:1.5;'>
#                 El anclaje convierte un problema de <strong style='color:#14B8A6;'>3 parámetros</strong>
#                 en uno de <strong style='color:#14B8A6;'>2 parámetros libres</strong>.
#             </div>
#             <div style='margin-top:0.8rem;'>
#                 <div style='font-size:0.8rem; color:#94A3B8; margin-bottom:0.3rem;'>Consecuencias:</div>
#                 <div style='font-size:0.82rem; color:#34D399;'>
#                     ✓ El dato más líquido (ATM) se reproduce exactamente
#                 </div>
#                 <div style='font-size:0.82rem; color:#34D399; margin-top:0.2rem;'>
#                     ✓ ρ y ν se ocupan sólo de capturar skew y curvatura
#                 </div>
#                 <div style='font-size:0.82rem; color:#34D399; margin-top:0.2rem;'>
#                     ✓ Optimización más estable y rápida
#                 </div>
#             </div>
#         </div>
#         """, unsafe_allow_html=True)
