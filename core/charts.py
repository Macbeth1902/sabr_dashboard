"""
core/charts.py — Todas las gráficas Plotly del proyecto

"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Paleta global ────────────────────────────────────────────────────────────
C_TEAL   = "#14B8A6"
C_AMBER  = "#F59E0B"
C_BLUE   = "#60A5FA"
C_GREEN  = "#34D399"
C_ROSE   = "#F472B6"
C_BG     = "#0B0F1A"
C_CARD   = "#131929"
C_BORDER = "#1E2D45"
C_TEXT   = "#F1F5F9"
C_MUTED  = "#94A3B8"

LAYOUT_BASE = dict(
    paper_bgcolor=C_BG,
    plot_bgcolor=C_CARD,
    font=dict(color=C_TEXT, family="Inter, system-ui, sans-serif", size=12),
    margin=dict(l=50, r=30, t=50, b=50),
    xaxis=dict(gridcolor=C_BORDER, zerolinecolor=C_BORDER),
    yaxis=dict(gridcolor=C_BORDER, zerolinecolor=C_BORDER),
)


def fig_curva_ois(years, zero, fwd28, nodes_rep, par_rep) -> go.Figure:
    """Factor de descuento y tasa cero continua."""
    from core.data import DC, N_TOTAL
    from core.bootstrap import bootstrap_ois_directo
    from core.data import PAR_FULL

    DF = bootstrap_ois_directo(PAR_FULL)
    idx   = np.arange(0, N_TOTAL + 1)
    yr    = idx * 28 / 360.0

    nodes_yrs = [n * 28 / 360 for n in nodes_rep]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Factor de Descuento DF(t)", "Tasa Cero Continua (%)"],
        horizontal_spacing=0.12,
    )

    # ── Panel izquierdo: DF ──
    fig.add_trace(go.Scatter(
        x=yr, y=DF,
        mode="lines", name="DF(t)",
        line=dict(color=C_TEAL, width=2.5),
    ), row=1, col=1)

    # ── Panel derecho: tasa cero ──
    fig.add_trace(go.Scatter(
        x=yr[1:], y=zero[1:] * 100,
        mode="lines", name="Tasa Cero",
        line=dict(color=C_AMBER, width=2.5),
    ), row=1, col=2)

    # Nodos representativos
    zero_at_nodes = [-np.log(DF[n]) / (n * 28 / 360) * 100 for n in nodes_rep]
    fig.add_trace(go.Scatter(
        x=nodes_yrs, y=zero_at_nodes,
        mode="markers", name="Nodos rep.",
        marker=dict(color=C_TEXT, size=8, symbol="circle"),
    ), row=1, col=2)

    fig.update_layout(**LAYOUT_BASE, height=380,
                      showlegend=False,
                      title_text="Curva OIS de TIIE de Fondeo — Bootstrapping directo (390 nodos)")
    fig.update_xaxes(title_text="Años", gridcolor=C_BORDER, zerolinecolor=C_BORDER)
    fig.update_yaxes(gridcolor=C_BORDER, zerolinecolor=C_BORDER)
    fig.update_yaxes(title_text="DF", row=1, col=1)
    fig.update_yaxes(title_text="% (cont. anual)", row=1, col=2)
    return fig


def fig_forward_curve(years, fwd28) -> go.Figure:
    """Curva de tasas forward a 28 días."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years[1:], y=fwd28[1:] * 100,
        mode="lines", name="Fwd 28d",
        line=dict(color=C_BLUE, width=2),
        fill="tozeroy",
        fillcolor="rgba(96,165,250,0.08)",
    ))
    fig.update_layout(
        **LAYOUT_BASE, height=320,
        title_text="Tasas Forward a 28 días",
        xaxis_title="Años",
        yaxis_title="Fwd 28d (%)",
    )
    return fig


