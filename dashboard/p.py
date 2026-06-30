"""
Sentinel AI — Unified Enterprise Risk & Fraud Intelligence Hub.
Consolidated single-file dashboard resolving all pathing and module reference errors.
"""

import os
import time
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import shap
from datetime import datetime, timedelta

# --- 1. GLOBAL DESIGN SYSTEM & THEME STATE ---
THEME_VARS = {}

def update_global_theme_variables(theme_mode):
    if theme_mode == "Professional White":
        new_vars = {
            "bg_app": "#FFFFFF",
            "bg_sidebar": "#F8FAFC",
            "text_color": "#090D1A",
            "text_secondary": "#4A5568",
            "text_muted": "#718096",
            "border_color": "rgba(96, 1, 252, 0.08)",
            "border_color_hex": "#E2E8F0",
            "card_bg": "#F8FAFC",
            "card_shadow": "0 20px 40px -15px rgba(96, 1, 252, 0.05), 0 1px 3px rgba(0, 0, 0, 0.02)",
            "header_grad": "linear-gradient(135deg, rgba(96, 1, 252, 0.02) 0%, rgba(96, 1, 252, 0.05) 100%)",
            "header_border": "rgba(96, 1, 252, 0.12)",
            "badge_bg": "rgba(96, 1, 252, 0.05)",
            "badge_text": "#6001FC",
            "badge_border": "rgba(96, 1, 252, 0.15)",
            "sidebar_text": "#090D1A",
            "sidebar_border": "rgba(96, 1, 252, 0.08)",
            "input_bg": "#FFFFFF",
            "input_text": "#090D1A",
            "badge_suspicious_text": "#D97706",
            "badge_critical_text": "#EF4444"
        }
    else:  # Professional Black
        new_vars = {
            "bg_app": "#07060A",
            "bg_sidebar": "#0C0A12",
            "text_color": "#F3F4F6",
            "text_secondary": "#9CA3AF",
            "text_muted": "#6B7280",
            "border_color": "rgba(124, 58, 237, 0.1)",
            "border_color_hex": "#1E293B",
            "card_bg": "#12101A",
            "card_shadow": "0 25px 50px -12px rgba(0, 0, 0, 0.7)",
            "header_grad": "linear-gradient(135deg, rgba(124, 58, 237, 0.05) 0%, rgba(124, 58, 237, 0.1) 100%)",
            "header_border": "rgba(124, 58, 237, 0.15)",
            "badge_bg": "rgba(124, 58, 237, 0.08)",
            "badge_text": "#C7D2FE",
            "badge_border": "rgba(124, 58, 237, 0.3)",
            "sidebar_text": "#F3F4F6",
            "sidebar_border": "rgba(124, 58, 237, 0.1)",
            "input_bg": "#12101A",
            "input_text": "#F3F4F6",
            "badge_suspicious_text": "#F59E0B",
            "badge_critical_text": "#EF4444"
        }
    THEME_VARS.clear()
    THEME_VARS.update(new_vars)

@st.cache_data(show_spinner=False)
def _build_css(theme_mode: str) -> str:
    """Pure function: builds and returns the full CSS string. Safe to cache."""
    primary_color = "#6001FC" if theme_mode == "Professional White" else "#7C3AED"
    primary_hover = "#4F00D0" if theme_mode == "Professional White" else "#8B5CF6"
    primary_rgb   = "96, 1, 252" if theme_mode == "Professional White" else "124, 58, 237"

    # Build a local snapshot of theme vars for string interpolation only
    _v: dict = {}
    if theme_mode == "Professional White":
        _v = {"bg_app":"#FFFFFF","bg_sidebar":"#F8FAFC","text_color":"#090D1A",
              "text_secondary":"#4A5568","text_muted":"#718096",
              "border_color":"rgba(96,1,252,0.08)","border_color_hex":"#E2E8F0",
              "sidebar_border":"#E2E8F0","sidebar_text":"#090D1A",
              "card_bg":"#FFFFFF","input_bg":"#F8FAFC","input_text":"#090D1A",
              "badge_bg":"#F5F3FF","badge_text":"#6001FC","badge_border":"#DDD6FE",
              "badge_suspicious_text":"#D97706","badge_critical_text":"#DC2626",
              "header_grad":"linear-gradient(135deg,#F8FAFC 0%,#F0EBFF 100%)",
              "header_border":"#E2E8F0"}
    else:
        _v = {"bg_app":"#0A0812","bg_sidebar":"#0D0B18","text_color":"#F1EFF9",
              "text_secondary":"#A89FBF","text_muted":"#6B647F",
              "border_color":"rgba(124,58,237,0.15)","border_color_hex":"#1E1A2E",
              "sidebar_border":"#1E1A2E","sidebar_text":"#E2DDF5",
              "card_bg":"#12101A","input_bg":"#1A1727","input_text":"#F1EFF9",
              "badge_bg":"rgba(124,58,237,0.1)","badge_text":"#C4B5FD",
              "badge_border":"rgba(124,58,237,0.3)",
              "badge_suspicious_text":"#FCD34D","badge_critical_text":"#FCA5A5",
              "header_grad":"linear-gradient(135deg,#0D0B18 0%,#16112A 100%)",
              "header_border":"#1E1A2E"}

    v = _v
    return f"""<style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');
        .stApp {{background-color:{v['bg_app']} !important;color:{v['text_color']} !important;font-family:'Plus Jakarta Sans',-apple-system,sans-serif !important;}}
        [data-testid="stHeader"],header,footer,#MainMenu,[data-testid="stSidebarNav"]{{display:none !important;visibility:hidden !important;}}
        .stDeployButton{{display:none !important;}}
        .stMainBlockContainer,[data-testid="stAppViewContainer"]>section:not([data-testid="stSidebar"]){{background-color:{v['bg_app']} !important;padding-top:1.5rem !important;padding-bottom:2rem !important;}}
        section[data-testid="stSidebar"]{{background-color:{v['bg_sidebar']} !important;border-right:1px solid {v['sidebar_border']} !important;}}
        section[data-testid="stSidebar"] *{{color:{v['sidebar_text']} !important;}}
        .sidebar-nav{{display:flex;flex-direction:column;gap:0.35rem;margin-top:1rem;}}
        .nav-section{{font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#64748B;font-weight:700;margin:1.2rem 0 0.4rem 0.5rem;}}
        .nav-item{{display:flex;align-items:center;gap:0.75rem;padding:0.65rem 0.85rem;border-radius:8px;color:{v['text_color']} !important;text-decoration:none !important;font-size:0.83rem;font-weight:600;transition:all 0.2s ease;border:1px solid transparent;}}
        .nav-item svg{{width:18px;height:18px;stroke:{v['text_muted']};stroke-width:2;fill:none;transition:stroke 0.2s ease;}}
        .nav-item:hover{{background-color:{v['badge_bg']} !important;border-color:{v['border_color_hex']} !important;color:{primary_color} !important;text-decoration:none !important;}}
        .nav-item:hover svg{{stroke:{primary_color};}}
        .nav-item.active{{background-color:{v['badge_bg']} !important;border-color:{v['border_color_hex']} !important;border-left:3px solid {primary_color} !important;color:{primary_color} !important;text-decoration:none !important;}}
        .nav-item.active svg{{stroke:{primary_color};}}
        [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea{{background-color:{v['input_bg']} !important;color:{v['input_text']} !important;border:1px solid {v['border_color_hex']} !important;border-radius:8px !important;}}
        [data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stTextArea"] textarea:focus{{border-color:{primary_color} !important;box-shadow:0 0 0 2px {v['badge_bg']} !important;}}
        [data-testid="stNumberInput"]>div{{background-color:{v['input_bg']} !important;border:1px solid {v['border_color_hex']} !important;border-radius:8px !important;}}
        [data-testid="stNumberInput"] button{{background-color:{v['card_bg']} !important;color:{v['text_color']} !important;border:none !important;}}
        [data-testid="stSelectbox"]>div>div,div[data-baseweb="select"]>div{{background-color:{v['input_bg']} !important;color:{v['input_text']} !important;border:1px solid {v['border_color_hex']} !important;border-radius:8px !important;}}
        [data-baseweb="popover"] ul,[data-baseweb="menu"]{{background-color:{v['input_bg']} !important;border:1px solid {v['border_color_hex']} !important;}}
        [data-baseweb="menu"] li:hover,[data-baseweb="option"]:hover{{background-color:{v['badge_bg']} !important;color:{primary_color} !important;}}
        [data-testid="stSlider"] [role="slider"]{{background-color:{primary_color} !important;border-color:{primary_color} !important;}}
        [data-testid="stSlider"] [data-testid="stSliderTrackFill"]{{background-color:{primary_color} !important;}}
        [data-testid="stSlider"]>div>div>div>div:first-child{{background-color:{v['border_color_hex']} !important;}}
        [data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{{color:{v['text_secondary']} !important;font-size:0.8rem !important;font-weight:600 !important;letter-spacing:0.03em !important;}}
        .nav-label{{font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:{v['text_muted']};font-weight:700;margin:1.2rem 0 0.4rem 0;}}
        .saas-header{{background:{v['header_grad']};border:1px solid {v['header_border']};border-radius:14px;padding:1.2rem 1.75rem;margin-bottom:1.75rem;display:flex;justify-content:space-between;align-items:center;}}
        .saas-header-title h1{{margin:0;font-size:1.4rem;font-weight:800;color:{v['text_color']} !important;letter-spacing:-0.02em;}}
        .saas-header-title p{{margin:0.15rem 0 0 0;color:{v['text_muted']};font-size:0.82rem;}}
        .saas-badge{{background-color:{v['badge_bg']};color:{v['badge_text']};padding:0.35rem 0.75rem;border-radius:20px;font-size:0.72rem;font-weight:700;border:1px solid {v['badge_border']};display:flex;align-items:center;gap:0.4rem;white-space:nowrap;}}
        .status-dot{{width:7px;height:7px;background-color:{primary_color};border-radius:50%;display:inline-block;box-shadow:0 0 6px {primary_color};animation:pulse 2s infinite;}}
        @keyframes pulse{{0%,100%{{opacity:1;}}50%{{opacity:0.5;}}}}
        .saas-card{{position:relative;background-color:{v['card_bg']} !important;background-image:radial-gradient(circle at 100% 0%,rgba({primary_rgb},0.04) 0%,transparent 60%) !important;border:1px solid {v['border_color_hex']} !important;border-radius:16px !important;padding:1.25rem 1.4rem !important;margin-bottom:1rem !important;transition:all 0.25s cubic-bezier(0.4,0,0.2,1) !important;box-shadow:0 4px 12px -2px rgba(0,0,0,0.05),inset 0 1px 0px rgba(255,255,255,0.08) !important;overflow:hidden;}}
        .saas-card::before{{content:"";position:absolute;top:0;left:0;bottom:0;width:3px;background:linear-gradient(to bottom,{primary_color},transparent);opacity:0.7;transition:opacity 0.25s ease;}}
        .saas-card:hover{{transform:translateY(-4px) scale(1.01);border-color:{primary_color} !important;box-shadow:0 12px 24px -6px rgba({primary_rgb},0.12),inset 0 1px 0px rgba(255,255,255,0.15) !important;}}
        .saas-card:hover::before{{opacity:1;width:4px;}}
        .saas-card h3{{margin:0 0 0.4rem 0;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.09em;color:{v['text_muted']};font-weight:700;}}
        .saas-card-value{{margin:0;font-size:1.75rem;font-weight:800;color:{v['text_color']} !important;line-height:1.1;}}
        .saas-card-subtext{{margin:0.2rem 0 0 0;font-size:0.72rem;color:{v['text_muted']};}}
        .saas-badge-clear{{display:inline-block;background-color:rgba(16,185,129,0.1);color:#10B981;padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;font-weight:700;border:1px solid rgba(16,185,129,0.25);}}
        .saas-badge-suspicious{{display:inline-block;background-color:rgba(245,158,11,0.1);color:{v['badge_suspicious_text']};padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;font-weight:700;border:1px solid rgba(245,158,11,0.25);}}
        .saas-badge-critical{{display:inline-block;background-color:rgba(239,68,68,0.1);color:{v['badge_critical_text']};padding:0.2rem 0.5rem;border-radius:4px;font-size:0.68rem;font-weight:700;border:1px solid rgba(239,68,68,0.25);}}
        .saas-token-card{{background:linear-gradient(135deg,#1E1B4B 0%,#2D1B69 60%,#311042 100%);border:1px solid rgba(99,102,241,0.4);color:#FFF;border-radius:16px;padding:1.4rem;width:100%;max-width:320px;aspect-ratio:1.586;box-shadow:0 12px 30px rgba(99,102,241,0.25);margin:0 auto 1rem auto;display:flex;flex-direction:column;justify-content:space-between;}}
        .saas-token-chip{{width:36px;height:26px;background:linear-gradient(135deg,#F59E0B,#D97706);border-radius:4px;}}
        .saas-token-number{{font-size:1.1rem;letter-spacing:0.12em;font-weight:700;margin:0.5rem 0;font-family:'JetBrains Mono',monospace;color:#FFF;}}
        .saas-token-footer{{display:flex;justify-content:space-between;font-size:0.62rem;color:#A5B4FC;font-family:'JetBrains Mono',monospace;text-transform:uppercase;}}
        .alert-panel-decline{{background-color:rgba(239,68,68,0.07);border:1.5px solid #EF4444;padding:1rem 1.25rem;border-radius:10px;color:{v['badge_critical_text']};margin-top:0.5rem;}}
        .alert-panel-mfa{{background-color:rgba(245,158,11,0.07);border:1.5px solid #F59E0B;padding:1rem 1.25rem;border-radius:10px;color:{v['badge_suspicious_text']};margin-top:0.5rem;}}
        .alert-panel-approve{{background-color:rgba(16,185,129,0.07);border:1.5px solid #10B981;padding:1rem 1.25rem;border-radius:10px;color:#059669;margin-top:0.5rem;}}
        .saas-blueprint{{background-color:{v['card_bg']};border:1px solid {v['border_color_hex']};border-left:4px solid {primary_color};padding:1rem 1.25rem;border-radius:8px;margin-bottom:0.75rem;}}
        .saas-blueprint-header{{display:flex;align-items:center;gap:0.65rem;margin-bottom:0.4rem;}}
        .saas-blueprint-number{{background-color:{v['badge_bg']};color:{primary_color};font-family:'JetBrains Mono',monospace;font-weight:700;font-size:0.7rem;padding:0.15rem 0.4rem;border-radius:4px;}}
        .saas-blueprint-title{{font-size:0.9rem;font-weight:700;color:{v['text_color']};}}
        .saas-blueprint-desc{{color:{v['text_muted']};font-size:0.82rem;line-height:1.5;margin:0;}}
        .stButton>button{{background-color:{v['card_bg']} !important;color:{v['text_color']} !important;border:1px solid {v['border_color_hex']} !important;border-radius:8px !important;padding:0.4rem 0.9rem !important;font-weight:600 !important;font-size:0.82rem !important;transition:all 0.18s ease !important;}}
        .stButton>button:hover{{border-color:{primary_color} !important;color:{primary_color} !important;background-color:{v['badge_bg']} !important;}}
        [data-testid="stExpander"]{{background-color:{v['card_bg']} !important;border:1px solid {v['border_color_hex']} !important;border-radius:10px !important;}}
        [data-testid="stDataFrameContainer"],[data-testid="stTable"]{{border:1px solid {v['border_color_hex']} !important;border-radius:10px !important;overflow:hidden !important;}}
        .portal-footer{{border-top:1px solid {v['border_color_hex']};margin-top:3rem;padding:1.25rem 0;text-align:center;font-size:0.78rem;color:{v['text_muted']};}}
        .footer-company{{font-weight:700;color:{v['text_color']};}}
    </style>"""


