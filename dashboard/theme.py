import streamlit as st
import os
import joblib

# Global CSS variables dictionary to store theme values dynamically
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

def inject_custom_css(theme_mode):  # noqa: PLR0915
    """Inject full custom CSS for the selected theme into the Streamlit app."""
    update_global_theme_variables(theme_mode)
    primary_color = "#6001FC" if theme_mode == "Professional White" else "#7C3AED"
    primary_hover = "#4F00D0" if theme_mode == "Professional White" else "#8B5CF6"
    
    # Extract variables for clean formatting
    v = THEME_VARS
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@300;400;500;600&display=swap');

        /* Global App Styling */
        .stApp {{
            background-color: {v['bg_app']} !important;
            color: {v['text_color']} !important;
            font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        }}

        /* Hide default Streamlit header bar, footer, and menu */
        [data-testid="stHeader"], header, footer, #MainMenu {{
            display: none !important;
            visibility: hidden !important;
            background: none !important;
            background-color: transparent !important;
        }}
        .stDeployButton {{
            display: none !important;
        }}

        /* ── Sidebar: Force Always Visible + Prevent Auto-Collapse ── */
        section[data-testid="stSidebar"] {{
            background-color: {v['bg_sidebar']} !important;
            border-right: 1px solid {v['sidebar_border']} !important;
            min-width: 240px !important;
            max-width: 300px !important;
            transition: transform 0.3s ease !important;
        }}
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {{
            color: {v['sidebar_text']} !important;
        }}

        /* ── Sidebar Collapse Toggle Button: Always Visible & Branded ── */
        [data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            background: {primary_color} !important;
            border: none !important;
            border-radius: 0 8px 8px 0 !important;
            width: 24px !important;
            height: 56px !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            color: #FFFFFF !important;
            box-shadow: 3px 0 12px {primary_color}44 !important;
            top: 50vh !important;
            transform: translateY(-50%) !important;
            z-index: 999 !important;
        }}
        [data-testid="collapsedControl"]:hover {{
            background: {primary_hover} !important;
            width: 28px !important;
        }}
        [data-testid="collapsedControl"] svg {{
            fill: #ffffff !important;
            color: #ffffff !important;
            width: 14px !important;
            height: 14px !important;
        }}

        /* ── Sidebar expand button (chevron that appears when collapsed) ── */
        button[data-testid="baseButton-header"] {{
            background: {primary_color}22 !important;
            border: 1px solid {primary_color}44 !important;
            border-radius: 6px !important;
            color: {primary_color} !important;
        }}

        /* ── Main content: don't let it bleed under sidebar ── */
        .main .block-container {{
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            max-width: 100% !important;
        }}


        /* Input & Widget Styling */
        div[data-baseweb="select"] > div {{
            background-color: {v['input_bg']} !important;
            color: {v['input_text']} !important;
            border-color: {v['border_color']} !important;
        }}
        input, select, textarea, div[role="radiogroup"] label {{
            color: {v['text_color']} !important;
        }}

        /* ── Number Input: force white bg, correct text, purple focus ── */
        div[data-testid="stNumberInput"] div[data-baseweb="input"] {{
            background-color: {v['input_bg']} !important;
            border-color: {v['border_color_hex']} !important;
            border-radius: 6px !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"]:focus-within {{
            border-color: {primary_color} !important;
            box-shadow: 0 0 0 2px {primary_color}22 !important;
        }}
        div[data-testid="stNumberInput"] div[data-baseweb="input"] > div {{
            background-color: {v['input_bg']} !important;
        }}
        div[data-testid="stNumberInput"] input {{
            background-color: {v['input_bg']} !important;
            color: {v['input_text']} !important;
            caret-color: {primary_color} !important;
        }}
        /* Stepper +/- buttons */
        div[data-testid="stNumberInput"] button {{
            background-color: {v['input_bg']} !important;
            color: {v['input_text']} !important;
            border-color: {v['border_color_hex']} !important;
        }}
        div[data-testid="stNumberInput"] button:hover {{
            background-color: {v['badge_bg']} !important;
            color: {primary_color} !important;
        }}
        /* "Press Enter to apply" tooltip text */
        div[data-testid="stNumberInput"] small,
        div[data-testid="stNumberInput"] [data-testid="InputInstructions"] {{
            color: {v['text_muted']} !important;
        }}

        /* ── Slider: replace red track & thumb with primary purple ── */
        div[data-testid="stSlider"] div[role="slider"] {{
            background-color: {primary_color} !important;
            border-color: {primary_color} !important;
            box-shadow: 0 0 0 4px {primary_color}22 !important;
        }}
        div[data-testid="stSlider"] [data-testid="stSliderTrackFill"],
        div[data-testid="stSlider"] div[style*="background"] {{
            background-color: {primary_color} !important;
        }}
        /* Slider thumb inner dot */
        div[data-testid="stSlider"] div[role="slider"]:before {{
            background: {primary_color} !important;
        }}
        /* Slider value label */
        div[data-testid="stSlider"] p {{
            color: {primary_color} !important;
            font-weight: 700 !important;
        }}

        /* ── Hide native Streamlit multi-page nav completely ── */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}

        /* ── Custom Premium Sidebar Nav ── */
        .snav-brand {{
            padding: 1.4rem 1rem 1rem 1rem;
            border-bottom: 1px solid {v['border_color_hex']};
            margin-bottom: 0.5rem;
        }}
        .snav-logo {{
            font-size: 1.45rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            color: {v['text_color']};
            line-height: 1;
        }}
        .snav-logo span {{ color: {primary_color}; }}
        .snav-tagline {{
            font-size: 0.6rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            color: {v['text_muted']};
            margin-top: 0.3rem;
        }}
        .snav-section-label {{
            font-size: 0.58rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: {v['text_muted']};
            padding: 1.1rem 1rem 0.35rem 1rem;
            opacity: 0.7;
        }}
        .snav-item {{
            display: flex;
            align-items: center;
            gap: 0.7rem;
            padding: 0.6rem 1rem;
            margin: 0.1rem 0.5rem;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 600;
            color: {v['text_color']};
            text-decoration: none !important;
            transition: all 0.18s ease;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        .snav-item:hover {{
            background: {v['badge_bg']};
            color: {primary_color};
            border-color: {v['border_color_hex']};
            text-decoration: none !important;
        }}
        .snav-item.active {{
            background: {v['badge_bg']};
            color: {primary_color};
            border-color: {primary_color};
            border-left: 3px solid {primary_color};
            font-weight: 700;
        }}
        .snav-icon {{
            width: 16px;
            height: 16px;
            opacity: 0.65;
            flex-shrink: 0;
        }}
        .snav-item:hover .snav-icon,
        .snav-item.active .snav-icon {{
            opacity: 1;
        }}
        .snav-divider {{
            height: 1px;
            background: {v['border_color_hex']};
            margin: 0.75rem 1rem;
        }}

        /* Nav Labels in Sidebar */
        .nav-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {v['text_muted']};
            font-weight: 700;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        /* Header HUD Card */
        .saas-header {{
            background: {v['header_grad']};
            border: 1px solid {v['header_border']};
            border-radius: 12px;
            padding: 1.25rem 2rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: {v['card_shadow']};
        }}
        .saas-header-title h1 {{
            margin: 0;
            font-size: 1.6rem;
            font-weight: 800;
            color: {v['text_color']} !important;
            letter-spacing: -0.02em;
        }}
        .saas-header-title p {{
            margin: 0.2rem 0 0 0;
            color: {v['text_muted']};
            font-size: 0.85rem;
            font-weight: 500;
        }}
        .saas-badge {{
            background-color: {v['badge_bg']};
            color: {v['badge_text']};
            padding: 0.4rem 0.8rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            border: 1px solid {v['badge_border']};
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .status-dot {{
            width: 8px;
            height: 8px;
            background-color: {primary_color};
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px {primary_color};
        }}

        /* Clean SaaS Cards */
        .saas-card {{
            background-color: {v['card_bg']} !important;
            border: 1px solid {v['border_color']} !important;
            border-radius: 12px !important;
            padding: 1.25rem !important;
            box-shadow: {v['card_shadow']} !important;
            margin-bottom: 1.5rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }}
        .saas-card:hover {{
            transform: translateY(-2px);
            border-color: {primary_color} !important;
        }}
        .saas-card h3 {{
            margin: 0 0 0.5rem 0;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: {v['text_muted']};
            font-weight: 600;
        }}
        .saas-card-value {{
            margin: 0;
            font-size: 1.85rem;
            font-weight: 800;
            color: {v['text_color']} !important;
        }}
        .saas-card-subtext {{
            margin: 0.25rem 0 0 0;
            font-size: 0.75rem;
            color: {v['text_muted']};
            font-weight: 500;
        }}

        /* Threat Badges */
        .saas-badge-clear {{
            background-color: rgba(16, 185, 129, 0.1);
            color: #10B981;
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 700;
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}
        .saas-badge-suspicious {{
            background-color: rgba(245, 158, 11, 0.1);
            color: {v['badge_suspicious_text']};
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 700;
            border: 1px solid rgba(245, 158, 11, 0.25);
        }}
        .saas-badge-critical {{
            background-color: rgba(239, 68, 68, 0.1);
            color: {v['badge_critical_text']};
            padding: 0.25rem 0.5rem;
            border-radius: 6px;
            font-size: 0.7rem;
            font-weight: 700;
            border: 1px solid rgba(239, 68, 68, 0.25);
        }}

        /* Credit Card Widget */
        .saas-token-card {{
            background: linear-gradient(135deg, #1E1B4B 0%, #311042 100%);
            border: 1px solid #4338CA;
            color: #FFFFFF;
            border-radius: 14px;
            padding: 1.5rem;
            aspect-ratio: 1.586/1;
            width: 100%;
            max-width: 300px;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.2);
            margin: 0 auto 1rem auto;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .saas-token-chip {{
            width: 38px;
            height: 28px;
            background: linear-gradient(135deg, #F59E0B, #D97706);
            border-radius: 4px;
            box-shadow: inset 0 1px 3px rgba(255,255,255,0.3);
        }}
        .saas-token-number {{
            font-size: 1.2rem;
            letter-spacing: 0.1em;
            font-weight: 700;
            margin: 0.75rem 0;
            font-family: 'JetBrains Mono', monospace;
            color: #FFFFFF;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }}
        .saas-token-footer {{
            display: flex;
            justify-content: space-between;
            font-size: 0.65rem;
            color: #A5B4FC;
            font-family: 'JetBrains Mono', monospace;
            text-transform: uppercase;
        }}

        /* Decision Panels */
        .alert-panel-decline {{
            background-color: rgba(239, 68, 68, 0.08);
            border: 1.5px solid #EF4444;
            padding: 1.25rem;
            border-radius: 8px;
            color: {v['badge_critical_text']};
            margin-top: 0.5rem;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.1);
        }}
        .alert-panel-mfa {{
            background-color: rgba(245, 158, 11, 0.08);
            border: 1.5px solid #F59E0B;
            padding: 1.25rem;
            border-radius: 8px;
            color: {v['badge_suspicious_text']};
            margin-top: 0.5rem;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.1);
        }}
        .alert-panel-approve {{
            background-color: rgba(16, 185, 129, 0.08);
            border: 1.5px solid #10B981;
            padding: 1.25rem;
            border-radius: 8px;
            color: #059669;
            margin-top: 0.5rem;
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.1);
        }}

        /* Blueprint step cards */
        .saas-blueprint {{
            background-color: {v['card_bg']};
            border: 1px solid {v['border_color']};
            padding: 1.25rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid {primary_color};
        }}
        .saas-blueprint-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }}
        .saas-blueprint-number {{
            background-color: {v['border_color']};
            color: {v['text_color']};
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            font-size: 0.75rem;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }}
        .saas-blueprint-title {{
            font-size: 0.95rem;
            font-weight: 700;
            color: {v['text_color']};
        }}
        .saas-blueprint-desc {{
            color: {v['text_muted']};
            font-size: 0.85rem;
            line-height: 1.5;
            margin: 0;
        }}

        /* Custom Secondary Button */
        .stButton > button {{
            background-color: {v['card_bg']} !important;
            color: {v['text_color']} !important;
            border: 1px solid {v['border_color']} !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            box-shadow: {v['card_shadow']} !important;
        }}
        .stButton > button:hover {{
            border-color: {primary_color} !important;
            color: {primary_color} !important;
            background-color: {v['badge_bg']} !important;
        }}

        /* Custom Primary Button (Pill, Glowing Violet) */
        .stButton > button[kind="primary"] {{
            background-color: {primary_color} !important;
            color: #FFFFFF !important;
            border-radius: 50px !important;
            border: none !important;
            font-weight: 700 !important;
            padding: 0.5rem 2rem !important;
            box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.3) !important;
            transition: all 0.2s ease-in-out !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {primary_hover} !important;
            box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5) !important;
            transform: translateY(-1px) !important;
        }}

        /* Footer styling */
        .portal-footer {{
            border-top: 1px solid {v['border_color']};
            margin-top: 3rem;
            padding: 1.5rem 0;
            text-align: center;
            font-size: 0.8rem;
            color: {v['text_muted']};
        }}
        .footer-company {{
            font-weight: 700;
            color: {v['text_color']};
        }}

        /* ── Skeleton Loader ─────────────────────────────────── */
        @keyframes shimmer {{
            0%   {{ background-position: -800px 0; }}
            100% {{ background-position:  800px 0; }}
        }}
        .skeleton-base {{
            background: linear-gradient(
                90deg,
                {v['card_bg']} 25%,
                {v['border_color_hex']} 50%,
                {v['card_bg']} 75%
            );
            background-size: 800px 100%;
            animation: shimmer 1.6s infinite linear;
            border-radius: 8px;
        }}
        .skeleton-wrapper {{
            padding: 0;
            width: 100%;
        }}
        .skeleton-header {{
            height: 56px;
            width: 70%;
            margin-bottom: 0.6rem;
        }}
        .skeleton-header-sub {{
            height: 18px;
            width: 45%;
            margin-bottom: 2rem;
        }}
        .skeleton-kpi-row {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}
        .skeleton-kpi {{
            height: 96px;
            border-radius: 12px;
        }}
        .skeleton-chart-wide {{
            height: 260px;
            border-radius: 12px;
            margin-bottom: 1.5rem;
        }}
        .skeleton-row {{
            display: grid;
            grid-template-columns: 1.6fr 1fr;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .skeleton-block {{
            height: 220px;
            border-radius: 12px;
        }}
        .skeleton-block-sm {{
            height: 140px;
            border-radius: 12px;
        }}
        .skeleton-3col {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
        }}

        /* ── Responsive: Tablet (≤900px) ──────────────────────── */
        @media (max-width: 900px) {{
            .skeleton-kpi-row {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .skeleton-3col {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .skeleton-row {{
                grid-template-columns: 1fr;
            }}
            .saas-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.75rem;
                padding: 1rem 1.25rem;
            }}
            .saas-header-title h1 {{ font-size: 1.3rem; }}
        }}

        /* ── Responsive: Mobile (≤600px) ──────────────────────── */
        @media (max-width: 600px) {{
            /* Main content padding reduction */
            .block-container {{
                padding: 1rem 0.75rem !important;
                max-width: 100% !important;
            }}
            /* Stack sidebar nav label sections */
            .snav-brand {{
                padding: 1rem 0.75rem 0.75rem 0.75rem;
            }}
            .snav-logo {{ font-size: 1.2rem; }}
            .snav-item {{
                padding: 0.5rem 0.75rem;
                font-size: 0.78rem;
            }}
            /* KPI skeleton row: single column on small mobile */
            .skeleton-kpi-row {{
                grid-template-columns: 1fr 1fr;
                gap: 0.75rem;
            }}
            .skeleton-kpi {{ height: 80px; }}
            .skeleton-chart-wide {{ height: 180px; }}
            .skeleton-3col {{ grid-template-columns: 1fr; }}
            .skeleton-block {{ height: 160px; }}
            .skeleton-block-sm {{ height: 110px; }}
            /* Cards */
            .saas-card {{ padding: 1rem !important; }}
            .saas-card-value {{ font-size: 1.5rem; }}
            .saas-header {{
                padding: 0.9rem 1rem;
                border-radius: 8px;
            }}
            .saas-header-title h1 {{ font-size: 1.15rem; }}
            /* Token card shrink */
            .saas-token-card {{ max-width: 100%; }}
            .saas-token-number {{ font-size: 1rem; }}
            /* Blueprint cards */
            .saas-blueprint {{ padding: 1rem; }}
            .saas-blueprint-title {{ font-size: 0.88rem; }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_footer():
    st.markdown("""
        <div class="portal-footer">
            &copy; 2026 <span class="footer-company">Sentinel AI Security</span>. Operational Console Systems. All Rights Reserved. Deployed Operator Profile: <b>Meet R Kakadiya</b>
        </div>
    """, unsafe_allow_html=True)

def render_skeleton_loading(label: str = "Loading intelligence assets…"):
    """Render animated shimmer skeleton placeholders while model.pkl loads."""
    v = THEME_VARS
    # Pulse dot + label
    primary = "#7C3AED" if v.get("bg_app", "#07060A") == "#07060A" else "#6001FC"
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.75rem;">
        <span style="width:10px;height:10px;background:{primary};border-radius:50%;
                     display:inline-block;box-shadow:0 0 10px {primary};
                     animation:shimmer 1.6s infinite linear;"></span>
        <span style="font-size:0.8rem;font-weight:700;text-transform:uppercase;
                     letter-spacing:0.1em;color:{v.get('text_muted','#6B7280')};"
        >{label}</span>
    </div>
    <div class="skeleton-wrapper">
        <!-- Header skeleton -->
        <div class="skeleton-base skeleton-header"></div>
        <div class="skeleton-base skeleton-header-sub"></div>
        <!-- KPI row -->
        <div class="skeleton-kpi-row">
            <div class="skeleton-base skeleton-kpi"></div>
            <div class="skeleton-base skeleton-kpi"></div>
            <div class="skeleton-base skeleton-kpi"></div>
            <div class="skeleton-base skeleton-kpi"></div>
        </div>
        <!-- Wide chart -->
        <div class="skeleton-base skeleton-chart-wide"></div>
        <!-- Two-column row -->
        <div class="skeleton-row">
            <div class="skeleton-base skeleton-block"></div>
            <div class="skeleton-base skeleton-block"></div>
        </div>
        <!-- 3-col footer cards -->
        <div class="skeleton-3col">
            <div class="skeleton-base skeleton-block-sm"></div>
            <div class="skeleton-base skeleton-block-sm"></div>
            <div class="skeleton-base skeleton-block-sm"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


@st.cache_resource
def load_dashboard_assets():
    # Attempt to load model files
    for path in ["dashboard/model.pkl", "model.pkl"]:
        if os.path.exists(path):
            try:
                return joblib.load(path)
            except (IOError, EOFError, ValueError, IndexError, KeyError, AttributeError, ImportError, RuntimeError):
                pass
    return None

def init_shared_sidebar(theme_mode):
    """Render the premium custom sidebar navigation."""
    import streamlit as st
    is_white = theme_mode == "Professional White"
    primary  = "#6001FC" if is_white else "#7C3AED"
    bg       = "#F8FAFC" if is_white else "#0C0A12"
    txt      = "#090D1A" if is_white else "#F3F4F6"
    muted    = "#94A3B8" if is_white else "#64748B"
    bdr      = "#E2E8F0" if is_white else "#1E293B"
    badge_bg = "rgba(96,1,252,0.06)" if is_white else "rgba(124,58,237,0.1)"

    # Detect current page for active state
    cur = ""
    try:
        import inspect
        import os
        for frame in inspect.stack():
            filename = frame.filename
            if filename.endswith(".py"):
                basename = os.path.basename(filename)
                norm_path = os.path.normpath(filename).split(os.sep)
                if basename == "app.py" or "pages" in norm_path:
                    cur = basename
                    break
    except Exception:
        pass

    def _active(path):
        if path == "/":
            return " active" if cur in ("", "/", "app.py") else ""
        return " active" if path.lower() in cur.lower() else ""

    def _icon(d):
        icons = {
            "home":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/></svg>',
            "cmd":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>',
            "threat":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l9 4v6c0 5.25-3.75 10.14-9 11.25C6.75 22.14 3 17.25 3 12V6l9-4z"/><path d="M12 8v4M12 16h.01"/></svg>',
            "policy":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4"/><path d="M12 2l9 4v6c0 5.25-3.75 10.14-9 11.25C6.75 22.14 3 17.25 3 12V6l9-4z"/></svg>',
            "batch":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 17.5h7M17.5 14v7"/></svg>',
            "profiler": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg>',
            "smote":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v2M12 20v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M2 12h2M20 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>',
            "health":   '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
            "audit":    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
            "api":      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 12h16M4 18h7"/><path d="M15 15l2 2 4-4"/></svg>',
            "explorer": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>',
            "shap":     '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2a10 10 0 100 20A10 10 0 0012 2z"/><path d="M12 8v4l3 3"/></svg>',
        }
        return icons.get(d, "")

    nav_html = f"""
    <style>
        section[data-testid="stSidebar"] > div {{
            padding: 0 !important;
        }}
        section[data-testid="stSidebar"] {{
            background: {bg} !important;
            border-right: 1px solid {bdr} !important;
        }}
    </style>
    <div class="snav-brand">
        <div class="snav-logo">Sentinel<span>AI</span></div>
        <div class="snav-tagline">Risk Intelligence Hub</div>
    </div>

    <div class="snav-section-label">Dashboard</div>
    <a class="snav-item{_active('/')}" href="/" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('home')}</span>Overview
    </a>

    <div class="snav-section-label">Required Pages</div>
    <a class="snav-item{_active('Command_Center')}" href="/Command_Center_Hub" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('cmd')}</span>Overview
    </a>
    <a class="snav-item{_active('Transaction_Explorer')}" href="/Transaction_Explorer" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('explorer')}</span>Transaction Explorer
    </a>
    <a class="snav-item{_active('SHAP_Explainer')}" href="/SHAP_Explainer" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('shap')}</span>SHAP Explainer
    </a>

    <div class="snav-section-label">Operations</div>
    <a class="snav-item{_active('Threat_Simulator')}" href="/Threat_Simulator_Lab" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('threat')}</span>Threat Simulator Lab
    </a>
    <a class="snav-item{_active('Risk_Policy')}" href="/Risk_Policy_Optimizer" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('policy')}</span>Risk Policy Optimizer
    </a>
    <a class="snav-item{_active('Batch_Predictor')}" href="/Batch_Predictor_Hub" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('batch')}</span>Batch Predictor Hub
    </a>
    <a class="snav-item{_active('Customer_Risk')}" href="/Customer_Risk_Profiler" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('profiler')}</span>Customer Risk Profiler
    </a>

    <div class="snav-section-label">Data Science &amp; Audit</div>
    <a class="snav-item{_active('SMOTE')}" href="/SMOTE_&_AI_Science" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('smote')}</span>SMOTE &amp; AI Science
    </a>
    <a class="snav-item{_active('Model_Health')}" href="/Model_Health_Telemetry" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('health')}</span>Model Health &amp; Telemetry
    </a>
    <a class="snav-item{_active('Audit')}" href="/Audit_Compliance_Ledger" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('audit')}</span>Audit Compliance Ledger
    </a>

    <div class="snav-section-label">Developer &amp; System</div>
    <a class="snav-item{_active('API_Gateway')}" href="/API_Gateway_Sandbox" target="_self">
        <span class="snav-icon" style="color:{primary};">{_icon('api')}</span>API Gateway Sandbox
    </a>

    <div class="snav-divider"></div>
    """
    st.sidebar.markdown(nav_html, unsafe_allow_html=True)

    # ── Preferences ──────────────────────────────────────────────
    st.sidebar.markdown(
        f'<div class="snav-section-label">Console Preferences</div>',
        unsafe_allow_html=True
    )
    theme_options = ["Professional White", "Professional Black"]
    sel = st.sidebar.selectbox(
        "Theme", theme_options,
        index=theme_options.index(theme_mode) if theme_mode in theme_options else 0,
        key="global_theme_selector"
    )
    if sel != theme_mode:
        st.session_state.theme_mode = sel
        st.rerun()

    # ── Deployed Model Card ───────────────────────────────────────
    assets = load_dashboard_assets()
    if assets:
        card_bg  = "#FFFFFF" if is_white else "#0F172A"
        card_txt = txt
        st.sidebar.markdown(
            f'<div class="snav-section-label">Deployed Model Node</div>',
            unsafe_allow_html=True
        )
        st.sidebar.markdown(f"""
        <div style="background:{card_bg};padding:0.8rem 0.9rem;border-radius:8px;
                    border:1px solid {bdr};font-size:0.7rem;line-height:1.7;
                    font-family:'JetBrains Mono',monospace;margin:0 0.5rem;">
            <div style="color:{muted};margin-bottom:0.15rem;">KERNEL</div>
            <div style="color:{card_txt};font-weight:700;margin-bottom:0.5rem;">{assets['best_model_name'].upper()}</div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:{muted};">ROC-AUC</span>
                <span style="color:{card_txt};font-weight:700;">{assets['performance']['AUC-ROC']:.4f}</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:{muted};">PRECISION</span>
                <span style="color:{card_txt};font-weight:700;">{assets['performance']['Precision']:.4f}</span>
            </div>
            <div style="margin-top:0.5rem;display:flex;align-items:center;gap:0.4rem;">
                <span style="width:6px;height:6px;background:{primary};border-radius:50%;
                             display:inline-block;box-shadow:0 0 6px {primary};"></span>
                <span style="color:{primary};font-weight:700;">ACTIVE DEPLOYED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
