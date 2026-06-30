"""Sentinel AI — Enterprise Risk & Fraud Intelligence Hub: main entrypoint."""

import streamlit as st
try:
    from theme import inject_custom_css, render_footer, init_shared_sidebar
except ModuleNotFoundError:
    from dashboard.theme import inject_custom_css, render_footer, init_shared_sidebar

st.set_page_config(
    page_title="Sentinel AI — Risk Intelligence Hub",
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

v_bg    = "#07060A" if st.session_state.theme_mode == "Professional Black" else "#FFFFFF"
v_card  = "#12101A" if st.session_state.theme_mode == "Professional Black" else "#F8FAFC"
v_text  = "#F3F4F6" if st.session_state.theme_mode == "Professional Black" else "#090D1A"
v_muted = "#6B7280"
primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"
border  = "#1E293B" if st.session_state.theme_mode == "Professional Black" else "#E2E8F0"

# ── Hero Header ───────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center; padding: 3rem 1rem 2rem 1rem;">
    <div style="display:inline-flex; align-items:center; gap:0.5rem;
                background:{v_card}; border:1px solid {border};
                padding:0.3rem 0.9rem; border-radius:20px; margin-bottom:1.5rem;">
        <span style="width:7px;height:7px;background:{primary};border-radius:50%;
                     display:inline-block;box-shadow:0 0 8px {primary};"></span>
        <span style="font-size:0.72rem;font-weight:700;color:{primary};
                     text-transform:uppercase;letter-spacing:0.1em;">
            Live · Sentinel AI v4.0 Active
        </span>
    </div>
    <h1 style="font-size:3rem;font-weight:900;color:{v_text};margin:0;
               letter-spacing:-0.04em;line-height:1.1;">
        Autonomous Fraud<br>Intelligence Console
    </h1>
    <p style="color:{v_muted};font-size:1.05rem;margin:1rem auto 0 auto;
              max-width:580px;line-height:1.6;">
        Real-time ML-powered transaction risk scoring, explainable AI attribution,
        and adaptive policy enforcement for enterprise payment rails.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Headline KPI Strip ────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpis = [
    ("ROC-AUC Score",  "0.9787", "+0.4% vs baseline", primary),
    ("Precision",      "86.7%",  "Calibrated on 3k samples", "#10B981"),
    ("Inference Speed","< 15ms", "LightGBM optimised",  "#F59E0B"),
    ("Fraud Blocked",  "$4.2M",  "Capital shield value", "#EF4444"),
]
for col, (label, val, sub, accent) in zip([k1,k2,k3,k4], kpis):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {border};border-top:3px solid {accent};
                    border-radius:12px;padding:1.25rem 1.1rem;text-align:center;">
            <p style="margin:0;font-size:0.68rem;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.1em;color:{v_muted};">{label}</p>
            <p style="margin:0.3rem 0 0.1rem 0;font-size:2rem;font-weight:900;color:{v_text};">{val}</p>
            <p style="margin:0;font-size:0.72rem;color:{v_muted};">{sub}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────
st.markdown(f"""
<p style="text-align:center;font-size:0.72rem;font-weight:700;text-transform:uppercase;
           letter-spacing:0.1em;color:{primary};margin-bottom:1.25rem;">
    Platform Capabilities
</p>
""", unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)

_icon_shield = f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24"
  fill="none" stroke="{primary}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <path d="M12 2l7 4v5c0 5.25-3.5 9.74-7 11-3.5-1.26-7-5.75-7-11V6z"/>
  <polyline points="9 12 11 14 15 10"/>
</svg>"""

_icon_zap = f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24"
  fill="none" stroke="{primary}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
</svg>"""

_icon_chart = f"""<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24"
  fill="none" stroke="{primary}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="20" x2="18" y2="10"/>
  <line x1="12" y1="20" x2="12" y2="4"/>
  <line x1="6"  y1="20" x2="6"  y2="14"/>
  <line x1="2"  y1="20" x2="22" y2="20"/>
</svg>"""

features = [
    ("Command Center",
     "Real-time anomaly telemetry, live alert queues, risk distribution maps, and interactive threat drill-down.",
     "→ Navigate to Command Center Hub", _icon_shield),
    ("Threat Simulator",
     "Input any transaction scenario and receive instant ML scoring with SHAP decision attribution waterfall.",
     "→ Navigate to Threat Simulator Lab", _icon_zap),
    ("Policy Optimizer",
     "Dynamically tune classification thresholds and visualize financial cost curves for optimal risk policy.",
     "→ Navigate to Risk Policy Optimizer", _icon_chart),
]
for col, (title, desc, cta, icon) in zip([f1, f2, f3], features):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {border};border-radius:14px;
                    padding:1.5rem;height:100%;">
            <div style="width:44px;height:44px;border-radius:10px;
                        background:{primary}18;display:flex;align-items:center;
                        justify-content:center;margin-bottom:1rem;">
                {icon}
            </div>
            <h3 style="margin:0 0 0.5rem 0;font-size:1rem;font-weight:800;color:{v_text};">{title}</h3>
            <p style="margin:0 0 1rem 0;font-size:0.83rem;color:{v_muted};line-height:1.55;">{desc}</p>
            <p style="margin:0;font-size:0.75rem;font-weight:700;color:{primary};">{cta}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)

# ── Pipeline Steps ────────────────────────────────────────────
st.markdown(f"""
<p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
          letter-spacing:0.1em;color:{primary};margin-bottom:1rem;">
    How It Works
</p>
""", unsafe_allow_html=True)

stages = [
    ("01", "Transaction Ingestion",
     "Payment rails dispatch amount, card brand, funding type, and email domain to the Sentinel API."),
    ("02", "Feature Engineering",
     "Engine computes log transforms, amount ratios, device risk flags, and domain risk indices in memory."),
    ("03", "ML Inference",
     "LightGBM classifier scores risk probability in under 15ms using SMOTE-balanced training data."),
    ("04", "Policy Enforcement",
     "Score is compared against threshold — Approve, MFA Challenge, or Decline is dispatched to processors."),
]
pc = st.columns(4)
for col, (num, title, desc) in zip(pc, stages):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {border};border-radius:12px;
                    border-top:3px solid {primary};padding:1.1rem;">
            <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                        font-weight:700;color:{primary};margin-bottom:0.5rem;">
                STAGE {num}
            </div>
            <h4 style="margin:0 0 0.5rem 0;font-size:0.88rem;font-weight:800;color:{v_text};">{title}</h4>
            <p style="margin:0;font-size:0.78rem;color:{v_muted};line-height:1.5;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

render_footer()