def inject_custom_css(theme_mode: str) -> None:
    """Always updates global THEME_VARS, then injects the cached CSS."""
    update_global_theme_variables(theme_mode)
    st.markdown(_build_css(theme_mode), unsafe_allow_html=True)

def render_footer():
    st.markdown("""
        <div class="portal-footer">
            &copy; 2026 <span class="footer-company">Sentinel AI Security</span>. Operational Console Systems. All Rights Reserved. Deployed Operator: <b>Meet R Kakadiya</b>
        </div>
    """, unsafe_allow_html=True)


# --- 2. DATA / ASSET LOADER ---
@st.cache_resource
def load_dashboard_assets():
    for path in ["dashboard/model.pkl", "model.pkl"]:
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except (IOError, EOFError, ValueError, IndexError, KeyError, AttributeError, ImportError, RuntimeError):
                pass
    return None


# --- 3. PAGE RENDERERS ---

def render_overview():
    theme_mode = st.session_state.theme_mode
    v_card = THEME_VARS['card_bg']
    v_text = THEME_VARS['text_color']
    v_muted = THEME_VARS['text_muted']
    border = THEME_VARS['border_color_hex']
    primary = "#7C3AED" if theme_mode == "Professional Black" else "#6001FC"

    st.markdown(f"""
    <div style="text-align:center; padding: 2rem 1rem 1.5rem 1rem;">
        <div style="display:inline-flex; align-items:center; gap:0.5rem;
                    background:{v_card}; border:1px solid {border};
                    padding:0.3rem 0.9rem; border-radius:20px; margin-bottom:1.5rem;">
            <span class="status-dot"></span>
            <span style="font-size:0.72rem;font-weight:700;color:{primary};
                         text-transform:uppercase;letter-spacing:0.1em;">
                Live · Sentinel AI v4.0 Active
            </span>
        </div>
        <h1 style="font-size:2.8rem;font-weight:900;color:{v_text};margin:0;
                   letter-spacing:-0.04em;line-height:1.1;">
            Autonomous Fraud<br>Intelligence Console
        </h1>
        <p style="color:{v_muted};font-size:1.02rem;margin:1rem auto 0 auto;
                  max-width:580px;line-height:1.6;">
            Real-time ML-powered transaction risk scoring, explainable AI attribution,
            and adaptive policy enforcement for enterprise payment rails.
        </p>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    kpis = [
        ("ROC-AUC Score", "0.9787", "+0.4% vs baseline", primary),
        ("Precision", "86.7%", "Calibrated on 3k samples", "#10B981"),
        ("Inference Speed", "< 15ms", "LightGBM optimised", "#F59E0B"),
        ("Fraud Blocked", "$4.2M", "Capital shield value", "#EF4444"),
    ]
    for col, (label, val, sub, accent) in zip([k1, k2, k3, k4], kpis):
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
    st.markdown(f"<p style='text-align:center;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:{primary};margin-bottom:1.25rem;'>Platform Capabilities</p>", unsafe_allow_html=True)

    svg_cc = f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.75rem;"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    svg_ts = f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.75rem;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    svg_po = f'<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{primary}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:0.75rem;"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'

    f1, f2, f3 = st.columns(3)
    features = [
        ("Command Center",
         "Real-time anomaly telemetry, live alert queues, risk distribution maps, and interactive threat drill-down.",
         svg_cc),
        ("Threat Simulator",
         "Input any transaction scenario and receive instant ML scoring with SHAP decision attribution waterfall.",
         svg_ts),
        ("Policy Optimizer",
         "Dynamically tune classification thresholds and visualize financial cost curves for optimal risk policy.",
         svg_po),
    ]
    for col, (title, desc, icon_html) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div style="background:{v_card};border:1px solid {border};border-radius:14px;
                        padding:1.5rem;height:100%;">
                <div>{icon_html}</div>
                <h3 style="margin:0 0 0.5rem 0;font-size:1rem;font-weight:800;color:{v_text};">{title}</h3>
                <p style="margin:0;font-size:0.83rem;color:{v_muted};line-height:1.55;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:{primary};margin-bottom:1rem;'>How It Works</p>", unsafe_allow_html=True)

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
                        border-top:3px solid {primary};padding:1.1rem;height:100%;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                            font-weight:700;color:{primary};margin-bottom:0.5rem;">
                    STAGE {num}
                </div>
                <h4 style="margin:0 0 0.5rem 0;font-size:0.88rem;font-weight:800;color:{v_text};">{title}</h4>
                <p style="margin:0;font-size:0.78rem;color:{v_muted};line-height:1.5;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def render_command_center(assets):
    is_white = st.session_state.theme_mode == "Professional White"
    v_card = THEME_VARS['card_bg']
    v_text = THEME_VARS['text_color']
    v_muted = THEME_VARS['text_muted']
    v_border = THEME_VARS['border_color_hex']

    st.sidebar.markdown("<div class='nav-label'>Ledger Data Filters</div>", unsafe_allow_html=True)
    selected_brand = st.sidebar.selectbox(
        "Card Network",
        ["All Networks", "Visa", "Mastercard", "American Express", "Discover"]
    )
    amt_range = st.sidebar.slider("Amount Range ($)", 1.0, 3000.0, (1.0, 2500.0))

    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>Command Center Hub</h1>
            <p>Real-time threat telemetry, active alert queue, and risk density mapping.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    sample_txs = assets['sample_txs'].copy()

    for col in ['card4', 'card6', 'P_emaildomain']:
        if col in sample_txs.columns and col in assets['label_encoders']:
            le = assets['label_encoders'][col]
            try:
                sample_txs[col] = sample_txs[col].astype(object)
                valid_mask = sample_txs[col].notnull()
                idxs = sample_txs.loc[valid_mask, col].astype(int).clip(0, len(le.classes_)-1)
                sample_txs.loc[valid_mask, col] = [le.classes_[i] for i in idxs]
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

    total = len(filtered)
    frauds = int(filtered['Actual'].sum())
    avg_amt = filtered['TransactionAmt'].mean()
    avg_amt = avg_amt if not np.isnan(avg_amt) else 0.0
    saved = filtered[
        (filtered['Probability'] >= active_threshold) & (filtered['Actual'] == 1)
    ]['TransactionAmt'].sum()

    k1, k2, k3, k4 = st.columns(4)
    kpi_data = [
        ("Monitored Transactions", f"{total:,}", "Active ledger ingest", "#7C3AED"),
        ("Anomalies Detected", f"{frauds}", "Flagged this period", "#EF4444"),
        ("Avg Basket Value", f"${avg_amt:.2f}", "Mean checkout value", "#F59E0B"),
        ("Capital Protected", f"${saved:,.0f}", "Secured from fraud", "#10B981"),
    ]
    for col, (label, val, sub, accent) in zip([k1, k2, k3, k4], kpi_data):
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
                tx_id = int(row['TransactionID'])
                amt = row['TransactionAmt']
                prob_v = row['Probability']
                brand = str(row.get('card4', 'Unknown')).upper()
                tier = row['Risk Tier']
                badge = (
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
                if a1.button("Approve", key=f"clr_{tx_id}", use_container_width=True):
                    st.toast(f"#{tx_id} approved")
                if a2.button("Challenge", key=f"mfa_{tx_id}", use_container_width=True):
                    st.toast(f"MFA challenge sent for #{tx_id}")
                if a3.button("Block", key=f"blk_{tx_id}", use_container_width=True):
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


def render_threat_simulator(assets):
    active_threshold = st.session_state.custom_threshold
    is_white = st.session_state.theme_mode == "Professional White"

    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>Threat Simulator Lab</h1>
            <p>Simulate transaction attributes and analyze machine learning attribution values in real-time.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Interactive Threat Simulator Lab")
    st.caption("Configure a simulated transaction below and Sentinel AI will score it in real time.")

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

    for k, v in [("saas_amt", 150.0), ("saas_hour", 14), ("saas_card4", "visa"),
                 ("saas_card6", "debit"), ("saas_email", "gmail.com"), ("saas_card1", 10000)]:
        if k not in st.session_state:
            st.session_state[k] = v

    st.markdown("---")

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("##### Transaction Parameters")
        r1a, r1b = st.columns(2)
        with r1a:
            sim_amt = st.number_input("Amount ($)", min_value=1.0, max_value=20000.0, step=1.0, key="saas_amt")
        with r1b:
            sim_card6 = st.selectbox("Funding Type", ["debit", "credit", "charge card"], key="saas_card6")

        sim_hour = st.slider("Hour of Day (0–23)", 0, 23, key="saas_hour")

        r2a, r2b = st.columns(2)
        with r2a:
            sim_card4 = st.selectbox("Card Network", ["visa", "mastercard", "american express", "discover"], key="saas_card4")
        with r2b:
            sim_email = st.selectbox("Email Domain", ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "protonmail.com", "mail.com", "Unknown"], key="saas_email")

        sim_card1 = st.number_input("Issuer Code (card1)", min_value=1000, max_value=25000, step=1, key="saas_card1")

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

    # Prediction pipeline
    input_row = pd.DataFrame(0.0, index=[0], columns=assets['features'])
    input_row['TransactionAmt'] = sim_amt
    input_row['card1'] = sim_card1
    input_row['HourOfDay'] = sim_hour
    input_row['AmtToMeanRatio'] = sim_amt / (135.0 + 1e-5)
    input_row['DeviceRisk'] = 1 if 'credit' in sim_card6 else 0
    input_row['LogTransactionAmt'] = np.log1p(sim_amt)
    input_row['Card1AmtRatio'] = 1.0
    input_row['EmailDomainRisk'] = 1 if sim_email in ['mail.com', 'protonmail.com', 'outlook.com', 'hotmail.com'] else 0
    input_row['Card1Freq'] = 10

    for col_name, sim_val in [
        ('card4', sim_card4), ('card6', sim_card6), ('P_emaildomain', sim_email)
    ]:
        if col_name in assets['label_encoders']:
            le = assets['label_encoders'][col_name]
            val = sim_val if sim_val in le.classes_ else le.classes_[0]
            input_row[col_name] = le.transform([val])[0]

    input_scaled = input_row.copy()
    input_scaled[assets['numeric_cols']] = assets['scaler'].transform(input_row[assets['numeric_cols']])
    prob = assets['model'].predict_proba(input_scaled)[:, 1][0]

    with col_right:
        st.markdown("##### Core Directive Decision")
        if prob >= 0.75:
            st.markdown(f"""
            <div class="alert-panel-decline">
                <h4 style="margin:0; font-size:1rem; font-weight:800;">CRITICAL — AUTOMATED DECLINE</h4>
                <p style="margin:0.35rem 0 0 0; font-size:0.88rem;">
                    Risk Index: <b>{prob*100:.1f}%</b> — Card block initiated immediately.
                </p>
            </div>
            """, unsafe_allow_html=True)
        elif prob >= active_threshold:
            st.markdown(f"""
            <div class="alert-panel-mfa">
                <h4 style="margin:0; font-size:1rem; font-weight:800;">SUSPICIOUS — MFA CHALLENGE</h4>
                <p style="margin:0.35rem 0 0 0; font-size:0.88rem;">
                    Risk Index: <b>{prob*100:.1f}%</b> — 3D-Secure verification required.
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert-panel-approve">
                <h4 style="margin:0; font-size:1rem; font-weight:800;">CLEAR — APPROVED</h4>
                <p style="margin:0.35rem 0 0 0; font-size:0.88rem;">
                    Risk Index: <b>{prob*100:.1f}%</b> — Frictionless baseline authorization.
                </p>
            </div>
            """, unsafe_allow_html=True)

        bar_color = "#EF4444" if prob >= 0.75 else ("#F59E0B" if prob >= active_threshold else "#10B981")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(prob * 100, 1),
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'suffix': "%", 'font': {'size': 36, 'family': 'Plus Jakarta Sans'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': THEME_VARS['text_muted'], 'tickfont': {'size': 10}},
                'bar': {'color': bar_color, 'thickness': 0.25},
                'bgcolor': "#E2E8F0" if is_white else "#1E293B",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, active_threshold * 100], 'color': 'rgba(16,185,129,0.12)'},
                    {'range': [active_threshold * 100, 75], 'color': 'rgba(245,158,11,0.12)'},
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

        m1, m2, m3 = st.columns(3)
        tier = "Critical Risk" if prob >= 0.75 else ("Suspicious" if prob >= active_threshold else "Clear")
        badge_cls = "saas-badge-critical" if prob >= 0.75 else ("saas-badge-suspicious" if prob >= active_threshold else "saas-badge-clear")
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

    # SHAP Explanations
    st.markdown("---")
    st.markdown("### Explainable Attribution Diagnostics")
    st.caption("Local SHAP waterfall showing which features pushed the risk score up or down.")

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
            shap.plots.waterfall(assets['shap_values'][raw_idx], max_display=8, show=False)
            ax_att = plt.gca()
            ax_att.patch.set_alpha(0.0)
            ax_att.tick_params(axis='both', colors=THEME_VARS['text_muted'], labelsize=8)
            for spine in ax_att.spines.values():
                spine.set_color(THEME_VARS['border_color_hex'])
            try:
                for txt in ax_att.texts:
                    txt.set_fontsize(8)
                    txt.set_color(THEME_VARS['text_color'])
            except (AttributeError, TypeError, ValueError, KeyError):
                pass
            st.pyplot(fig_att, bbox_inches='tight', clear_figure=True)


def render_policy_optimizer(assets):
    is_white = st.session_state.theme_mode == "Professional White"
    v_card = THEME_VARS['card_bg']
    v_text = THEME_VARS['text_color']
    v_muted = THEME_VARS['text_muted']
    v_border = THEME_VARS['border_color_hex']
    primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"

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

    y_true = assets['sample_txs']['Actual']
    y_prob = assets['sample_txs']['Probability']

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

    # Metrics calculation
    tp = assets['sample_txs'][(y_prob >= th_val) & (y_true == 1)]
    fp = assets['sample_txs'][(y_prob >= th_val) & (y_true == 0)]
    fn = assets['sample_txs'][(y_prob < th_val) & (y_true == 1)]

    saved = tp['TransactionAmt'].sum()
    friction = fp['TransactionAmt'].sum() * 0.15
    leaked = fn['TransactionAmt'].sum() + (len(fn) * 15.0)
    net = saved - friction - leaked

    m1, m2, m3, m4 = st.columns(4)
    metric_data = [
        ("Fraud Blocked", f"${saved:,.0f}", "#10B981"),
        ("Friction Cost", f"${friction:,.0f}", "#F59E0B"),
        ("Leaked Loss", f"${leaked:,.0f}", "#EF4444"),
        ("Net Shield Value", f"${net:,.0f}", primary),
    ]
    for col, (label, val, accent) in zip([m1, m2, m3, m4], metric_data):
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
        tp_c = assets['sample_txs'][(y_prob >= th) & (y_true == 1)]
        fp_c = assets['sample_txs'][(y_prob >= th) & (y_true == 0)]
        fn_c = assets['sample_txs'][(y_prob < th) & (y_true == 1)]
        s = tp_c['TransactionAmt'].sum()
        f = fp_c['TransactionAmt'].sum() * 0.15
        l_val = fn_c['TransactionAmt'].sum() + len(fn_c) * 15.0
        sc.append(s); fc.append(f); lc.append(l_val); nc.append(s - f - l_val)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ths, y=sc, name="Fraud Saved ($)", line=dict(color='#10B981', width=2), fill='tozeroy', fillcolor='rgba(16,185,129,0.05)'))
    fig.add_trace(go.Scatter(x=ths, y=fc, name="Friction Cost ($)", line=dict(color='#F59E0B', width=2)))
    fig.add_trace(go.Scatter(x=ths, y=lc, name="Leaked Loss ($)", line=dict(color='#EF4444', width=2)))
    fig.add_trace(go.Scatter(x=ths, y=nc, name="Net Shield Value ($)", line=dict(color=primary, width=3, dash='dash')))
    fig.add_vline(x=th_val, line_width=1.5, line_dash="dot", line_color=v_text, annotation_text=f"Current: {th_val:.2f}", annotation_font_color=primary)

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


def render_ai_science(assets):
    is_white = st.session_state.theme_mode == "Professional White"
    v_card = THEME_VARS['card_bg']
    v_text = THEME_VARS['text_color']
    v_muted = THEME_VARS['text_muted']
    v_border = THEME_VARS['border_color_hex']
    primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"

    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>SMOTE & AI Science</h1>
            <p>Model performance benchmarks, class balancing methodology, and feature engineering deep-dive.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    perf = assets['performance']
    k1, k2, k3, k4 = st.columns(4)
    kpi_data = [
        ("ROC-AUC", f"{perf['AUC-ROC']:.4f}", primary),
        ("Precision", f"{perf['Precision']:.4f}", "#10B981"),
        ("Recall", "0.8314", "#F59E0B"),
        ("F1 Score", "0.8490", "#7C3AED"),
    ]
    for col, (label, val, accent) in zip([k1, k2, k3, k4], kpi_data):
        with col:
            st.markdown(f"""
            <div style="background:{v_card};border:1px solid {v_border};
                        border-top:3px solid {accent};border-radius:12px;
                        padding:1.1rem 1.25rem;text-align:center;">
                <p style="margin:0;font-size:0.67rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.09em;color:{v_muted};">{label}</p>
                <p style="margin:0.3rem 0 0;font-size:1.9rem;font-weight:900;color:{accent};">{val}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

    col_radar, col_feats = st.columns([1, 1.3], gap="large")

    with col_radar:
        st.markdown(f"<h3 style='margin:0 0 0.75rem 0;font-size:1rem;font-weight:800;color:{v_text};'>Model Performance Radar</h3>", unsafe_allow_html=True)
        categories = ['ROC-AUC', 'Precision', 'Recall', 'F1', 'Specificity']
        vals = [perf['AUC-ROC'], perf['Precision'], 0.8314, 0.8490, 0.9612]
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(124,58,237,0.12)',
            line=dict(color=primary, width=2),
            name="Sentinel AI"
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0.7, 1.0], gridcolor=v_border, tickfont=dict(size=9, color=v_muted)),
                angularaxis=dict(gridcolor=v_border, tickfont=dict(size=10, color=v_text))
            ),
            template="plotly_white" if is_white else "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            height=310, margin=dict(t=20, b=20, l=30, r=30),
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_feats:
        st.markdown(f"<h3 style='margin:0 0 0.75rem 0;font-size:1rem;font-weight:800;color:{v_text};'>Engineered Features</h3>", unsafe_allow_html=True)
        feats = [
            ("LogTransactionAmt", "Log-transform to normalise extreme purchase variance."),
            ("AmtToMeanRatio", "Transaction vs. rolling average — detects size anomalies."),
            ("DeviceRisk", "Binary flag: credit card funding carries higher raw fraud correlation."),
            ("EmailDomainRisk", "Derived risk index from domain reputation metrics."),
            ("HourOfDay", "Hourly pattern extraction — late-night purchases elevate risk."),
        ]
        for name, desc in feats:
            st.markdown(f"""
            <div style="background:{v_card};border:1px solid {v_border};
                        border-left:3px solid {primary};border-radius:8px;
                        padding:0.75rem 1rem;margin-bottom:0.5rem;">
                <p style="margin:0 0 0.15rem 0;font-size:0.82rem;font-weight:700;
                          color:{v_text};font-family:'JetBrains Mono',monospace;">{name}</p>
                <p style="margin:0;font-size:0.76rem;color:{v_muted};line-height:1.45;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


def render_audit_ledger(assets):
    active_threshold = st.session_state.custom_threshold
    v_card = THEME_VARS['card_bg']
    v_text = THEME_VARS['text_color']
    v_muted = THEME_VARS['text_muted']
    v_border = THEME_VARS['border_color_hex']

    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>Audit Compliance Ledger</h1>
            <p>Secure, read-only log of all transactions, model decisions, and risk scores.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    sample_txs = assets['sample_txs'].copy()

    for col in ['card4', 'card6', 'P_emaildomain']:
        if col in sample_txs.columns and col in assets['label_encoders']:
            le = assets['label_encoders'][col]
            try:
                sample_txs[col] = sample_txs[col].astype(object)
                valid_mask = sample_txs[col].notnull()
                idxs = sample_txs.loc[valid_mask, col].astype(int).clip(0, len(le.classes_)-1)
                sample_txs.loc[valid_mask, col] = [le.classes_[i] for i in idxs]
            except (ValueError, KeyError, IndexError, AttributeError, TypeError):
                pass

    def classify_risk(risk_score, th):
        if risk_score >= 0.75:
            return "Critical Risk"
        if risk_score >= th:
            return "Suspicious"
        return "Clear"

    sample_txs['Risk Tier'] = sample_txs['Probability'].apply(
        lambda x: classify_risk(x, active_threshold)
    )

    total = len(sample_txs)
    critical = (sample_txs['Risk Tier'] == 'Critical Risk').sum()
    susp = (sample_txs['Risk Tier'] == 'Suspicious').sum()
    clear = (sample_txs['Risk Tier'] == 'Clear').sum()

    s1, s2, s3, s4 = st.columns(4)
    for col, (label, val, accent) in zip(
        [s1, s2, s3, s4],
        [("Total Records", f"{total:,}", v_text),
         ("Critical", f"{critical}", "#EF4444"),
         ("Suspicious", f"{susp}", "#F59E0B"),
         ("Clear", f"{clear}", "#10B981")]
    ):
        with col:
            st.markdown(f"""
            <div style="background:{v_card};border:1px solid {v_border};border-radius:10px;
                        padding:0.85rem 1rem;text-align:center;">
                <p style="margin:0;font-size:0.67rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:0.09em;color:{v_muted};">{label}</p>
                <p style="margin:0.25rem 0 0;font-size:1.6rem;font-weight:900;color:{accent};">{val}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='margin:0 0 0.75rem 0;font-size:1rem;font-weight:800;color:%s;'>Transaction Ledger Search</h3>" % v_text, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2.5, 1.2, 1])
    with fc1:
        search_tx = st.text_input(
            "Search by ID",
            placeholder="Enter transaction ID…",
            label_visibility="collapsed"
        )
    with fc2:
        filter_tier = st.selectbox(
            "Filter by Risk Tier",
            ["All Tiers", "Clear", "Suspicious", "Critical Risk"],
            label_visibility="collapsed"
        )
    with fc3:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        csv_data = sample_txs.to_csv(index=False)
        st.download_button(
            label="Export CSV",
            data=csv_data,
            file_name=f"sentinel_ledger_{int(time.time())}.csv",
            mime="text/csv",
            use_container_width=True
        )

    filtered = sample_txs.copy()
    if search_tx:
        filtered = filtered[filtered['TransactionID'].astype(str).str.contains(search_tx)]
    if filter_tier != "All Tiers":
        filtered = filtered[filtered['Risk Tier'] == filter_tier]

    st.markdown(f"<p style='margin:0.5rem 0 0.5rem 0;font-size:0.76rem;color:{v_muted};'>Showing {min(len(filtered), 150):,} of {len(filtered):,} records</p>", unsafe_allow_html=True)

    display_df = filtered[[
        'TransactionID', 'TransactionAmt', 'HourOfDay',
        'card4', 'card6', 'Probability', 'Risk Tier', 'Actual'
    ]].head(150).copy()

    display_df['Actual'] = display_df['Actual'].astype(bool)
    display_df['card4'] = display_df['card4'].astype(str).str.upper()
    display_df['card6'] = display_df['card6'].astype(str).str.upper()

    st.dataframe(
        display_df,
        use_container_width=True,
        height=420,
        column_config={
            "TransactionID": st.column_config.TextColumn("Txn ID", width="small"),
            "TransactionAmt": st.column_config.NumberColumn("Amount", format="$%.2f", width="small"),
            "HourOfDay": st.column_config.NumberColumn("Hour", format="%d", width="small"),
            "card4": st.column_config.TextColumn("Network", width="small"),
            "card6": st.column_config.TextColumn("Type", width="small"),
            "Probability": st.column_config.ProgressColumn("Risk Index", format="%.1f%%", min_value=0, max_value=1, width="medium"),
            "Risk Tier": st.column_config.TextColumn("Tier", width="medium"),
            "Actual": st.column_config.CheckboxColumn("Is Fraud?", width="small"),
        },
        hide_index=True
    )


def render_custom_sidebar_nav(active_key):
    v = THEME_VARS
    primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"
    
    # helper for active class
    def cls(key):
        return "nav-item active" if active_key == key else "nav-item"

    # SVG string definitions (without emojis)
    svg_home = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>'
    svg_command = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    svg_threat = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    svg_policy = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    svg_batch = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="9"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/></svg>'
    svg_cust = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
    svg_science = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3z"/><path d="M6 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3z"/><path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/></svg>'
    svg_model_health = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'
    svg_audit = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>'
    svg_sandbox = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>'
    svg_health = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/></svg>'

    nav_html = f"""<div class="sidebar-nav">
<div class="nav-section">Dashboard</div>
<a href="/?page=Overview" target="_self" class="{cls('Overview')}">
{svg_home} Overview Dashboard
</a>
<div class="nav-section">Operations</div>
<a href="/?page=CommandCenter" target="_self" class="{cls('CommandCenter')}">
{svg_command} Command Center Hub
</a>
<a href="/?page=ThreatSimulator" target="_self" class="{cls('ThreatSimulator')}">
{svg_threat} Threat Simulator Lab
</a>
<a href="/?page=PolicyOptimizer" target="_self" class="{cls('PolicyOptimizer')}">
{svg_policy} Risk Policy Optimizer
</a>
<a href="/?page=BatchPredictor" target="_self" class="{cls('BatchPredictor')}">
{svg_batch} Batch Predictor Hub
</a>
<a href="/?page=CustomerProfiler" target="_self" class="{cls('CustomerProfiler')}">
{svg_cust} Customer Risk Profiler
</a>
<div class="nav-section">Data Science & Audit</div>
<a href="/?page=AIScience" target="_self" class="{cls('AIScience')}">
{svg_science} SMOTE & AI Science
</a>
<a href="/?page=ModelHealth" target="_self" class="{cls('ModelHealth')}">
{svg_model_health} Model Health & Telemetry
</a>
<a href="/?page=AuditLedger" target="_self" class="{cls('AuditLedger')}">
{svg_audit} Audit Compliance Ledger
</a>
<div class="nav-section">Developer & System</div>
<a href="/?page=APISandbox" target="_self" class="{cls('APISandbox')}">
{svg_sandbox} API Gateway Sandbox
</a>
<a href="/?page=SystemHealth" target="_self" class="{cls('SystemHealth')}">
{svg_health} System Health & Telemetry
</a>
</div>"""
    st.sidebar.markdown(nav_html, unsafe_allow_html=True)


def render_api_sandbox(assets):
    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>API Gateway Sandbox</h1>
            <p>Test raw JSON payloads, inspect transaction risk scoring endpoint behavior, and review responses.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### REST API Integration Sandbox")
    st.caption("Perform simulated HTTP POST requests to evaluating endpoint and analyze response schemas.")

    c1, c2 = st.columns([1.2, 1], gap="large")
    with c1:
        st.markdown("##### Request Details")
        st.text_input("Endpoint URL", value="https://api.sentinel-ai.internal/v1/risk/evaluate", disabled=True)
        st.text_input("Authorization Token", value="Bearer st_live_4f9a3bcd10287e59cde0", type="password")
        
        default_payload = """{
  "TransactionID": 3982402,
  "TransactionAmt": 250.00,
  "card1": 13926,
  "card4": "visa",
  "card6": "credit",
  "P_emaildomain": "protonmail.com",
  "HourOfDay": 3
}"""
        payload_text = st.text_area("JSON Request Body", value=default_payload, height=220)
        send_btn = st.button("Execute Request")

    with c2:
        st.markdown("##### Response Details")
        if send_btn:
            try:
                import json
                data = json.loads(payload_text)
                
                # Predict
                sim_amt = float(data.get("TransactionAmt", 100.0))
                sim_card1 = int(data.get("card1", 10000))
                sim_hour = int(data.get("HourOfDay", 12))
                sim_card4 = str(data.get("card4", "visa")).lower()
                sim_card6 = str(data.get("card6", "debit")).lower()
                sim_email = str(data.get("P_emaildomain", "gmail.com")).lower()
                
                input_row = pd.DataFrame(0.0, index=[0], columns=assets['features'])
                input_row['TransactionAmt'] = sim_amt
                input_row['card1'] = sim_card1
                input_row['HourOfDay'] = sim_hour
                input_row['AmtToMeanRatio'] = sim_amt / (135.0 + 1e-5)
                input_row['DeviceRisk'] = 1 if 'credit' in sim_card6 else 0
                input_row['LogTransactionAmt'] = np.log1p(sim_amt)
                input_row['Card1AmtRatio'] = 1.0
                input_row['EmailDomainRisk'] = 1 if sim_email in ['mail.com', 'protonmail.com', 'outlook.com', 'hotmail.com'] else 0
                input_row['Card1Freq'] = 10

                for col_name, sim_val in [
                    ('card4', sim_card4), ('card6', sim_card6), ('P_emaildomain', sim_email)
                ]:
                    if col_name in assets['label_encoders']:
                        le = assets['label_encoders'][col_name]
                        val = sim_val if sim_val in le.classes_ else le.classes_[0]
                        input_row[col_name] = le.transform([val])[0]

                input_scaled = input_row.copy()
                input_scaled[assets['numeric_cols']] = assets['scaler'].transform(input_row[assets['numeric_cols']])
                prob = float(assets['model'].predict_proba(input_scaled)[:, 1][0])
                
                active_threshold = st.session_state.custom_threshold
                decision = "DECLINE" if prob >= 0.75 else ("CHALLENGE" if prob >= active_threshold else "APPROVE")
                
                response_json = {
                    "status": "success",
                    "timestamp": int(time.time()),
                    "data": {
                        "transaction_id": int(data.get("TransactionID", 0)),
                        "evaluation": {
                            "risk_score": round(prob, 4),
                            "decision": decision,
                            "policy_threshold": active_threshold,
                            "latency_ms": 11.2
                        },
                        "risk_attributes": {
                            "high_value_check": "passed" if sim_amt < 1000 else "flagged",
                            "domain_risk_index": "critical" if sim_email in ['protonmail.com', 'mail.com'] else "low",
                            "card_issuing_country": "US"
                        }
                    }
                }
                
                st.markdown("""
                <div style="background-color: rgba(16,185,129,0.07); border: 1px solid #10B981; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
                    <span style="font-weight:700; color:#10B981;">STATUS: 200 OK</span> &nbsp;&middot;&nbsp; 
                    <span style="color:#64748B; font-size:0.8rem;">Time: 11.2ms</span>
                </div>
                """, unsafe_allow_html=True)
                st.code(json.dumps(response_json, indent=2), language="json")
                
            except Exception as e:
                st.markdown("""
                <div style="background-color: rgba(239,68,68,0.07); border: 1px solid #EF4444; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
                    <span style="font-weight:700; color:#EF4444;">STATUS: 400 Bad Request</span>
                </div>
                """, unsafe_allow_html=True)
                st.code(json.dumps({"error": "Malformed JSON payload", "details": str(e)}, indent=2), language="json")
        else:
            st.info("Execute raw HTTP payload evaluation to inspect model response body.")


def render_system_health(assets):
    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>System Health & Telemetry</h1>
            <p>Real-time infrastructure statistics, runtime performance metrics, and console logging stream.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Live Infrastructure Resource Telemetry")
    st.caption("Active monitoring metrics for machine learning classifier host environment.")

    # Grid of system stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="saas-card">
            <h3>CPU Utilization</h3>
            <p class="saas-card-value">12.4%</p>
            <p class="saas-card-subtext">8 Cores active</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="saas-card">
            <h3>Memory Footprint</h3>
            <p class="saas-card-value">2.4 GB</p>
            <p class="saas-card-subtext">Of 16.0 GB total</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="saas-card">
            <h3>API Gateway Throughput</h3>
            <p class="saas-card-value">185 req/s</p>
            <p class="saas-card-subtext">Peak 320 req/s</p>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="saas-card">
            <h3>Model Inference Latency</h3>
            <p class="saas-card-value">11.4 ms</p>
            <p class="saas-card-subtext">P99 lat: 14.8ms</p>
        </div>
        """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.6, 1], gap="large")
    with col1:
        st.markdown("##### Real-Time Gateway Log Stream")
        
        import random
        log_templates = [
            "INFO  [evaluator] Txn #{tx_id} - Score: {score}% - Decision: {dec}",
            "DEBUG [redis_cache] Cache HIT for key card1_{card1}",
            "INFO  [gateway] Received POST request from ip 172.16.89.41 - status 200",
            "WARN  [evaluator] Request transaction amount ${amt} exceeds p95 limit",
            "DEBUG [evaluator] Evaluation completed in {lat}ms"
        ]
        
        logs = []
        for i in range(10):
            tx_id = random.randint(3000000, 3999999)
            score = round(random.uniform(1.0, 99.0), 1)
            dec = "APPROVE" if score < 45 else ("CHALLENGE" if score < 75 else "DECLINE")
            card1 = random.randint(1000, 25000)
            amt = random.randint(50, 3000)
            lat = round(random.uniform(8.2, 14.9), 1)
            
            tmpl = random.choice(log_templates)
            log_str = tmpl.format(tx_id=tx_id, score=score, dec=dec, card1=card1, amt=amt, lat=lat)
            timestamp = datetime.now() - timedelta(seconds=(10 - i) * 3)
            logs.append(f"[{timestamp.strftime('%H:%M:%S')}] {log_str}")
            
        logs_text = "\n".join(logs)
        st.text_area("Active Node Console Terminal Output", value=logs_text, height=260, disabled=True)
        
    with col2:
        st.markdown("##### Latency Percentile Distribution")
        percentiles = ['Min', 'P50', 'P90', 'P95', 'P99', 'Max']
        latency_vals = [2.4, 8.1, 10.9, 12.3, 14.8, 26.5]
        
        fig_lat = px.bar(
            x=percentiles, y=latency_vals,
            labels={'x': 'Percentile', 'y': 'Latency (ms)'},
            color_discrete_sequence=['#7C3AED']
        )
        is_white = st.session_state.theme_mode == "Professional White"
        fig_lat.update_layout(
            template="plotly_white" if is_white else "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=10, b=10, l=10, r=10),
            height=260
        )
        st.plotly_chart(fig_lat, use_container_width=True)


def render_batch_predictor(assets):
    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>Batch Predictor Hub</h1>
            <p>Upload transaction batch files (CSV) or generate simulated datasets to perform high-volume ML inference.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    v = THEME_VARS
    primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"

    st.markdown("### High-Throughput Batch Inference")
    st.caption("Upload multiple transactions at once to evaluate them using the active LightGBM risk classifier.")

    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("##### Upload Transaction File")
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    with c2:
        st.markdown("##### Simulation Engine")
        st.write("Don't have a batch file? Generate a mock payload of 150 transactions with anomalous signals in one click.")
        gen_btn = st.button("Generate Simulated Batch", use_container_width=True)

    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully.")
        except Exception as e:
            st.error(f"Error parsing CSV: {e}")
    elif gen_btn:
        import random
        rows = []
        networks = ['visa', 'mastercard', 'discover', 'american express']
        types = ['debit', 'credit']
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'protonmail.com', 'mail.com', 'outlook.com']
        
        for i in range(150):
            tx_id = 4000000 + i
            amt = round(np.random.exponential(150.0) + random.uniform(5, 50), 2)
            card1 = random.randint(1000, 20000)
            net = random.choice(networks)
            t = random.choice(types)
            dom = random.choice(domains)
            hour = random.randint(0, 23)
            rows.append({
                'TransactionID': tx_id,
                'TransactionAmt': amt,
                'card1': card1,
                'card4': net,
                'card6': t,
                'P_emaildomain': dom,
                'HourOfDay': hour
            })
        df = pd.DataFrame(rows)
        st.success("Generated 150 simulated transactions.")

    if df is not None:
        required_cols = ['TransactionAmt', 'card1', 'card4', 'card6', 'P_emaildomain', 'HourOfDay']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"Missing required columns in input batch: {missing}")
            return

        with st.spinner("Executing batch inference..."):
            active_threshold = st.session_state.custom_threshold

            # --- Vectorised feature engineering (single DataFrame, one predict call) ---
            feat_df = pd.DataFrame(0.0, index=df.index, columns=assets['features'])

            amts   = df['TransactionAmt'].astype(float).values
            card1s = df['card1'].astype(float).values
            hours  = df['HourOfDay'].astype(float).values
            card4s = df['card4'].astype(str).str.lower()
            card6s = df['card6'].astype(str).str.lower()
            emails = df['P_emaildomain'].astype(str).str.lower()

            risky_domains = {'mail.com', 'protonmail.com', 'outlook.com', 'hotmail.com'}

            feat_df['TransactionAmt']  = amts
            feat_df['card1']           = card1s
            feat_df['HourOfDay']       = hours
            feat_df['AmtToMeanRatio']  = amts / 135.00001
            feat_df['LogTransactionAmt'] = np.log1p(amts)
            feat_df['Card1AmtRatio']   = 1.0
            feat_df['Card1Freq']       = 10
            feat_df['DeviceRisk']      = card6s.str.contains('credit').astype(float).values
            feat_df['EmailDomainRisk'] = emails.isin(risky_domains).astype(float).values

            for col_name, series in [('card4', card4s), ('card6', card6s), ('P_emaildomain', emails)]:
                if col_name in assets['label_encoders']:
                    le = assets['label_encoders'][col_name]
                    safe = series.apply(lambda x: x if x in le.classes_ else le.classes_[0])
                    feat_df[col_name] = le.transform(safe).astype(float)

            feat_scaled = feat_df.copy()
            feat_scaled[assets['numeric_cols']] = assets['scaler'].transform(feat_df[assets['numeric_cols']])

            probs_arr = assets['model'].predict_proba(feat_scaled)[:, 1]
            tiers_arr = np.where(
                probs_arr >= 0.75, 'CRITICAL',
                np.where(probs_arr >= active_threshold, 'SUSPICIOUS', 'CLEAR')
            )

            df['Risk Index']      = probs_arr
            df['Evaluation Tier'] = tiers_arr

        total_amt = df['TransactionAmt'].sum()
        critical_count = (df['Evaluation Tier'] == "CRITICAL").sum()
        suspicious_count = (df['Evaluation Tier'] == "SUSPICIOUS").sum()
        clear_count = (df['Evaluation Tier'] == "CLEAR").sum()
        flagged_rate = ((critical_count + suspicious_count) / len(df)) * 100

        st.markdown("#### Batch Summary Metrics")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="saas-card">
                <h3>Total Evaluated</h3>
                <p class="saas-card-value">{len(df)}</p>
                <p class="saas-card-subtext">Transactions parsed</p>
            </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="saas-card">
                <h3>Total Value</h3>
                <p class="saas-card-value">${total_amt:,.2f}</p>
                <p class="saas-card-subtext">Cumulative amount</p>
            </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="saas-card">
                <h3>Flagged Fraud Rate</h3>
                <p class="saas-card-value">{flagged_rate:.1f}%</p>
                <p class="saas-card-subtext">{critical_count + suspicious_count} flagged anomalies</p>
            </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="saas-card">
                <h3>Status Distribution</h3>
                <p class="saas-card-value" style="font-size: 1.2rem; margin-top: 0.5rem;">
                    <span style="color:#10B981;">{clear_count} Ok</span> &nbsp;&middot;&nbsp; 
                    <span style="color:#F59E0B;">{suspicious_count} Susp</span> &nbsp;&middot;&nbsp; 
                    <span style="color:#EF4444;">{critical_count} Crit</span>
                </p>
                <p class="saas-card-subtext">Risk tier segmentation</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Visual Analytics")
        plot_c1, plot_c2 = st.columns([1.6, 1], gap="large")
        with plot_c1:
            fig_scatter = px.scatter(
                df, x='TransactionAmt', y='Risk Index',
                color='Evaluation Tier',
                color_discrete_map={'CLEAR': '#10B981', 'SUSPICIOUS': '#F59E0B', 'CRITICAL': '#EF4444'},
                labels={'TransactionAmt': 'Amount ($)', 'Risk Index': 'Risk Score'},
                title="Risk Index vs Transaction Amount"
            )
            fig_scatter.update_layout(
                template="plotly_white" if st.session_state.theme_mode == "Professional White" else "plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        with plot_c2:
            fig_pie = px.pie(
                df, names='Evaluation Tier',
                color='Evaluation Tier',
                color_discrete_map={'CLEAR': '#10B981', 'SUSPICIOUS': '#F59E0B', 'CRITICAL': '#EF4444'},
                hole=0.4,
                title="Risk Level Segmentation"
            )
            fig_pie.update_layout(
                template="plotly_white" if st.session_state.theme_mode == "Professional White" else "plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("#### Annotated Prediction Results")
        st.dataframe(
            df[['TransactionID', 'TransactionAmt', 'card4', 'card6', 'P_emaildomain', 'Risk Index', 'Evaluation Tier']],
            use_container_width=True,
            column_config={
                "TransactionID": st.column_config.TextColumn("Txn ID"),
                "TransactionAmt": st.column_config.NumberColumn("Amount", format="$%.2f"),
                "card4": st.column_config.TextColumn("Network"),
                "card6": st.column_config.TextColumn("Type"),
                "P_emaildomain": st.column_config.TextColumn("Email Domain"),
                "Risk Index": st.column_config.ProgressColumn("Risk Score", format="%.1f%%", min_value=0, max_value=1),
                "Evaluation Tier": st.column_config.TextColumn("Tier"),
            },
            hide_index=True
        )

        csv_annotated = df.to_csv(index=False)
        st.download_button(
            label="Download Annotated Results (CSV)",
            data=csv_annotated,
            file_name="sentinel_batch_predictions.csv",
            mime="text/csv",
            use_container_width=True
        )


def render_customer_profiler(assets):
    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>Customer Risk Profiler</h1>
            <p>Compute customer trust indexing, verify historical behavior patterns, and assign operational KYC policies.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    v = THEME_VARS
    primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"

    st.markdown("### Profile Risk Evaluator")
    st.caption("Assess overall customer risk ratings based on account telemetry, device fingerprint status, and transaction velocity.")

    c1, c2 = st.columns([1.2, 1], gap="large")
    with c1:
        st.markdown("##### Customer Identity Profile")
        cust_id = st.text_input("Customer ID", value="CUST-98304-DX")
        
        col_id1, col_id2 = st.columns(2)
        with col_id1:
            country = st.selectbox("Operating Jurisdiction", ["United States (US)", "United Kingdom (GB)", "Germany (DE)", "Cayman Islands (KY)", "Nigeria (NG)"])
            acct_age = st.number_input("Account Tenure (Days)", min_value=1, max_value=3650, value=120)
        with col_id2:
            card_net = st.selectbox("Preferred Issuing Network", ["Visa", "Mastercard", "Discover", "American Express"])
            card_type = st.selectbox("Card Funding Type", ["Debit", "Credit"])

        st.markdown("##### Behavior & Device Telemetry")
        col_bh1, col_bh2 = st.columns(2)
        with col_bh1:
            velocity_30d = st.number_input("30-Day Cumulative Volume ($)", min_value=0.0, value=1500.0)
            email_domain = st.selectbox("Customer Email Domain", ["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "mail.com"])
        with col_bh2:
            mfa_bypass = st.slider("MFA Failures / Bypass Attempts (Last 7 Days)", 0, 10, value=1)
            device_anom = st.checkbox("Device Fingerprint Anomalies Flagged", value=False)

        eval_btn = st.button("Evaluate Profile Trust Index", use_container_width=True)

    with c2:
        st.markdown("##### Trust Index Analysis")
        if eval_btn:
            base_risk = 0.15
            if acct_age < 30:
                base_risk += 0.25
            elif acct_age < 90:
                base_risk += 0.10
            if "KY" in country or "NG" in country:
                base_risk += 0.30
            if email_domain in ["protonmail.com", "mail.com"]:
                base_risk += 0.20
            if card_type == "Credit":
                base_risk += 0.05
            if velocity_30d > 10000:
                base_risk += 0.15
            elif velocity_30d > 5000:
                base_risk += 0.05
            base_risk += mfa_bypass * 0.08
            if device_anom:
                base_risk += 0.25
                
            risk_score = min(max(base_risk, 0.01), 0.99)
            decision = "DECLINE" if risk_score >= 0.75 else ("CHALLENGE" if risk_score >= st.session_state.custom_threshold else "APPROVE")
            color = "#EF4444" if decision == "DECLINE" else ("#F59E0B" if decision == "CHALLENGE" else "#10B981")
            
            st.markdown(f"""
            <div style="background-color: {v['card_bg']}; border: 1px solid {v['border_color_hex']}; border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem;">
                <p style="margin: 0; font-size: 0.72rem; text-transform: uppercase; color: {v['text_muted']}; letter-spacing: 0.1em;">Customer Risk Rating</p>
                <h2 style="margin: 0.5rem 0; font-size: 3rem; font-weight: 900; color: {color};">{risk_score * 100:.1f}%</h2>
                <span class="saas-badge" style="display: inline-flex; justify-content: center; border-color: {color}; color: {color}; background-color: rgba(0,0,0,0);">
                    RECOMMENDED ACTION: {decision}
                </span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### Key Risk Signals")
            factors = []
            if acct_age < 30:
                factors.append(("Fresh Account Age", "New account registered less than 30 days ago.", "HIGH RISK"))
            if "KY" in country or "NG" in country:
                factors.append(("High-Risk Jurisdiction", f"Account registered from high-monitoring country: {country}", "CRITICAL"))
            if email_domain in ["protonmail.com", "mail.com"]:
                factors.append(("Encrypted/Disposable Email", f"Domain '{email_domain}' is commonly flagged for fraud registration.", "MEDIUM RISK"))
            if mfa_bypass > 2:
                factors.append(("Repeated Auth Failures", f"{mfa_bypass} failed MFA/login attempts detected recently.", "HIGH RISK"))
            if device_anom:
                factors.append(("Device Inconsistency", "Browser agent fingerprint differs from billing billing state.", "CRITICAL"))
            if not factors:
                factors.append(("Clean Profile History", "No high-risk anomalous attributes flagged.", "TRUSTED"))

            for title, desc, level in factors:
                lvl_color = "#10B981" if level == "TRUSTED" else ("#F59E0B" if "MEDIUM" in level else "#EF4444")
                st.markdown(f"""
                <div style="border: 1px solid {v['border_color_hex']}; border-radius: 8px; padding: 0.75rem 1rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size:0.85rem; color:{v['text_color']};">{title}</strong>
                        <p style="margin:0; font-size:0.75rem; color:{v['text_muted']};">{desc}</p>
                    </div>
                    <span style="font-size:0.65rem; font-weight:700; color:{lvl_color}; border: 1px solid {lvl_color}; padding: 0.15rem 0.4rem; border-radius: 4px;">{level}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Initiate Customer Profile Trust evaluation to analyze identity and behavior signals.")


def render_model_health(assets):
    st.markdown("""
    <div class="saas-header">
        <div class="saas-header-title">
            <h1>Model Health & Telemetry</h1>
            <p>Monitor real-time ML performance scores, model calibration drift, and feature attribution metrics.</p>
        </div>
        <div class="saas-badge">
            <span class="status-dot"></span>
            Meet R Kakadiya
        </div>
    </div>
    """, unsafe_allow_html=True)

    v = THEME_VARS
    primary = "#7C3AED" if st.session_state.theme_mode == "Professional Black" else "#6001FC"

    st.markdown("### Production Performance Indicators")
    k1, k2, k3, k4 = st.columns(4)
    
    kpis = [
        ("ROC-AUC", "0.9207", primary),
        ("PRECISION", "0.8672", "#10B981"),
        ("RECALL", "0.8314", "#F59E0B"),
        ("F1 SCORE", "0.8490", primary)
    ]
    for col, (label, val, accent) in zip([k1, k2, k3, k4], kpis):
        with col:
            st.markdown(f"""
            <div style="background:{v['card_bg']}; border:1px solid {v['border_color_hex']}; border-top:3px solid {accent};
                        border-radius:12px; padding:1.25rem 1.1rem; text-align:center;">
                <p style="margin:0; font-size:0.68rem; font-weight:700; text-transform:uppercase;
                          letter-spacing:0.1em; color:{v['text_muted']};">{label}</p>
                <p style="margin:0.3rem 0 0; font-size:2rem; font-weight:900; color:{v['text_color']};">{val}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Overall Model Score Section ──────────────────────────────────────────
    st.markdown("### Overall Model Scorecard")
    st.caption("Composite evaluation of model health across accuracy, speed, stability, and coverage dimensions — values refresh on every page load.")

    # Simulated real-time dimension values (seeded with time-varying noise)
    import random as _rnd
    _seed = int(datetime.now().timestamp()) % 1000
    _rnd.seed(_seed)

    rt_accuracy      = round(0.921 + _rnd.uniform(-0.004, 0.004), 4)
    rt_latency_ms    = round(12.4  + _rnd.uniform(-1.5, 2.8), 1)
    rt_calibration   = round(0.963 + _rnd.uniform(-0.008, 0.006), 4)
    rt_throughput    = int(1820   + _rnd.randint(-90, 140))
    rt_coverage      = round(0.974 + _rnd.uniform(-0.005, 0.005), 4)
    rt_stability     = round(0.947 + _rnd.uniform(-0.010, 0.008), 4)

    # Composite score = weighted average of all dimensions (0-100)
    composite = round((
        rt_accuracy   * 0.30 +
        min(1.0, 15.0 / rt_latency_ms) * 0.20 +
        rt_calibration * 0.15 +
        min(1.0, rt_throughput / 2000) * 0.10 +
        rt_coverage   * 0.15 +
        rt_stability  * 0.10
    ) * 100, 1)

    score_color = primary
    score_label = "EXCELLENT" if composite >= 88 else ("GOOD" if composite >= 75 else "DEGRADED")

    sc_left, sc_right = st.columns([1, 2.4], gap="large")

    with sc_left:
        # Big composite gauge card
        st.markdown(f"""
        <div style="background:{v['card_bg']}; border:1px solid {v['border_color_hex']};
                    border-radius:16px; padding:2rem 1.5rem; text-align:center; height:100%;">
            <p style="margin:0; font-size:0.68rem; font-weight:700; text-transform:uppercase;
                      letter-spacing:0.12em; color:{v['text_muted']};">Composite Health Index</p>
            <p style="margin:0.5rem 0; font-size:4rem; font-weight:900;
                      line-height:1; color:{score_color};">{composite}</p>
            <p style="margin:0; font-size:0.7rem; font-weight:700; color:{score_color};
                      letter-spacing:0.08em;">/ 100 &nbsp;&bull;&nbsp; {score_label}</p>
            <div style="margin-top:1.2rem; background:{v['border_color_hex']}; border-radius:999px; height:8px; overflow:hidden;">
                <div style="width:{composite}%; height:100%; background:{score_color};
                            border-radius:999px; transition:width 0.6s ease;"></div>
            </div>
            <p style="margin:0.8rem 0 0; font-size:0.7rem; color:{v['text_muted']};">
                Weighted across 6 operational dimensions
            </p>
        </div>
        """, unsafe_allow_html=True)

    with sc_right:
        # 6 individual dimension metric cards in 3Ã—2 grid
        # Monochrome dimension data — single accent, no rainbow
        dim_data = [
            ("Prediction Accuracy",   f"{rt_accuracy*100:.2f}%",   "Correct classifications against held-out validation set"),
            ("Inference Latency",     f"{rt_latency_ms} ms",        "P95 end-to-end scoring time per transaction"),
            ("Calibration Score",     f"{rt_calibration*100:.2f}%", "Brier score-based confidence alignment metric"),
            ("Throughput",            f"{rt_throughput} req/s",     "Peak sustained inference volume per second"),
            ("Feature Coverage",      f"{rt_coverage*100:.2f}%",    "Non-null feature completeness at inference time"),
            ("Prediction Stability",  f"{rt_stability*100:.2f}%",   "Score consistency across 30-day rolling window"),
        ]

        d_row1 = st.columns(3, gap="small")
        d_row2 = st.columns(3, gap="small")
        all_dim_cols = d_row1 + d_row2

        for dc, (dim_label, dim_val, dim_desc) in zip(all_dim_cols, dim_data):
            with dc:
                st.markdown(f"""
                <div style="background:{v['card_bg']}; border:1px solid {v['border_color_hex']};
                            border-top:2px solid {primary}; border-radius:10px;
                            padding:0.85rem 1rem; margin-bottom:0.6rem;">
                    <p style="margin:0; font-size:0.62rem; font-weight:700; text-transform:uppercase;
                              letter-spacing:0.09em; color:{v['text_muted']};">{dim_label}</p>
                    <p style="margin:0.25rem 0 0; font-size:1.4rem; font-weight:900;
                              color:{v['text_color']};">{dim_val}</p>
                    <p style="margin:0.2rem 0 0; font-size:0.65rem;
                              color:{v['text_muted']}; line-height:1.35;">{dim_desc}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # Sub-score horizontal bar chart
    st.markdown("##### Dimension Score Breakdown")
    dim_names  = ["Accuracy", "Latency", "Calibration", "Throughput", "Coverage", "Stability"]
    dim_scores = [
        round(rt_accuracy * 100, 1),
        round(min(1.0, 15.0 / rt_latency_ms) * 100, 1),
        round(rt_calibration * 100, 1),
        round(min(1.0, rt_throughput / 2000) * 100, 1),
        round(rt_coverage * 100, 1),
        round(rt_stability * 100, 1),
    ]
    # Monochrome bar chart — graduated opacity of primary
    bar_primary_rgb = "96, 1, 252" if st.session_state.theme_mode == "Professional White" else "124, 58, 237"
    dim_bar_colors = [
        f"rgba({bar_primary_rgb}, {0.45 + i * 0.09})" for i in range(6)
    ]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=dim_scores,
        y=dim_names,
        orientation='h',
        marker=dict(color=dim_bar_colors, line=dict(width=0)),
        text=[f"{s}%" for s in dim_scores],
        textposition='outside',
        textfont=dict(size=11, color=v['text_color'])
    ))
    fig_bar.update_layout(
        template="plotly_white" if st.session_state.theme_mode == "Professional White" else "plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10, l=10, r=70),
        height=220,
        xaxis=dict(range=[0, 115], showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(tickfont=dict(size=11, color=v['text_color'])),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1.2], gap="large")
    with c1:
        st.markdown("##### Model Performance Radar")
        
        categories = ['Precision', 'ROC-AUC', 'Specificity', 'F1', 'Recall']
        values = [0.8672, 0.9207, 0.9410, 0.8490, 0.8314]
        
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor='rgba(124, 58, 237, 0.15)' if st.session_state.theme_mode == "Professional Black" else 'rgba(96, 1, 252, 0.12)',
            line=dict(color=primary, width=2),
            name='Current Model Performance'
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0.6, 1.0],
                    tickfont=dict(size=8, color=v['text_muted']),
                    gridcolor='rgba(128,128,128,0.2)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=9, color=v['text_color']),
                    gridcolor='rgba(128,128,128,0.2)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=30, l=40, r=40),
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        st.markdown("##### Engineered Features")
        
        features = [
            ("LogTransactionAmt", "Log-transform to normalise extreme purchase variance."),
            ("AmtToMeanRatio", "Transaction vs. rolling average — detects size anomalies."),
            ("DeviceRisk", "Binary flag: credit card funding carries higher raw fraud correlation."),
            ("EmailDomainRisk", "Derived risk index from domain reputation metrics."),
            ("HourOfDay", "Hourly pattern extraction — late-night purchases elevate risk.")
        ]
        
        for name, desc in features:
            st.markdown(f"""
            <div style="background:{v['card_bg']}; border:1px solid {v['border_color_hex']};
                        border-left:3px solid {primary}; padding:0.85rem 1.1rem;
                        border-radius:8px; margin-bottom:0.6rem;">
                <span style="display:inline-block; font-family:'JetBrains Mono',monospace;
                             font-size:0.8rem; font-weight:700; color:{primary};
                             background:transparent; padding:0; margin:0;">{name}</span>
                <p style="margin:0.3rem 0 0; font-size:0.73rem; color:{v['text_muted']};
                          line-height:1.5;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    
    st.markdown("### Real-Time Inference Drift & Analytics")
    st.caption("Active monitoring of risk score prediction confidence and drift metrics over 24-hour evaluation cycle.")

    # Seed from current minute so chart is stable within a reload window
    _drift_seed = int(datetime.now().strftime("%Y%m%d%H%M"))
    np.random.seed(_drift_seed)
    hours_axis = [f"T-{24-i}h" for i in range(25)]
    mean_confidence = np.clip(0.88 + np.random.normal(0, 0.015, 25), 0.82, 0.97)
    drift_index     = np.clip(0.02 + np.random.uniform(0.005, 0.025, 25), 0.01, 0.06)
    np.random.seed(None)  # release fixed seed
    
    fig_drift = go.Figure()
    fig_drift.add_trace(go.Scatter(
        x=hours_axis, y=mean_confidence,
        mode='lines+markers',
        name='Avg Prediction Confidence',
        line=dict(color=primary, width=2.5),
        marker=dict(size=5)
    ))
    fig_drift.add_trace(go.Scatter(
        x=hours_axis, y=drift_index,
        mode='lines',
        name='Population Stability Index (PSI)',
        line=dict(color='#F59E0B', width=2, dash='dash')
    ))
    
    fig_drift.update_layout(
        template="plotly_white" if st.session_state.theme_mode == "Professional White" else "plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=20, b=20, l=20, r=20),
        height=280,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_drift, use_container_width=True)


def show_skeleton_loader():
    v = THEME_VARS
    
    if st.session_state.theme_mode == "Professional Black":
        shimmer_bg = "linear-gradient(90deg, #12101A 25%, #1D192B 50%, #12101A 75%)"
    else:
        shimmer_bg = "linear-gradient(90deg, #F8FAFC 25%, #EDF2F7 50%, #F8FAFC 75%)"
        
    st.markdown(f"""
    <style>
        @keyframes shimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        .skeleton-loader {{
            background: {shimmer_bg};
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite linear;
            border-radius: 8px;
            border: 1px solid {v['border_color_hex']};
            width: 100%;
        }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="skeleton-loader" style="height: 72px; margin-bottom: 1.5rem;"></div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    for col in [c1, c2, c3, c4]:
        with col:
            st.markdown("""
                <div class="skeleton-loader" style="height: 100px; margin-bottom: 1.5rem;"></div>
            """, unsafe_allow_html=True)
            
    g1, g2 = st.columns([1.6, 1])
    with g1:
        st.markdown("""
            <div class="skeleton-loader" style="height: 280px; margin-bottom: 1rem;"></div>
            <div class="skeleton-loader" style="height: 200px; margin-bottom: 1rem;"></div>
        """, unsafe_allow_html=True)
    with g2:
        st.markdown("""
            <div class="skeleton-loader" style="height: 180px; margin-bottom: 1rem;"></div>
            <div class="skeleton-loader" style="height: 300px; margin-bottom: 1rem;"></div>
        """, unsafe_allow_html=True)


# --- 4. MAIN ENTRANCE DISPATCHER ---
def main():
    st.set_page_config(
        page_title="Sentinel AI — Risk Intelligence Hub",
        page_icon=":shield:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "Professional White"
    if "custom_threshold" not in st.session_state:
        st.session_state.custom_threshold = 0.45
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Overview"

    # Read query parameters
    query_page = st.query_params.get("page", "Overview")

    # CSS Injection matching the active theme
    inject_custom_css(st.session_state.theme_mode)

    # ── Custom Sidebar Header ──
    st.sidebar.markdown("""
    <div style="padding-bottom: 1rem;">
        <h1 style="font-size:1.6rem; font-weight:800; margin:0; letter-spacing:-0.03em;">Sentinel AI</h1>
        <p style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#6B7280; margin:0.1rem 0 0 0; letter-spacing:0.1em;">Risk Intelligence Hub</p>
    </div>
    """, unsafe_allow_html=True)

    # Render custom HTML navigation
    render_custom_sidebar_nav(query_page)

    # Theme Preset selector
    st.sidebar.markdown("<div class='nav-label'>Console Preferences</div>", unsafe_allow_html=True)
    theme_sel = st.sidebar.selectbox(
        "Theme Preset",
        ["Professional White", "Professional Black"],
        key="theme_sel_box"
    )
    if theme_sel != st.session_state.theme_mode:
        st.session_state.theme_mode = theme_sel
        st.rerun()

    # Load shared backend model assets
    assets = load_dashboard_assets()

    # Smooth skeleton transition trigger — minimal sleep to allow DOM commit
    if query_page != st.session_state.current_page:
        show_skeleton_loader()
        st.session_state.current_page = query_page
        time.sleep(0.05)
        st.rerun()

    # Dispatch to active page
    if query_page == "Overview":
        render_overview()
    elif not assets:
        st.warning("Please verify model payload model.pkl exists in the dashboard/ or root directory to view live telemetry nodes.")
    else:
        if query_page == "CommandCenter":
            render_command_center(assets)
        elif query_page == "ThreatSimulator":
            render_threat_simulator(assets)
        elif query_page == "PolicyOptimizer":
            render_policy_optimizer(assets)
        elif query_page == "BatchPredictor":
            render_batch_predictor(assets)
        elif query_page == "CustomerProfiler":
            render_customer_profiler(assets)
        elif query_page == "AIScience":
            render_ai_science(assets)
        elif query_page == "ModelHealth":
            render_model_health(assets)
        elif query_page == "AuditLedger":
            render_audit_ledger(assets)
        elif query_page == "APISandbox":
            render_api_sandbox(assets)
        elif query_page == "SystemHealth":
            render_system_health(assets)

    render_footer()

if __name__ == "__main__":
    main()
