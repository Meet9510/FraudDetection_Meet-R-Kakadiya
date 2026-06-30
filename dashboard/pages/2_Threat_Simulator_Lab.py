"""Sentinel AI - Threat Simulator Lab: interactive transaction scoring page."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import shap
try:
    from theme import inject_custom_css, render_footer, init_shared_sidebar, load_dashboard_assets, THEME_VARS 
except ModuleNotFoundError:
    from dashboard.theme import inject_custom_css, render_footer, init_shared_sidebar, load_dashboard_assets, THEME_VARS
st.set_page_config(
    page_title="Sentinel AI - Threat Simulator Lab",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Professional White"
if "custom_threshold" not in st.session_state:
    st.session_state.custom_threshold = 0.45

inject_custom_css(st.session_state.theme_mode)
init_shared_sidebar(st.session_state.theme_mode)

assets = load_dashboard_assets()

st.markdown("""
<div class="saas-header">
    <div class="saas-header-title">
        <h1>Sentinel Risk Management Console</h1>
        <p>Simulate transaction attributes and analyze machine learning attribution values in real-time.</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not assets:
    st.warning(
        "Model payload not found. Place model.pkl in dashboard/ to activate features."
    )
    st.stop()

active_threshold = st.session_state.custom_threshold

st.markdown("### Interactive Threat Simulator Lab")
st.caption(
    "Configure a simulated transaction below and Sentinel AI will score it in real time.")

# ── Preset scenarios ──────────────────────────────────────────
SCENARIOS = {
    "Select Scenario Preset...": None,
    "Low Risk — Standard Debit Groceries": {
        "amt": 45.82, "hour": 13, "card4": "visa",
        "card6": "debit", "email": "gmail.com", "card1": 9500
    },
    "Suspicious — Premium Credit Late Checkout": {
        "amt": 680.00, "hour": 22, "card4": "mastercard",
        "card6": "credit", "email": "outlook.com", "card1": 15000
    },
    "Critical — Late-Night High-Value Foreign Card": {
        "amt": 1820.00, "hour": 3, "card4": "american express",
        "card6": "credit", "email": "protonmail.com", "card1": 18200
    },
}

preset_name = st.selectbox("Load Scenario Preset", list(SCENARIOS.keys()))
if preset_name != "Select Scenario Preset...":
    sel = SCENARIOS[preset_name]
    st.session_state.saas_amt = float(sel["amt"])
    st.session_state.saas_hour = int(sel["hour"])
    st.session_state.saas_card4 = sel["card4"]
    st.session_state.saas_card6 = sel["card6"]
    st.session_state.saas_email = sel["email"]
    st.session_state.saas_card1 = int(sel["card1"])

# Default values
for k, v in [("saas_amt", 150.0), ("saas_hour", 14), ("saas_card4", "visa"),
             ("saas_card6", "debit"), ("saas_email", "gmail.com"), ("saas_card1", 10000)]:
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("---")

