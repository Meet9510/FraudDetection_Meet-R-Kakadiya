"""Sentinel AI — Transaction Explorer: searchable, filterable real transaction table with live risk scoring."""

import streamlit as st
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
    page_title="Sentinel AI — Transaction Explorer",
    page_icon="🔍",
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
        <h1>Transaction Explorer</h1>
        <p>Search, filter, and inspect individual transactions with live ML risk scores from the test dataset.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Loading transaction ledger…")
assets = load_dashboard_assets()
_loading_slot.empty()

if not assets:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

threshold = st.session_state.custom_threshold
df = assets['sample_txs'].copy()

# Decode label-encoded columns back to strings
le_map = assets['label_encoders']
for col in ['card4', 'card6', 'P_emaildomain']:
    if col in df.columns and col in le_map:
        le = le_map[col]
        try:
            idxs = df[col].astype(int).clip(0, len(le.classes_) - 1)
            df[col] = [le.classes_[i] for i in idxs]
        except (ValueError, TypeError, KeyError):
            pass

df['Risk Score (%)'] = (df['Probability'] * 100).round(2)
df['Risk Tier'] = df['Probability'].apply(
    lambda p: "Critical" if p >= 0.75 else ("Suspicious" if p >= threshold else "Clear")
)
df['Confirmed Fraud'] = df['Actual'].map({1: "✓ Fraud", 0: "Legitimate"})

# ── Sidebar Filters ───────────────────────────────────────────
st.sidebar.markdown("<div class='nav-label'>Transaction Filters</div>", unsafe_allow_html=True)

search_id = st.sidebar.text_input(" Search by TransactionID", placeholder="e.g. 3089777")

tier_filter = st.sidebar.multiselect(
    "Risk Tier", ["Clear", "Suspicious", "Critical"],
    default=["Clear", "Suspicious", "Critical"]
)

amt_range = st.sidebar.slider(
    "Amount Range ($)", 0.0, float(df['TransactionAmt'].max()),
    (0.0, float(df['TransactionAmt'].max()))
)

hour_range = st.sidebar.slider("Hour of Day", 0, 23, (0, 23))

fraud_filter = st.sidebar.radio(
    "Transaction Type", ["All", "Fraud Only", "Legitimate Only"]
)

# ── Apply filters ─────────────────────────────────────────────
filtered = df.copy()

if search_id.strip():
    try:
        sid = int(search_id.strip())
        filtered = filtered[filtered['TransactionID'] == sid]
    except ValueError:
        st.sidebar.warning("TransactionID must be numeric")

filtered = filtered[filtered['Risk Tier'].isin(tier_filter)]
filtered = filtered[
    (filtered['TransactionAmt'] >= amt_range[0]) &
    (filtered['TransactionAmt'] <= amt_range[1])
]
filtered = filtered[
    (filtered['HourOfDay'] >= hour_range[0]) &
    (filtered['HourOfDay'] <= hour_range[1])
]
if fraud_filter == "Fraud Only":
    filtered = filtered[filtered['Actual'] == 1]
elif fraud_filter == "Legitimate Only":
    filtered = filtered[filtered['Actual'] == 0]

# ── Filter summary KPIs ───────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
for col, (label, val, accent) in zip([k1,k2,k3,k4], [
    ("Filtered Transactions", f"{len(filtered):,}",                    primary),
    ("Fraud in View",         f"{int(filtered['Actual'].sum()):,}",     "#EF4444"),
    ("Avg Risk Score",        f"{filtered['Risk Score (%)'].mean():.1f}%" if len(filtered) else "—", "#F59E0B"),
    ("Avg Amount",            f"${filtered['TransactionAmt'].mean():.2f}" if len(filtered) else "—", "#10B981"),
]):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {v_border};border-top:3px solid {accent};
                    border-radius:12px;padding:1rem 1.1rem;text-align:center;">
            <p style="margin:0;font-size:0.62rem;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.09em;color:{v_muted};">{label}</p>
            <p style="margin:0.25rem 0 0;font-size:1.6rem;font-weight:900;color:{accent};">{val}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Transaction Table ─────────────────────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.35rem;font-size:1rem;font-weight:800;color:{v_text};">
    Transaction Ledger — {len(filtered):,} records
