"""Sentinel AI — Command Center Hub: real-time operational telemetry page."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
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
    page_title="Sentinel AI — Command Center",
    page_icon="🛡",
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

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.markdown("<div class='nav-label'>Data Filters</div>", unsafe_allow_html=True)
selected_brand = st.sidebar.selectbox(
    "Card Network",
    ["All Networks", "Visa", "Mastercard", "American Express", "Discover"]
)
amt_range = st.sidebar.slider("Amount Range ($)", 1.0, 3000.0, (1.0, 2500.0))

# ── Page header ───────────────────────────────────────────────
st.markdown("""
<div class="saas-header">
    <div class="saas-header-title">
        <h1>Operational Command Center</h1>
        <p>Live threat telemetry, active alert queue, and risk density mapping.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Loading operational telemetry…")

assets = load_dashboard_assets()
_loading_slot.empty()  # clear skeleton once assets ready

if assets is None:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

# ── Prepare data ──────────────────────────────────────────────
sample_txs = assets['sample_txs'].copy()

for col in ['card4', 'card6', 'P_emaildomain']:
    if col in sample_txs.columns and col in assets['label_encoders']:
        le = assets['label_encoders'][col]
        try:
            valid_mask = sample_txs[col].notnull()
            raw = sample_txs.loc[valid_mask, col]
            # Only decode if values are numeric (encoded); skip if already strings
            if not pd.api.types.is_string_dtype(raw) and not pd.api.types.is_object_dtype(raw):
                idxs = raw.astype(int).clip(0, len(le.classes_) - 1)
                sample_txs[col] = sample_txs[col].astype(object)
                sample_txs.loc[valid_mask, col] = [le.classes_[i] for i in idxs]
            elif pd.api.types.is_object_dtype(raw):
                # Values are already strings — ensure unknown values are replaced with first class
                sample_txs[col] = sample_txs[col].astype(object)
                sample_txs.loc[valid_mask, col] = raw.apply(
                    lambda x: x if x in le.classes_ else le.classes_[0]
                )
        except (ValueError, KeyError, IndexError, TypeError):
            pass

active_threshold = st.session_state.custom_threshold

def classify_risk(score, th):
    if score >= 0.75:
        return "Critical Risk"
    if score >= th:
        return "Suspicious"
    return "Clear"

sample_txs['Risk Tier'] = sample_txs['Probability'].apply(
    lambda x: classify_risk(x, active_threshold)
)

filtered = sample_txs[
    (sample_txs['TransactionAmt'] >= amt_range[0]) &
    (sample_txs['TransactionAmt'] <= amt_range[1])
]
if selected_brand != "All Networks" and 'card4' in filtered.columns:
    filtered = filtered[
        filtered['card4'].astype(str).str.lower() == selected_brand.lower()
    ]

total   = len(filtered)
frauds  = int(filtered['Actual'].sum())
avg_amt = filtered['TransactionAmt'].mean()
avg_amt = avg_amt if not np.isnan(avg_amt) else 0.0
saved   = filtered[
    (filtered['Probability'] >= active_threshold) & (filtered['Actual'] == 1)
]['TransactionAmt'].sum()

# ── KPI Row ───────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpi_data = [
    ("Monitored Transactions", f"{total:,}", "Active ledger ingest", "#7C3AED"),
    ("Anomalies Detected",     f"{frauds}",  "Flagged this period",   "#EF4444"),
    ("Avg Basket Value",       f"${avg_amt:.2f}", "Mean checkout value", "#F59E0B"),
    ("Capital Protected",      f"${saved:,.0f}", "Secured from fraud",  "#10B981"),
]
for col, (label, val, sub, accent) in zip([k1,k2,k3,k4], kpi_data):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {v_border};
                    border-left:3px solid {accent};border-radius:12px;padding:1.1rem 1.25rem;">
            <p style="margin:0;font-size:0.68rem;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.09em;color:{v_muted};">{label}</p>
            <p style="margin:0.3rem 0 0.1rem;font-size:1.9rem;font-weight:900;color:{v_text};">{val}</p>
            <p style="margin:0;font-size:0.71rem;color:{v_muted};">{sub}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Alert Queue + Risk Pie ────────────────────────────────────
col_alerts, col_pie = st.columns([1.6, 1], gap="large")

