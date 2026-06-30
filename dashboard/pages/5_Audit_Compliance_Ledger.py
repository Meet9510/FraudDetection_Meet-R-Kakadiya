"""Sentinel AI — Audit Compliance Ledger: searchable, exportable transaction log."""

import time
import streamlit as st
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
    page_title="Sentinel AI — Audit Ledger",
    page_icon="ðŸ“‹",
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
        <h1>Audit Compliance Ledger</h1>
        <p>Secure, read-only log of all transactions, model decisions, and risk scores.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Loading audit ledger…")

assets = load_dashboard_assets()
_loading_slot.empty()

if not assets:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

active_threshold = st.session_state.custom_threshold

sample_txs = assets['sample_txs'].copy()

for col in ['card4', 'card6', 'P_emaildomain']:
    if col in sample_txs.columns and col in assets['label_encoders']:
        le = assets['label_encoders'][col]
        try:
            valid_mask = sample_txs[col].notnull()
            idxs = sample_txs.loc[valid_mask, col].astype(int).clip(0, len(le.classes_)-1)
            # Cast to object first so pandas accepts string values into the column
            sample_txs[col] = sample_txs[col].astype(object)
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

# ── Summary bar ───────────────────────────────────────────────
total    = len(sample_txs)
critical = (sample_txs['Risk Tier'] == 'Critical Risk').sum()
susp     = (sample_txs['Risk Tier'] == 'Suspicious').sum()
clear    = (sample_txs['Risk Tier'] == 'Clear').sum()

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

# ── Search + filters + export ─────────────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.75rem 0;font-size:1rem;font-weight:800;color:{v_text};">
    Transaction Ledger Search
</h3>
""", unsafe_allow_html=True)

fc1, fc2, fc3 = st.columns([2.5, 1.2, 1])
with fc1:
    search_tx = st.text_input(
        "Search by Transaction ID",
        placeholder="Enter full or partial transaction ID…",
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
        label="â†“ Export CSV",
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

st.markdown(f"""
<p style="margin:0.5rem 0 0.5rem 0;font-size:0.76rem;color:{v_muted};">
    Showing {min(len(filtered), 150):,} of {len(filtered):,} records
</p>
""", unsafe_allow_html=True)

# ── Dataframe ─────────────────────────────────────────────────
display_df = filtered[[
    'TransactionID', 'TransactionAmt', 'HourOfDay',
    'card4', 'card6', 'Probability', 'Risk Tier', 'Actual'
]].head(150).copy()

display_df['Actual'] = display_df['Actual'].astype(bool)
display_df['card4']  = display_df['card4'].astype(str).str.upper()
display_df['card6']  = display_df['card6'].astype(str).str.upper()

st.dataframe(
    display_df,
    use_container_width=True,
    height=420,
    column_config={
        "TransactionID":  st.column_config.TextColumn("Txn ID", width="small"),
        "TransactionAmt": st.column_config.NumberColumn("Amount", format="$%.2f", width="small"),
        "HourOfDay":      st.column_config.NumberColumn("Hour", format="%d", width="small"),
        "card4":          st.column_config.TextColumn("Network", width="small"),
        "card6":          st.column_config.TextColumn("Type", width="small"),
        "Probability":    st.column_config.ProgressColumn(
            "Risk Index", format="%.1%%", min_value=0, max_value=1, width="medium"
        ),
        "Risk Tier":      st.column_config.TextColumn("Tier", width="medium"),
        "Actual":         st.column_config.CheckboxColumn("Is Fraud?", width="small"),
    },
    hide_index=True
)

render_footer()