</h3>
<p style="margin:0 0 0.75rem;font-size:0.78rem;color:{v_muted};">
    Click any row to load the live risk score detail below.
</p>
""", unsafe_allow_html=True)

DISPLAY_COLS = [
    'TransactionID', 'TransactionAmt', 'HourOfDay', 'card4', 'card6',
    'P_emaildomain', 'DeviceRisk', 'Risk Score (%)', 'Risk Tier', 'Confirmed Fraud'
]
avail_cols = [c for c in DISPLAY_COLS if c in filtered.columns]
display_df = filtered[avail_cols].reset_index(drop=True)

if len(display_df) == 0:
    st.info("No transactions match the current filters.")
else:
    st.dataframe(
        display_df.style.background_gradient(subset=["Risk Score (%)"], cmap="RdYlGn_r"),
        use_container_width=True,
        height=360,
        hide_index=True
    )

st.markdown("---")

# ── Live Risk Score by TransactionID ─────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.5rem;font-size:1rem;font-weight:800;color:{v_text};">
    Live Risk Score Lookup
</h3>
<p style="margin:0 0 0.75rem;font-size:0.78rem;color:{v_muted};">
    Enter a TransactionID from the table above to view its full risk breakdown.
</p>
""", unsafe_allow_html=True)

lookup_id = st.text_input("TransactionID", placeholder="Enter TransactionID…", key="lookup_txid")