with col_alerts:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.75rem;">
        <div>
            <h3 style="margin:0;font-size:1rem;font-weight:800;color:{v_text};">
                Active Threat Alert Queue
            </h3>
            <p style="margin:0;font-size:0.78rem;color:{v_muted};">
                High-probability anomalies awaiting operator review
            </p>
        </div>
        <span style="background:rgba(239,68,68,0.1);color:#EF4444;border:1px solid rgba(239,68,68,0.25);
                     padding:0.2rem 0.6rem;border-radius:20px;font-size:0.7rem;font-weight:700;">
            LIVE
        </span>
    </div>
    """, unsafe_allow_html=True)

    high_risk = filtered[filtered['Probability'] >= active_threshold].sort_values(
        'Probability', ascending=False
    ).head(5)

    if len(high_risk) == 0:
        st.info("No anomalies matching current filters.")
    else:
        for _, row in high_risk.iterrows():
            tx_id  = int(row['TransactionID'])
            amt    = row['TransactionAmt']
            prob_v = row['Probability']
            brand  = str(row.get('card4', 'Unknown')).upper()
            tier   = row['Risk Tier']
            badge  = (
                "saas-badge-critical" if tier == "Critical Risk"
                else "saas-badge-suspicious"
            )
            st.markdown(f"""
            <div style="background:{v_card};border:1px solid {v_border};border-radius:10px;
                        padding:0.85rem 1rem;margin-bottom:0.5rem;
                        display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:1.25rem;flex:1;">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                                 font-weight:700;color:{v_muted};">#{tx_id}</span>
                    <span style="font-size:0.88rem;font-weight:700;color:{v_text};">${amt:.2f}</span>
                    <span style="font-size:0.78rem;color:{v_muted};">{brand}</span>
                    <span class="{badge}">{tier} · {prob_v*100:.1f}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            a1, a2, a3, _ = st.columns([1, 1, 1, 4])
            if a1.button("✓ Clear", key=f"clr_{tx_id}", use_container_width=True):
                st.toast(f"#{tx_id} cleared")
            if a2.button("⚡ MFA", key=f"mfa_{tx_id}", use_container_width=True):
                st.toast(f"MFA sent for #{tx_id}")
            if a3.button("✕ Block", key=f"blk_{tx_id}", use_container_width=True):
                st.toast(f"#{tx_id} blocked")

with col_pie:
    st.markdown(f"""
    <h3 style="margin:0 0 0.75rem 0;font-size:1rem;font-weight:800;color:{v_text};">
        Risk Distribution
    </h3>
    """, unsafe_allow_html=True)
    tier_counts = filtered['Risk Tier'].value_counts().reset_index()
    tier_counts.columns = ['Risk Tier', 'Volume']
    fig_pie = px.pie(
        tier_counts, names='Risk Tier', values='Volume',
        color='Risk Tier',
        color_discrete_map={
            'Clear': '#10B981', 'Suspicious': '#F59E0B', 'Critical Risk': '#EF4444'
        },
        hole=0.65
    )
    fig_pie.update_traces(textfont_size=11)
    fig_pie.update_layout(
        template="plotly_white" if is_white else "plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=0, r=0),
        height=290,
        legend=dict(
            orientation="h", yanchor="bottom",
            y=-0.2, xanchor="center", x=0.5,
            font=dict(size=11)
        )
    )
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Scatter: Risk Density Map ─────────────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.5rem 0;font-size:1rem;font-weight:800;color:{v_text};">
    Risk Density Time Mapping
</h3>
<p style="margin:0 0 0.75rem 0;font-size:0.78rem;color:{v_muted};">
    Transaction risk score plotted against time of day and value
</p>
""", unsafe_allow_html=True)

fig_scatter = px.scatter(
    filtered, x='HourOfDay', y='TransactionAmt',
    color='Probability', color_continuous_scale='Reds',
    log_y=True,
    labels={
        'HourOfDay': 'Hour of Day (24h)',
        'TransactionAmt': 'Transaction Value ($)',
        'Probability': 'Risk Index'
    },
    hover_data=['TransactionID']
)
fig_scatter.update_traces(marker=dict(size=7, opacity=0.75))
fig_scatter.update_layout(
    template="plotly_white" if is_white else "plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor=f'rgba(15,23,42,{"0.03" if is_white else "0.3"})',
    xaxis=dict(gridcolor=v_border, zeroline=False),
    yaxis=dict(gridcolor=v_border, zeroline=False),
    font=dict(family="Plus Jakarta Sans", color=v_muted, size=11),
    height=310,
    margin=dict(t=10, b=10, l=10, r=10),
    coloraxis_colorbar=dict(len=0.7, thickness=12)
)
st.plotly_chart(fig_scatter, use_container_width=True)

render_footer()