# ── Two-column layout: inputs left, results right ─────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("##### Transaction Parameters")

    r1a, r1b = st.columns(2)
    with r1a:
        sim_amt = st.number_input(
            "Amount ($)", min_value=1.0, max_value=20000.0,
            step=1.0, key="saas_amt"
        )
    with r1b:
        sim_card6 = st.selectbox(
            "Funding Type",
            ["debit", "credit", "charge card"],
            key="saas_card6"
        )

    sim_hour = st.slider("Hour of Day (0–23)", 0, 23, key="saas_hour")

    r2a, r2b = st.columns(2)
    with r2a:
        sim_card4 = st.selectbox(
            "Card Network",
            ["visa", "mastercard", "american express", "discover"],
            key="saas_card4"
        )
    with r2b:
        sim_email = st.selectbox(
            "Email Domain",
            ["gmail.com", "yahoo.com", "outlook.com",
             "hotmail.com", "protonmail.com", "mail.com", "Unknown"],
            key="saas_email"
        )

    sim_card1 = st.number_input(
        "Issuer Code (card1)", min_value=1000,
        max_value=25000, step=1, key="saas_card1"
    )

    # ── Credit card visual ────────────────────────────────────
    card_no_map = {
        "visa": "4532 •••• •••• 9823",
        "mastercard": "5243 •••• •••• 1045",
        "american express": "3782 •••••• 49102",
        "discover": "6011 •••• •••• 8293",
    }
    card_no = card_no_map.get(sim_card4, "•••• •••• •••• ••••")

    st.markdown(f"""
    <div class="saas-token-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="saas-token-chip"></div>
            <span style="font-family:'JetBrains Mono',monospace; font-weight:800;
                         font-size:0.9rem; text-transform:uppercase; color:#FFF;">
                {sim_card4}
            </span>
        </div>
        <div class="saas-token-number">{card_no}</div>
        <div class="saas-token-footer">
            <div>
                <div style="font-size:0.58rem; opacity:0.6;">OPERATOR</div>
                <div style="font-weight:700; color:#FFF;">Meet R Kakadiya</div>
            </div>
            <div>
                <div style="font-size:0.58rem; opacity:0.6;">VALUE</div>
                <div style="font-weight:700; color:#FFF;">${sim_amt:.2f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Build feature vector & run inference ──────────────────────
input_row = pd.DataFrame(0.0, index=[0], columns=assets['features'])
input_row['TransactionAmt'] = sim_amt
input_row['card1'] = sim_card1
input_row['HourOfDay'] = sim_hour
input_row['AmtToMeanRatio'] = sim_amt / (135.0 + 1e-5)
input_row['DeviceRisk'] = 1 if 'credit' in sim_card6 else 0
input_row['LogTransactionAmt'] = np.log1p(sim_amt)
input_row['Card1AmtRatio'] = 1.0
input_row['EmailDomainRisk'] = (
    1 if sim_email in ['mail.com', 'protonmail.com', 'outlook.com', 'hotmail.com']
    else 0
)
input_row['Card1Freq'] = 10

for col_name, sim_val in [
    ('card4', sim_card4), ('card6', sim_card6), ('P_emaildomain', sim_email)
]:
    if col_name in assets['label_encoders']:
        le = assets['label_encoders'][col_name]
        val = sim_val if sim_val in le.classes_ else le.classes_[0]
        input_row[col_name] = le.transform([val])[0]

input_scaled = input_row.copy()
input_scaled[assets['numeric_cols']] = assets['scaler'].transform(
    input_row[assets['numeric_cols']]
)
prob = assets['model'].predict_proba(input_scaled)[:, 1][0]

with col_right:
    st.markdown("##### Core Directive Decision")

    if prob >= 0.75:
        st.markdown(f"""
        <div class="alert-panel-decline">
            <h4 style="margin:0; font-size:1rem; font-weight:800;">
                CRITICAL — AUTOMATED DECLINE
            </h4>
            <p style="margin:0.35rem 0 0 0; font-size:0.88rem;">
                Risk Index: <b>{prob*100:.1f}%</b> — Card block initiated immediately.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif prob >= active_threshold:
        st.markdown(f"""
        <div class="alert-panel-mfa">
            <h4 style="margin:0; font-size:1rem; font-weight:800;">
                SUSPICIOUS — MFA CHALLENGE
            </h4>
            <p style="margin:0.35rem 0 0 0; font-size:0.88rem;">
                Risk Index: <b>{prob*100:.1f}%</b> — 3D-Secure verification required.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="alert-panel-approve">
            <h4 style="margin:0; font-size:1rem; font-weight:800;">
                CLEAR — APPROVED
            </h4>
            <p style="margin:0.35rem 0 0 0; font-size:0.88rem;">
                Risk Index: <b>{prob*100:.1f}%</b> — Frictionless baseline authorization.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # ── Risk gauge ────────────────────────────────────────────
    bar_color = (
        "#EF4444" if prob >= 0.75
        else ("#F59E0B" if prob >= active_threshold else "#10B981")
    )
    is_white = st.session_state.theme_mode == "Professional White"

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(prob * 100, 1),
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': "%", 'font': {
            'size': 36, 'family': 'Plus Jakarta Sans'}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': THEME_VARS['text_muted'],
                'tickfont': {'size': 10}
            },
            'bar': {'color': bar_color, 'thickness': 0.25},
            'bgcolor': "#E2E8F0" if is_white else "#1E293B",
            'borderwidth': 0,
            'steps': [
                {'range': [0, active_threshold * 100],
                    'color': 'rgba(16,185,129,0.12)'},
                {'range': [active_threshold * 100, 75],
                    'color': 'rgba(245,158,11,0.12)'},
                {'range': [75, 100], 'color': 'rgba(239,68,68,0.12)'},
            ],
            'threshold': {
                'line': {'color': bar_color, 'width': 2},
                'thickness': 0.8,
                'value': prob * 100
            }
        }
    ))
    fig_gauge.update_layout(
        height=230,
        margin=dict(t=20, b=10, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        template="plotly_white" if is_white else "plotly_dark",
        font=dict(family="Plus Jakarta Sans", color=THEME_VARS['text_color'])
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    # ── 3 quick metric chips ──────────────────────────────────
    m1, m2, m3 = st.columns(3)
    tier = (
        "Critical Risk" if prob >= 0.75
        else ("Suspicious" if prob >= active_threshold else "Clear")
    )
    badge_cls = (
        "saas-badge-critical" if prob >= 0.75
        else ("saas-badge-suspicious" if prob >= active_threshold else "saas-badge-clear")
    )
    with m1:
        st.markdown(f"""
        <div class="saas-card" style="padding:0.75rem !important; text-align:center;">
            <h3 style="margin:0 0 0.25rem 0;">Tier</h3>
            <span class="{badge_cls}">{tier}</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="saas-card" style="padding:0.75rem !important; text-align:center;">
            <h3 style="margin:0 0 0.25rem 0;">Score</h3>
            <p class="saas-card-value" style="font-size:1.3rem;">{prob*100:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="saas-card" style="padding:0.75rem !important; text-align:center;">
            <h3 style="margin:0 0 0.25rem 0;">Threshold</h3>
            <p class="saas-card-value" style="font-size:1.3rem;">{active_threshold*100:.0f}%</p>
        </div>
        """, unsafe_allow_html=True)

# ── SHAP Waterfall ────────────────────────────────────────────
st.markdown("---")
st.markdown("### Explainable Attribution Diagnostics")
st.caption(
    "Local SHAP waterfall showing which features pushed the risk score up or down.")

shap_sample_ids = assets['X_test_shap']['card1'].index.tolist()
matched_idx = int(sim_card1) % len(shap_sample_ids)
real_idx = shap_sample_ids[matched_idx]
raw_idx = assets['X_test_shap'].index.get_loc(real_idx)

with st.container(border=True):
    _, col_shap, _ = st.columns([0.5, 9, 0.5])
    with col_shap:
        fig_att = plt.figure(figsize=(9, 3))
        plt.clf()
        fig_att.patch.set_alpha(0.0)
        shap.plots.waterfall(assets['shap_values']
                             [raw_idx], max_display=8, show=False)
        ax_att = plt.gca()
        ax_att.patch.set_alpha(0.0)
        ax_att.tick_params(
            axis='both', colors=THEME_VARS['text_muted'], labelsize=8)
        for spine in ax_att.spines.values():
            spine.set_color(THEME_VARS['border_color_hex'])
        try:
            for txt in ax_att.texts:
                txt.set_fontsize(8)
                txt.set_color(THEME_VARS['text_color'])
        except (AttributeError, TypeError, ValueError, KeyError):
            pass
        st.pyplot(fig_att, bbox_inches='tight', clear_figure=True)

render_footer()