if lookup_id.strip():
    try:
        lid = int(lookup_id.strip())
        match = df[df['TransactionID'] == lid]
        if len(match) == 0:
            st.warning(f"TransactionID {lid} not found in the test dataset (300 records).")
        else:
            row = match.iloc[0]
            prob   = float(row['Probability'])
            tier   = row['Risk Tier']
            t_col  = "#EF4444" if tier == "Critical" else ("#F59E0B" if tier == "Suspicious" else "#10B981")
            t_bg   = t_col + "12"
            t_bdr  = t_col + "33"
            decision = "DECLINE" if prob >= 0.75 else ("MFA CHALLENGE" if prob >= threshold else "APPROVE")

            dc1, dc2 = st.columns([1, 1.5], gap="large")

            with dc1:
                st.markdown(f"""
                <div style="background:{v_card};border:1px solid {v_border};border-radius:14px;padding:1.5rem;">
                    <p style="margin:0 0 0.25rem;font-size:0.62rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.12em;color:{v_muted};">Transaction Detail</p>
                    <p style="margin:0 0 1rem;font-size:1.3rem;font-weight:900;color:{v_text};
                              font-family:'JetBrains Mono',monospace;">#{lid}</p>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
                        <div>
                            <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Amount</p>
                            <p style="margin:0;font-size:1.1rem;font-weight:800;color:{v_text};">${row['TransactionAmt']:.2f}</p>
                        </div>
                        <div>
                            <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Hour</p>
                            <p style="margin:0;font-size:1.1rem;font-weight:800;color:{v_text};">{int(row['HourOfDay'])}:00</p>
                        </div>
                        <div>
                            <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Card Network</p>
                            <p style="margin:0;font-size:1rem;font-weight:700;color:{v_text};">{str(row.get('card4','—')).upper()}</p>
                        </div>
                        <div>
                            <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Funding</p>
                            <p style="margin:0;font-size:1rem;font-weight:700;color:{v_text};">{str(row.get('card6','—')).upper()}</p>
                        </div>
                        <div>
                            <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Email Domain</p>
                            <p style="margin:0;font-size:0.9rem;font-weight:700;color:{v_text};">{str(row.get('P_emaildomain','—'))}</p>
                        </div>
                        <div>
                            <p style="margin:0;font-size:0.62rem;color:{v_muted};text-transform:uppercase;font-weight:600;">Device Risk</p>
                            <p style="margin:0;font-size:1rem;font-weight:700;color:{'#EF4444' if row.get('DeviceRisk',0)==1 else '#10B981'};">
                                {'HIGH' if row.get('DeviceRisk',0)==1 else 'LOW'}
                            </p>
                        </div>
                    </div>
                    <div style="margin-top:1rem;padding-top:0.75rem;border-top:1px solid {v_border};
                                display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.72rem;color:{v_muted};">Confirmed Fraud</span>
                        <span style="font-weight:700;color:{'#EF4444' if row['Actual']==1 else '#10B981'};">
                            {'✓ FRAUD' if row['Actual']==1 else 'LEGITIMATE'}
                        </span>
                    </div>
                    <div style="margin-top:0.5rem;display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.72rem;color:{v_muted};">Decision</span>
                        <span style="background:{t_bg};color:{t_col};padding:0.2rem 0.75rem;
                                     border-radius:20px;font-size:0.72rem;font-weight:700;
                                     border:1px solid {t_bdr};font-family:'JetBrains Mono',monospace;">
                            {decision}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with dc2:
                # Risk gauge
                bar_color = "#EF4444" if prob >= 0.75 else ("#F59E0B" if prob >= threshold else "#10B981")
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=round(prob * 100, 1),
                    domain={'x': [0, 1], 'y': [0, 1]},
                    number={'suffix': "%", 'font': {'size': 40, 'family': 'Plus Jakarta Sans', 'color': bar_color}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1,
                                 'tickcolor': v_muted, 'tickfont': {'size': 10}},
                        'bar': {'color': bar_color, 'thickness': 0.28},
                        'bgcolor': "#E2E8F0" if is_white else "#1E293B",
                        'borderwidth': 0,
                        'steps': [
                            {'range': [0, threshold * 100], 'color': 'rgba(16,185,129,0.10)'},
                            {'range': [threshold * 100, 75],  'color': 'rgba(245,158,11,0.10)'},
                            {'range': [75, 100],               'color': 'rgba(239,68,68,0.10)'},
                        ],
                        'threshold': {'line': {'color': bar_color, 'width': 2},
                                      'thickness': 0.8, 'value': prob * 100}
                    }
                ))
                fig_g.update_layout(
                    height=250, margin=dict(t=20, b=10, l=20, r=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    template="plotly_white" if is_white else "plotly_dark",
                    font=dict(family="Plus Jakarta Sans", color=v_muted)
                )
                st.plotly_chart(fig_g, use_container_width=True)

                # Feature signals
                signals = []
                if row['TransactionAmt'] > df['TransactionAmt'].mean() * 2:
                    signals.append(("⚠", "Amount 2× above mean", "#EF4444"))
                if int(row['HourOfDay']) in [0,1,2,3,4,22,23]:
                    signals.append(("🌙", "Late-night transaction", "#F59E0B"))
                if row.get('DeviceRisk', 0) == 1:
                    signals.append(("📱", "High-risk device type", "#F59E0B"))
                email = str(row.get('P_emaildomain',''))
                if email in ['protonmail.com','mail.com','hotmail.com']:
                    signals.append(("📧", f"High-risk domain: {email}", "#EF4444"))
                if row.get('AmtToMeanRatio', 1) > 3:
                    signals.append(("📈", f"Amount ratio: {row.get('AmtToMeanRatio',1):.1f}×", "#EF4444"))

                if signals:
                    st.markdown(f"""
                    <p style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.1em;color:{primary};margin:0.5rem 0 0.4rem;">
                        Risk Signals
                    </p>
                    """, unsafe_allow_html=True)
                    for icon, msg, sc in signals:
                        sc_bg  = sc + "12"
                        sc_bdr = sc + "33"
                        st.markdown(f"""
                        <div style="background:{sc_bg};border:1px solid {sc_bdr};border-radius:8px;
                                    padding:0.5rem 0.75rem;margin-bottom:0.4rem;font-size:0.78rem;
                                    color:{sc};font-weight:600;">{icon} {msg}</div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("No elevated risk signals detected.")

    except ValueError:
        st.error("Please enter a valid numeric TransactionID.")

render_footer()
