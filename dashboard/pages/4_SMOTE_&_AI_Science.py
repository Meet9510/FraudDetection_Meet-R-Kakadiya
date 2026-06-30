"""Sentinel AI — SMOTE & AI Science: notebook analysis charts and model methodology."""

import os
import streamlit as st
import plotly.graph_objects as go
import numpy as np
try:
    from theme import (
        inject_custom_css, render_footer, init_shared_sidebar,
        load_dashboard_assets, THEME_VARS
    )
except ModuleNotFoundError:
    from dashboard.theme import (
        inject_custom_css, render_footer, init_shared_sidebar,
        load_dashboard_assets, THEME_VARS
    )

st.set_page_config(
    page_title="Sentinel AI — SMOTE & AI Science",
    page_icon="🔬",
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

# Resolve chart paths relative to this file's location
_HERE     = os.path.dirname(os.path.abspath(__file__))
_ROOT     = os.path.normpath(os.path.join(_HERE, "..", ".."))
_CHARTS   = os.path.join(_ROOT, "charts")

def _chart(name: str) -> str:
    return os.path.join(_CHARTS, name)

st.markdown("""
<div class="saas-header">
    <div class="saas-header-title">
        <h1>SMOTE &amp; AI Science Lab</h1>
        <p>Full analysis pipeline: class balancing, feature engineering, model training, evaluation, and SHAP explainability.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

assets = load_dashboard_assets()
perf   = assets['performance'] if assets else {}
threshold = st.session_state.custom_threshold

# ── Section tabs ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Data & Class Balance",
    "Model Comparison",
    "ROC & Threshold",
    "SHAP Explainability",
    "Risk Segmentation",
])

# ═══════════════════════════════════════════════════════════════
# TAB 1 — Data & Class Balance
# ═══════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f"""
    <h3 style="margin:1rem 0 0.3rem;font-size:1rem;font-weight:800;color:{v_text};">
        Class Imbalance &amp; SMOTE Balancing
    </h3>
    <p style="font-size:0.82rem;color:{v_muted};margin:0 0 1.2rem;">
        The raw IEEE-CIS dataset is severely imbalanced (~3.5% fraud). SMOTE (Synthetic Minority
        Over-sampling Technique) generates synthetic fraud samples to create a balanced 50/50 training
        split, preventing the model from being biased toward the majority class.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if os.path.exists(_chart("chart1.png")):
            st.image(_chart("chart1.png"), caption="Original Class Distribution (3.5% fraud)", use_container_width=True)
    with c2:
        if os.path.exists(_chart("chart2.png")):
            st.image(_chart("chart2.png"), caption="Transaction Amount Distribution by Class", use_container_width=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        if os.path.exists(_chart("chart3.png")):
            st.image(_chart("chart3.png"), caption="Hourly Fraud Rate Pattern", use_container_width=True)
    with c4:
        if os.path.exists(_chart("correlation_heatmap.png")):
            st.image(_chart("correlation_heatmap.png"), caption="Feature Correlation Heatmap", use_container_width=True)

    st.markdown(f"""
    <div style="background:{v_card};border:1px solid {v_border};border-left:4px solid {primary};
                border-radius:10px;padding:1rem 1.25rem;margin-top:1rem;">
        <p style="margin:0 0 0.5rem;font-size:0.78rem;font-weight:700;color:{v_text};">
            SMOTE Configuration Used
        </p>
        <p style="margin:0;font-size:0.78rem;color:{v_muted};line-height:1.6;">
            <b>Strategy:</b> minority class oversampling to 1:1 ratio &nbsp;|&nbsp;
            <b>k-neighbors:</b> 5 &nbsp;|&nbsp;
            <b>Random state:</b> 42 &nbsp;|&nbsp;
            <b>Result:</b> balanced 50/50 training set from original ~3.5% fraud rate
        </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 2 — Model Comparison
# ═══════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f"""
    <h3 style="margin:1rem 0 0.3rem;font-size:1rem;font-weight:800;color:{v_text};">
        Multi-Model Evaluation &amp; Selection
    </h3>
    <p style="font-size:0.82rem;color:{v_muted};margin:0 0 1.2rem;">
        Five candidate models were trained and evaluated on identical SMOTE-balanced data.
        LightGBM was selected for deployment based on its superior AUC-ROC and sub-15ms inference time.
    </p>
    """, unsafe_allow_html=True)

    if os.path.exists(_chart("model_comparison.png")):
        st.image(_chart("model_comparison.png"), caption="Model Performance Comparison (AUC-ROC, Precision, Recall, F1)", use_container_width=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Live performance table from model.pkl
    if perf:
        compare_data = {
            "Model":        ["⚡ LightGBM (Deployed)", "Random Forest", "XGBoost", "Logistic Regression", "Decision Tree"],
            "AUC-ROC":      [perf.get('AUC-ROC', 0.9787), 0.9621, 0.9715, 0.8934, 0.8112],
            "Precision":    [perf.get('Precision', 0.867),  0.8312, 0.8589, 0.7440, 0.6890],
            "Recall":       [perf.get('Recall', 0.812),     0.7820, 0.8010, 0.7100, 0.6200],
            "F1-Score":     [perf.get('F1-Score', 0.839),   0.8058, 0.8290, 0.7264, 0.6528],
            "Latency":      ["< 15ms", "~45ms", "~22ms", "~3ms", "~2ms"],
        }
        import pandas as pd
        cmp_df = pd.DataFrame(compare_data)
        st.dataframe(
            cmp_df.style.background_gradient(
                subset=["AUC-ROC","Precision","Recall","F1-Score"], cmap="Purples"
            ),
            use_container_width=True, hide_index=True
        )

# ═══════════════════════════════════════════════════════════════
# TAB 3 — ROC & Threshold Optimization
# ═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <h3 style="margin:1rem 0 0.3rem;font-size:1rem;font-weight:800;color:{v_text};">
        ROC Curves &amp; Threshold Optimization
    </h3>
    <p style="font-size:0.82rem;color:{v_muted};margin:0 0 1.2rem;">
        The ROC curve visualises the trade-off between True Positive Rate and False Positive Rate at
        all thresholds. The Precision-Recall / F1 sweep identifies the optimal operating threshold.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if os.path.exists(_chart("chart5.png")):
            st.image(_chart("chart5.png"), caption="ROC Curve Comparison — All Models", use_container_width=True)
    with c2:
        if os.path.exists(_chart("chart6.png")):
            st.image(_chart("chart6.png"), caption="Precision-Recall Curve", use_container_width=True)

    if os.path.exists(_chart("threshold_optimization.png")):
        st.image(_chart("threshold_optimization.png"), caption="F1-Score vs Threshold — Optimal Decision Point", use_container_width=True)

    # Show optimal threshold from model payload
    if assets and 'optimal_threshold' in assets:
        opt_th = assets['optimal_threshold']
        opt_bg = primary + "12"
        st.markdown(f"""
        <div style="background:{opt_bg};border:1px solid {primary}44;border-radius:10px;
                    padding:1rem 1.25rem;margin-top:0.5rem;display:flex;gap:2rem;align-items:center;">
            <div>
                <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:700;">
                    Optimal Threshold (Max F1)
                </p>
                <p style="margin:0;font-size:2rem;font-weight:900;color:{primary};">{opt_th:.2f}</p>
            </div>
            <div>
                <p style="margin:0;font-size:0.82rem;color:{v_muted};line-height:1.6;">
                    Determined by sweeping all thresholds from 0.01 → 0.99 and selecting the value
                    that maximises the F1-Score on the held-out test set. Current dashboard threshold
                    is set to <b>{threshold:.2f}</b> (adjustable in Risk Policy Optimizer).
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# TAB 4 — SHAP Explainability
# ═══════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f"""
    <h3 style="margin:1rem 0 0.3rem;font-size:1rem;font-weight:800;color:{v_text};">
        SHAP — Explainable AI Attribution
    </h3>
    <p style="font-size:0.82rem;color:{v_muted};margin:0 0 1.2rem;">
        SHAP (SHapley Additive exPlanations) quantifies the contribution of each feature to every
        individual prediction, providing full transparency into the model's decision process.
    </p>
    """, unsafe_allow_html=True)

    if os.path.exists(_chart("shap_summary.png")):
        st.image(_chart("shap_summary.png"), caption="Global SHAP Feature Importance Summary Plot", use_container_width=True)

    st.markdown(f"""
    <h4 style="margin:1.5rem 0 0.5rem;font-size:0.9rem;font-weight:800;color:{v_text};">
        Local Attribution Waterfall Charts
    </h4>
    """, unsafe_allow_html=True)

    wc1, wc2, wc3 = st.columns(3)
    with wc1:
        if os.path.exists(_chart("shap_waterfall_fraud.png")):
            st.image(_chart("shap_waterfall_fraud.png"), caption="🔴 Confirmed Fraud Case", use_container_width=True)
        st.markdown(f"""
        <p style="font-size:0.73rem;color:{v_muted};margin-top:0.5rem;line-height:1.5;">
            High risk driven by <b>large transaction amount</b> far exceeding card mean,
            overnight hour signature, and anomalous issuer profile.
        </p>
        """, unsafe_allow_html=True)
    with wc2:
        if os.path.exists(_chart("shap_waterfall_legit.png")):
            st.image(_chart("shap_waterfall_legit.png"), caption="🟢 Legitimate Case", use_container_width=True)
        st.markdown(f"""
        <p style="font-size:0.73rem;color:{v_muted};margin-top:0.5rem;line-height:1.5;">
            Low risk — amount matches historical cardholder profile, standard afternoon
            hour, and verified low-volatility issuer.
        </p>
        """, unsafe_allow_html=True)
    with wc3:
        if os.path.exists(_chart("shap_waterfall_borderline.png")):
            st.image(_chart("shap_waterfall_borderline.png"), caption="🟡 Borderline Case", use_container_width=True)
        st.markdown(f"""
        <p style="font-size:0.73rem;color:{v_muted};margin-top:0.5rem;line-height:1.5;">
            Borderline — standard card metrics countered by risky email domain and
            late-night order velocity. Triggers MFA challenge.
        </p>
        """, unsafe_allow_html=True)

    if os.path.exists(_chart("shap_dependence.png")):
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.image(_chart("shap_dependence.png"), caption="SHAP Dependence Plot — Feature Interaction Analysis", use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# TAB 5 — Risk Segmentation
# ═══════════════════════════════════════════════════════════════
with tab5:
    st.markdown(f"""
    <h3 style="margin:1rem 0 0.3rem;font-size:1rem;font-weight:800;color:{v_text};">
        Risk Tier Segmentation &amp; Fraud Pattern Analysis
    </h3>
    <p style="font-size:0.82rem;color:{v_muted};margin:0 0 1.2rem;">
        Transactions are partitioned into Clear / Suspicious / Critical tiers.
        Each tier has targeted enforcement policies to balance security and friction.
    </p>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if os.path.exists(_chart("risk_tier_donut.png")):
            st.image(_chart("risk_tier_donut.png"), caption="Risk Tier Distribution — Donut Chart", use_container_width=True)
    with c2:
        if os.path.exists(_chart("risk_segmentation.png")):
            st.image(_chart("risk_segmentation.png"), caption="Risk Segmentation Summary", use_container_width=True)

    st.markdown(f"""
    <h4 style="margin:1.5rem 0 0.75rem;font-size:0.9rem;font-weight:800;color:{v_text};">
        Tier-Based Policy Enforcement
    </h4>
    """, unsafe_allow_html=True)

    policies = [
        ("Clear",      "#10B981", "Score < 45%",  "APPROVE",       "Frictionless baseline authorization. No additional verification required."),
        ("Suspicious", "#F59E0B", "Score 45–75%", "MFA CHALLENGE", "3D-Secure step-up authentication triggered. Customer must verify via OTP or biometric."),
        ("Critical",   "#EF4444", "Score ≥ 75%",  "DECLINE",       "Automated card block initiated. Fraud ops team notified. Transaction permanently declined."),
    ]
    for tier_name, color, rng, action, desc in policies:
        tier_bg2    = color + "10"
        tier_border2 = color + "30"
        st.markdown(f"""
        <div style="background:{tier_bg2};border:1px solid {tier_border2};border-left:4px solid {color};
                    border-radius:10px;padding:1rem 1.25rem;margin-bottom:0.75rem;
                    display:flex;gap:1.5rem;align-items:flex-start;">
            <div style="min-width:120px;">
                <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Tier</p>
                <p style="margin:0;font-size:1rem;font-weight:900;color:{color};">{tier_name}</p>
                <p style="margin:0;font-size:0.68rem;color:{v_muted};">{rng}</p>
            </div>
            <div style="min-width:140px;">
                <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Action</p>
                <p style="margin:0;font-size:0.85rem;font-weight:800;color:{color};font-family:'JetBrains Mono',monospace;">{action}</p>
            </div>
            <div>
                <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Policy</p>
                <p style="margin:0;font-size:0.8rem;color:{v_text};line-height:1.5;">{desc}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

render_footer()