def fig_sabr_smile(calib: dict, tenor_lbl: str, beat: float = 1.0) -> go.Figure:
    """Smile SABR para un tenor concreto vs. volatilidades de mercado."""
    from core.sabr import sabr_ln_vol
    from core.data import STRIKE_ABS, VOL_N, TENOR_LBL_SW, EXPIRY_FIX

    idx = TENOR_LBL_SW.index(tenor_lbl)
    c   = calib[tenor_lbl]
    f   = c["f"]
    K_mkt = f + STRIKE_ABS
    mask  = K_mkt > 0
    K_mkt = K_mkt[mask]
    V_mkt = VOL_N[idx][mask]

    K_fine = np.linspace(K_mkt[0], K_mkt[-1], 200)
    V_sabr = sabr_ln_vol(K_fine, f, EXPIRY_FIX,
                          c["alpha"], c["beta"], c["rho"], c["nu"]) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=(K_mkt - f) * 1e4, y=V_mkt * 100,
        mode="markers", name="Mercado (VCUB)",
        marker=dict(color=C_AMBER, size=9, symbol="circle-open", line=dict(width=2)),
    ))
    fig.add_trace(go.Scatter(
        x=(K_fine - f) * 1e4, y=V_sabr,
        mode="lines", name="SABR calibrado",
        line=dict(color=C_TEAL, width=2.5),
    ))
    fig.update_layout(
        **LAYOUT_BASE, height=380,
        title_text=f"Smile SABR · Tenor {tenor_lbl} · tex = 1A",
        xaxis_title="Moneyness K − f (pb)",
        yaxis_title="Vol. log-normal (%)",
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C_BORDER),
    )
    return fig


def fig_param_sensitivity(calib: dict, tenor_lbl: str, param: str) -> go.Figure:
    """Sensibilidad de la smile a variaciones de un parámetro."""
    from core.sabr import sabr_ln_vol, alpha_from_atm
    from core.data import ATM_N, TENOR_LBL_SW, EXPIRY_FIX, BETA

    idx = TENOR_LBL_SW.index(tenor_lbl)
    c   = calib[tenor_lbl]
    f   = c["f"]
    atm = ATM_N[idx]
    K_grid = np.linspace(f - 0.03, f + 0.03, 300)

    params = {
        "rho":   [(-0.30, "ρ = −0.30", C_BLUE),
                  (c["rho"], f"ρ = {c['rho']:.2f} (calibrado)", C_TEAL),
                  (0.60, "ρ = +0.60", C_ROSE)],
        "nu":    [(0.20, "ν = 0.20", C_BLUE),
                  (c["nu"],  f"ν = {c['nu']:.2f} (calibrado)", C_TEAL),
                  (0.90, "ν = 0.90", C_ROSE)],
        "alpha": [(alpha_from_atm(atm * 0.85, f, EXPIRY_FIX, BETA, c["rho"], c["nu"]),
                   f"ATM = {atm*0.85*100:.1f}%", C_BLUE),
                  (c["alpha"],
                   f"ATM = {atm*100:.1f}% (calibrado)", C_TEAL),
                  (alpha_from_atm(atm * 1.15, f, EXPIRY_FIX, BETA, c["rho"], c["nu"]),
                   f"ATM = {atm*1.15*100:.1f}%", C_ROSE)],
    }

    titles = {"rho": "Sensibilidad a ρ (skew)",
              "nu":  "Sensibilidad a ν (smile / curvatura)",
              "alpha": "Sensibilidad a α (nivel via vol ATM)"}

    fig = go.Figure()
    for pval, label, color in params[param]:
        if param == "rho":
            a = alpha_from_atm(atm, f, EXPIRY_FIX, BETA, pval, c["nu"])
            v = sabr_ln_vol(K_grid, f, EXPIRY_FIX, a, BETA, pval, c["nu"]) * 100
        elif param == "nu":
            a = alpha_from_atm(atm, f, EXPIRY_FIX, BETA, c["rho"], pval)
            v = sabr_ln_vol(K_grid, f, EXPIRY_FIX, a, BETA, c["rho"], pval) * 100
        else:  # alpha
            v = sabr_ln_vol(K_grid, f, EXPIRY_FIX, pval, BETA, c["rho"], c["nu"]) * 100
        fig.add_trace(go.Scatter(
            x=(K_grid - f) * 1e4, y=v,
            mode="lines", name=label,
            line=dict(color=color, width=2.2),
        ))

    fig.update_layout(
        **LAYOUT_BASE, height=380,
        title_text=titles[param] + f" · Tenor {tenor_lbl}",
        xaxis_title="Moneyness K − f (pb)",
        yaxis_title="Vol. log-normal (%)",
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C_BORDER),
    )
    return fig


