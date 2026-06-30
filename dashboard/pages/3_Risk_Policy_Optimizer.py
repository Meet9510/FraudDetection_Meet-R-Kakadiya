"""Sentinel AI — Risk Policy Optimizer: threshold tuning and cost curve analysis."""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
try:
    from theme import (
        inject_custom_css, render_footer, init_shared_sidebar,
        load_dashboard_assets, THEME_VARS, render_skeleton_loading
    )
except ModuleNotFoundError:
    from dashboard.theme import (
        inject_custom_css, render_footer, init_shared_sidebar,
        load_dashboard_assets, THEME_VARS, render_skeleton_loading
    )

st.set_page_config(
    page_title="Sentinel AI — Policy Optimizer",
    page_icon="ðŸ“Š",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Professional White"
if "custom_threshold" not in st.session_state:
    st.session_state.custom_threshold = 0.45

inject_custom_css(st.session_state.theme_mode)
init_shared_sidebar(st.session_state.theme_mode)

is_white = st.session_state.theme_mode == "Professional White"
primary  = "#6001FC" if is_white else "#7C3AED"
v_card   = THEME_VARS['card_bg']
v_text   = THEME_VARS['text_color']
v_muted  = THEME_VARS['text_muted']
v_border = THEME_VARS['border_color_hex']

st.markdown("""
<div class="saas-header">
    <div class="saas-header-title">
        <h1>Risk Policy Optimizer</h1>
        <p>Tune classification thresholds and visualize fraud cost vs friction trade-offs.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Loading risk policy engine…")

assets = load_dashboard_assets()
_loading_slot.empty()

if not assets:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

sample_txs = assets['sample_txs'].copy()
y_true = sample_txs['Actual']
y_prob = sample_txs['Probability']

# ── Threshold slider ──────────────────────────────────────────
st.markdown(f"""
<p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
          letter-spacing:0.1em;color:{primary};margin-bottom:0.35rem;">
    Classification Threshold Control
</p>
""", unsafe_allow_html=True)

th_val = st.slider(
    "Drag to adjust the global decision threshold",
    min_value=0.05, max_value=0.95,
    value=st.session_state.custom_threshold, step=0.01,
    format="%.2f"
)
st.session_state.custom_threshold = th_val

# ── Compute metrics at selected threshold ─────────────────────
tp = sample_txs[(y_prob >= th_val) & (y_true == 1)]
fp = sample_txs[(y_prob >= th_val) & (y_true == 0)]
fn = sample_txs[(y_prob < th_val) & (y_true == 1)]

saved    = tp['TransactionAmt'].sum()
friction = fp['TransactionAmt'].sum() * 0.15
leaked   = fn['TransactionAmt'].sum() + (len(fn) * 15.0)
net      = saved - friction - leaked

# ── 4 result KPIs ─────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
m1, m2, m3, m4 = st.columns(4)
metric_data = [
    ("Fraud Blocked", f"${saved:,.0f}", "#10B981"),
    ("Friction Cost",  f"${friction:,.0f}", "#F59E0B"),
    ("Leaked Loss",    f"${leaked:,.0f}", "#EF4444"),
    ("Net Shield Value", f"${net:,.0f}", primary),
]
for col, (label, val, accent) in zip([m1,m2,m3,m4], metric_data):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {v_border};
                    border-top:3px solid {accent};border-radius:12px;
                    padding:1.1rem 1.25rem;text-align:center;">
            <p style="margin:0;font-size:0.67rem;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.09em;color:{v_muted};">{label}</p>
            <p style="margin:0.3rem 0 0;font-size:1.7rem;font-weight:900;color:{accent};">{val}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Cost curve chart ──────────────────────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.35rem 0;font-size:1rem;font-weight:800;color:{v_text};">
    Financial Optimization Cost Curves
</h3>
<p style="margin:0 0 0.75rem 0;font-size:0.78rem;color:{v_muted};">
    Sweep of all threshold values — find the optimal operating point
</p>
""", unsafe_allow_html=True)

ths = np.linspace(0.05, 0.95, 37)
sc, fc, lc, nc = [], [], [], []
for th in ths:
    tp_c = sample_txs[(y_prob >= th) & (y_true == 1)]
    fp_c = sample_txs[(y_prob >= th) & (y_true == 0)]
    fn_c = sample_txs[(y_prob < th) & (y_true == 1)]
    s = tp_c['TransactionAmt'].sum()
    f = fp_c['TransactionAmt'].sum() * 0.15
    l_val = fn_c['TransactionAmt'].sum() + len(fn_c) * 15.0
    sc.append(s); fc.append(f); lc.append(l_val); nc.append(s - f - l_val)

fig = go.Figure()
fig.add_trace(go.Scatter(x=ths, y=sc, name="Fraud Saved ($)",
                          line=dict(color='#10B981', width=2), fill='tozeroy',
                          fillcolor='rgba(16,185,129,0.05)'))
fig.add_trace(go.Scatter(x=ths, y=fc, name="Friction Cost ($)",
                          line=dict(color='#F59E0B', width=2)))
fig.add_trace(go.Scatter(x=ths, y=lc, name="Leaked Loss ($)",
                          line=dict(color='#EF4444', width=2)))
fig.add_trace(go.Scatter(x=ths, y=nc, name="Net Shield Value ($)",
                          line=dict(color=primary, width=3, dash='dash')))
fig.add_vline(x=th_val, line_width=1.5, line_dash="dot",
              line_color=v_text,
              annotation_text=f"Current: {th_val:.2f}",
              annotation_font_color=primary)
fig.update_layout(
    template="plotly_white" if is_white else "plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor=f'rgba(15,23,42,{"0.02" if is_white else "0.25"})',
    xaxis=dict(title="Threshold", gridcolor=v_border, zeroline=False),
    yaxis=dict(title="Value ($)", gridcolor=v_border, zeroline=False),
    font=dict(family="Plus Jakarta Sans", color=v_muted, size=11),
    height=340, margin=dict(t=15, b=15, l=10, r=10),
    legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center")
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── System Pipeline Blueprint ─────────────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.5rem 0;font-size:1rem;font-weight:800;color:{v_text};">
    System Operational Flow
</h3>
""", unsafe_allow_html=True)

stages = [
    ("01", "Transaction Ingest Rails",
     "Payment rails dispatch attributes (amount, card brand, funding, domain) to the Sentinel security API."),
    ("02", "Dynamic Feature Generation",
     "Comparative ratios (AmtToMeanRatio), hourly metrics, and categorical flags are built in memory."),
    ("03", "Neural Classification Inference",
     "LightGBM classifier outputs a precise anomaly score in <15ms from scaled feature inputs."),
    ("04", "Policy & Directive Enforcement",
     "Score overlays manual whitelist/blacklist rules to issue Approve, MFA Challenge, or Decline."),
]
pc = st.columns(4)
for col, (num, title, desc) in zip(pc, stages):
    with col:
        st.markdown(f"""
        <div class="saas-blueprint">
            <div class="saas-blueprint-header">
                <div class="saas-blueprint-number">{num}</div>
                <div class="saas-blueprint-title">{title}</div>
            </div>
            <p class="saas-blueprint-desc">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.code("""[Ingest API] ──â–¶ [Feature Engine] ──â–¶ [LightGBM Node]
                                                       â”‚
[Audit Logs] â—€── [Policy Enforcer] â—€── [Threshold Core]""", language="text")

render_footer()