def fig_sabr_surface(calib: dict) -> go.Figure:
    """Superficie 3D SABR: volatilidad vs. tenor y moneyness."""
    from core.sabr import sabr_ln_vol
    from core.data import TENOR_LBL_SW, TENOR_Y_SW, EXPIRY_FIX, BETA

    # Excluimos tenores muy cortos (1Mo–9Mo) para una presentación más limpia
    idx_start = 4  # desde 1Yr
    tenors_plot = TENOR_Y_SW[idx_start:]
    lbls_plot   = TENOR_LBL_SW[idx_start:]

    moneyness_bp = np.linspace(-250, 250, 60)

    Z = []
    for lbl in lbls_plot:
        c = calib[lbl]
        f = c["f"]
        K_row = f + moneyness_bp / 1e4
        K_row = np.maximum(K_row, 1e-6)
        v_row = sabr_ln_vol(K_row, f, EXPIRY_FIX,
                             c["alpha"], BETA, c["rho"], c["nu"]) * 100
        Z.append(v_row)

    Z = np.array(Z)
    X, Y = np.meshgrid(moneyness_bp, tenors_plot)

    fig = go.Figure(data=[go.Surface(
        x=X, y=Y, z=Z,
        colorscale=[
            [0.0,  "#0B3D91"],
            [0.25, "#14B8A6"],
            [0.5,  "#34D399"],
            [0.75, "#F59E0B"],
            [1.0,  "#F87171"],
        ],
        opacity=0.92,
        showscale=True,
        colorbar=dict(title="Vol (%)", tickfont=dict(color=C_TEXT)),
    )])

    fig.update_layout(
        paper_bgcolor=C_BG,
        font=dict(color=C_TEXT, family="Inter, system-ui, sans-serif"),
        title_text="Superficie SABR · tex = 1A · Tenores 1Yr–30Yr",
        scene=dict(
            xaxis=dict(title="Moneyness (pb)", gridcolor=C_BORDER,
                       backgroundcolor=C_CARD, color=C_TEXT),
            yaxis=dict(title="Tenor (años)",   gridcolor=C_BORDER,
                       backgroundcolor=C_CARD, color=C_TEXT),
            zaxis=dict(title="Vol. log-normal (%)", gridcolor=C_BORDER,
                       backgroundcolor=C_CARD, color=C_TEXT),
            bgcolor=C_CARD,
        ),
        height=520,
        margin=dict(l=0, r=0, t=60, b=0),
    )
    return fig

def fig_calibration_params(calib: dict) -> go.Figure:
    """Evolución de los parámetros SABR calibrados a lo largo de los tenores."""
    from core.data import TENOR_LBL_SW, TENOR_Y_SW

    tenors = TENOR_Y_SW
    #alphas = [calib[l]["alpha"] for l in TENOR_LBL_SW]
    #rhos   = [calib[l]["rho"]   for l in TENOR_LBL_SW]
    #nus    = [calib[l]["nu"]    for l in TENOR_LBL_SW]
    rmses  = [calib[l]["rmse"] * 1e4 for l in TENOR_LBL_SW]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=["RMSE (pb)"],
        vertical_spacing=0.18,
        horizontal_spacing=0.12,
    )

    pairs = [(rmses, C_ROSE,  2, 2)]

    names = ["RMSE (pb)"]
    for (vals, col, r, c_), nm in zip(pairs, names):
        fig.add_trace(go.Scatter(
            x=tenors, y=vals,
            mode="lines+markers",
            line=dict(color=col, width=2),
            marker=dict(size=6),
            name=nm,
        ), row=r, col=c_)

    fig.update_layout(
        **LAYOUT_BASE,
        height=480,
        showlegend=False,
        title_text="Parámetro RMSE (pb) calibrado por tenor (tex = 1A)",
    )
    fig.update_xaxes(title_text="Tenor (años)", gridcolor=C_BORDER)
    fig.update_yaxes(gridcolor=C_BORDER)
    return fig


# def fig_calibration_params(calib: dict) -> go.Figure:
#     """Evolución de los parámetros SABR calibrados a lo largo de los tenores."""
#     from core.data import TENOR_LBL_SW, TENOR_Y_SW

#     tenors = TENOR_Y_SW
#     alphas = [calib[l]["alpha"] for l in TENOR_LBL_SW]
#     rhos   = [calib[l]["rho"]   for l in TENOR_LBL_SW]
#     nus    = [calib[l]["nu"]    for l in TENOR_LBL_SW]
#     rmses  = [calib[l]["rmse"] * 1e4 for l in TENOR_LBL_SW]

#     fig = make_subplots(
#         rows=2, cols=2,
#         subplot_titles=["α (nivel)", "ρ (skew)", "ν (curvatura)", "RMSE (pb)"],
#         vertical_spacing=0.18,
#         horizontal_spacing=0.12,
#     )

#     pairs = [(alphas, C_TEAL, 1, 1), (rhos, C_AMBER, 1, 2),
#              (nus,   C_BLUE,  2, 1), (rmses, C_ROSE,  2, 2)]

#     names = ["α", "ρ", "ν", "RMSE (pb)"]
#     for (vals, col, r, c_), nm in zip(pairs, names):
#         fig.add_trace(go.Scatter(
#             x=tenors, y=vals,
#             mode="lines+markers",
#             line=dict(color=col, width=2),
#             marker=dict(size=6),
#             name=nm,
#         ), row=r, col=c_)

#     fig.update_layout(
#         **LAYOUT_BASE,
#         height=480,
#         showlegend=False,
#         title_text="Parámetros SABR calibrados por tenor (tex = 1A)",
#     )
#     fig.update_xaxes(title_text="Tenor (años)", gridcolor=C_BORDER)
#     fig.update_yaxes(gridcolor=C_BORDER)
#     return fig


def fig_vcub_heatmap() -> go.Figure:
    """Heatmap de la matriz VCUB original de Bloomberg."""
    from core.data import VOL_N, TENOR_LBL_SW, STRIKE_LABELS

    fig = go.Figure(data=go.Heatmap(
        z=VOL_N * 100,
        x=STRIKE_LABELS,
        y=TENOR_LBL_SW,
        colorscale=[
            [0.0,  "#0B3D91"],
            [0.4,  "#14B8A6"],
            [0.7,  "#F59E0B"],
            [1.0,  "#F87171"],
        ],
        colorbar=dict(title="Vol (%)", tickfont=dict(color=C_TEXT)),
        hoverongaps=False,
        hovertemplate="Tenor: %{y}<br>Strike: %{x}<br>Vol: %{z:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **LAYOUT_BASE,
        height=420,
        title_text="Matriz VCUB — Bloomberg 20-may-2026 (Vol. log-normal %)",
        xaxis_title="Moneyness relativo al ATM",
        yaxis_title="Tenor del swap subyacente",
    )
    return fig


def fig_smile_comparison(res_list: list) -> go.Figure:
    """
    Compara la smile del swaption para distintos strikes valuados.
    res_list: lista de dicts devueltos por valuar_swaption
    """
    from core.sabr import sabr_ln_vol
    from core.data import BETA, EXPIRY_FIX

    if not res_list:
        return go.Figure()

    c0 = res_list[0]
    f  = c0["f"]
    al, rho, nu = c0["alpha"], c0["rho"], c0["nu"]

    K_grid = np.linspace(f * 0.60, f * 1.45, 300)
    V_grid = sabr_ln_vol(K_grid, f, EXPIRY_FIX, al, BETA, rho, nu) * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=(K_grid - f) * 1e4, y=V_grid,
        mode="lines", name="Smile SABR",
        line=dict(color=C_TEAL, width=2.5),
    ))

    colors_pts = [C_AMBER, C_ROSE, C_BLUE, C_GREEN]
    for i, res in enumerate(res_list):
        K_i     = res["K"]
        sigma_i = res["sigma"] * 100
        label   = f"K = {K_i*100:.4f}%  [{res['posicion']}]"
        fig.add_trace(go.Scatter(
            x=[(K_i - f) * 1e4], y=[sigma_i],
            mode="markers+text",
            name=label,
            text=[f"σ={sigma_i:.2f}%"],
            textposition="top center",
            marker=dict(color=colors_pts[i % len(colors_pts)], size=12, symbol="diamond"),
        ))

    fig.update_layout(
        **LAYOUT_BASE, height=380,
        title_text=f"Smile SABR · Tenor {c0['tenor']:.1f}A · tex = 1A",
        xaxis_title="Moneyness K − f (pb)",
        yaxis_title="Vol. implícita Black (%)",
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=C_BORDER, font=dict(size=11)),
    )
    return fig