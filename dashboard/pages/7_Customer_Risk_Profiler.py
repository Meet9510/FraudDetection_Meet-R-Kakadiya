"""Sentinel AI — Customer Risk Profiler: per-issuer risk aggregation from real test-set data."""

import streamlit as st
import pandas as pd
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
    page_title="Sentinel AI — Customer Risk Profiler",
    page_icon="👤",
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
        <h1>Customer Risk Profiler</h1>
        <p>Real test-set transaction data grouped by card issuer (card1) with ML risk scores.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Loading customer intelligence data…")
assets = load_dashboard_assets()
_loading_slot.empty()

if not assets:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

threshold  = st.session_state.custom_threshold
raw        = assets['sample_txs'].copy()

# ── Build real card-issuer profiles from model.pkl test data ──
# card1 is the issuer code — group by it as "customer"
card_groups = (
    raw.groupby("card1")
    .agg(
        Transactions   = ("TransactionAmt", "count"),
        Avg_Amount     = ("TransactionAmt", "mean"),
        Total_Amount   = ("TransactionAmt", "sum"),
        Avg_Risk       = ("Probability",    "mean"),
        Peak_Risk      = ("Probability",    "max"),
        Actual_Fraud   = ("Actual",         "sum"),
        Fraud_Rate     = ("Actual",         "mean"),
        Avg_Hour       = ("HourOfDay",      "mean"),
    )
    .reset_index()
    .rename(columns={"card1": "Card_ID"})
)

def tier(prob):
    if prob >= 0.75:   return "Critical"
    if prob >= threshold: return "Suspicious"
    return "Clear"

card_groups["Risk_Tier"]    = card_groups["Avg_Risk"].apply(tier)
card_groups["Avg_Amount"]   = card_groups["Avg_Amount"].round(2)
card_groups["Total_Amount"] = card_groups["Total_Amount"].round(2)
card_groups["Avg_Risk"]     = card_groups["Avg_Risk"].round(4)
card_groups["Peak_Risk"]    = card_groups["Peak_Risk"].round(4)
card_groups["Fraud_Rate"]   = (card_groups["Fraud_Rate"] * 100).round(1)

# Keep top-30 by transaction count for a manageable UI list
top_cards = card_groups.nlargest(30, "Transactions").reset_index(drop=True)

# ── Fleet Summary KPIs ────────────────────────────────────────
total_cards = len(top_cards)
crit_cards  = (top_cards["Risk_Tier"] == "Critical").sum()
sus_cards   = (top_cards["Risk_Tier"] == "Suspicious").sum()
avg_fleet   = top_cards["Avg_Risk"].mean() * 100
total_fraud = int(top_cards["Actual_Fraud"].sum())

k1, k2, k3, k4, k5 = st.columns(5)
for col, (label, val, accent) in zip([k1,k2,k3,k4,k5], [
    ("Monitored Issuers",   f"{total_cards}",       primary),
    ("Critical Issuers",    f"{crit_cards}",         "#EF4444"),
    ("Suspicious Issuers",  f"{sus_cards}",          "#F59E0B"),
    ("Fleet Avg Risk",      f"{avg_fleet:.1f}%",     "#10B981"),
    ("Confirmed Fraud Txs", f"{total_fraud}",        "#6366F1"),
]):
    with col:
        st.markdown(f"""
        <div style="background:{v_card};border:1px solid {v_border};
                    border-top:3px solid {accent};border-radius:12px;
                    padding:1rem 1.1rem;text-align:center;">
            <p style="margin:0;font-size:0.62rem;font-weight:700;text-transform:uppercase;
                      letter-spacing:0.09em;color:{v_muted};">{label}</p>
            <p style="margin:0.25rem 0 0;font-size:1.6rem;font-weight:900;color:{accent};">{val}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Card selector + detail view ───────────────────────────────
col_left, col_right = st.columns([1, 1.6], gap="large")

with col_left:
    st.markdown(f"""
    <p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
              letter-spacing:0.1em;color:{primary};margin-bottom:0.5rem;">
        Select Card Issuer
    </p>
    """, unsafe_allow_html=True)

    card_options = top_cards["Card_ID"].astype(str).tolist()
    selected_card_str = st.selectbox("Card ID", card_options, label_visibility="collapsed")
    row = top_cards[top_cards["Card_ID"].astype(str) == selected_card_str].iloc[0]

    tier_color  = "#EF4444" if row["Risk_Tier"] == "Critical" else ("#F59E0B" if row["Risk_Tier"] == "Suspicious" else "#10B981")
    tier_bg     = tier_color + "12"
    tier_border = tier_color + "33"

    # Use native Streamlit widgets — avoids HTML rendering bug in complex f-string blocks
    st.markdown(f"""
    <div style="background:{v_card};border:1px solid {v_border};border-radius:14px;
                padding:1rem 1.25rem;margin-top:0.75rem;">
        <p style="margin:0 0 0.2rem;font-size:0.62rem;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.12em;color:{v_muted};">Real Issuer Profile</p>
        <p style="margin:0 0 0.75rem;font-size:1.25rem;font-weight:900;color:{v_text};
                  font-family:'JetBrains Mono',monospace;">CARD-{row['Card_ID']}</p>
    </div>
    """, unsafe_allow_html=True)

    ma, mb = st.columns(2)
    with ma:
        st.metric("Transactions",   int(row['Transactions']))
        st.metric("Avg Amount",     f"${row['Avg_Amount']:.0f}")
        st.metric("Confirmed Fraud",int(row['Actual_Fraud']))
        st.metric("Fraud Rate",     f"{row['Fraud_Rate']:.1f}%")
    with mb:
        st.metric("Total Volume",   f"${row['Total_Amount']:,.0f}")
        st.metric("Avg Risk Score", f"{row['Avg_Risk']*100:.1f}%")
        st.metric("Peak Risk",      f"{row['Peak_Risk']*100:.1f}%")
        st.metric("Avg Hour",       f"{row['Avg_Hour']:.0f}:00")

    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                padding:0.6rem 1rem;background:{tier_bg};border:1px solid {tier_border};
                border-radius:10px;margin-top:0.5rem;">
        <span style="font-size:0.72rem;color:{v_muted};font-weight:600;">Risk Tier</span>
        <span style="font-weight:800;color:{tier_color};font-size:0.85rem;
                     font-family:'JetBrains Mono',monospace;">{row['Risk_Tier'].upper()}</span>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    # Pull actual transactions for this card from raw data
    card_txs = raw[raw["card1"] == int(selected_card_str)].copy().reset_index(drop=True)
    card_txs = card_txs.sort_values("HourOfDay")

    st.markdown(f"""
    <p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
              letter-spacing:0.1em;color:{primary};margin-bottom:0.5rem;">
        Transaction Risk Distribution (Real Data)
    </p>
    """, unsafe_allow_html=True)

    if len(card_txs) > 0:
        # Risk score scatter for each real transaction
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(card_txs))),
            y=card_txs["Probability"] * 100,
            mode='lines+markers',
            line=dict(color=primary, width=2),
            marker=dict(
                color=["#EF4444" if p >= 0.75 else ("#F59E0B" if p >= threshold else "#10B981")
                       for p in card_txs["Probability"]],
                size=9,
                symbol=["diamond" if a == 1 else "circle" for a in card_txs["Actual"]],
                line=dict(color="white", width=1)
            ),
            hovertemplate=(
                "<b>Tx #%{x}</b><br>"
                "Risk: %{y:.1f}%<br>"
                "Amount: $%{customdata[0]:.2f}<br>"
                "Hour: %{customdata[1]}:00<br>"
                "Actual Fraud: %{customdata[2]}<extra></extra>"
            ),
            customdata=list(zip(
                card_txs["TransactionAmt"],
                card_txs["HourOfDay"],
                card_txs["Actual"]
            ))
        ))
        fig.add_hline(y=threshold * 100, line_dash="dot", line_color=v_muted,
                      annotation_text=f"Threshold {threshold*100:.0f}%",
                      annotation_font_color=v_muted)
        fig.add_hline(y=75, line_dash="dot", line_color="rgba(239, 68, 68, 0.4)",
                      annotation_text="Critical 75%", annotation_font_color="#EF4444")
        fig.update_layout(
            template="plotly_white" if is_white else "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Transaction Index", gridcolor=v_border, zeroline=False),
            yaxis=dict(title="ML Risk Score (%)", range=[0, 105], gridcolor=v_border),
            font=dict(family="Plus Jakarta Sans", color=v_muted, size=11),
            height=270, margin=dict(t=10, b=10, l=10, r=10), showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Amount bar chart coloured by risk tier
        fig2 = go.Figure(go.Bar(
            x=list(range(len(card_txs))),
            y=card_txs["TransactionAmt"],
            marker_color=["#EF4444" if p >= 0.75 else ("#F59E0B" if p >= threshold else primary)
                          for p in card_txs["Probability"]],
            hovertemplate="Tx #%{x}<br>$%{y:.2f}<extra></extra>"
        ))
        fig2.update_layout(
            template="plotly_white" if is_white else "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Transaction Index", gridcolor=v_border, zeroline=False),
            yaxis=dict(title="Amount ($)", gridcolor=v_border),
            font=dict(family="Plus Jakarta Sans", color=v_muted, size=11),
            height=200, margin=dict(t=5, b=10, l=10, r=10), showlegend=False
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.caption(f"🔷 Diamond markers = Confirmed fraud · Colour = Risk tier · {len(card_txs)} real transactions shown")
    else:
        st.info("No transactions found for this card in the test dataset.")

st.markdown("---")

# ── Full transaction table for selected card ──────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.5rem;font-size:1rem;font-weight:800;color:{v_text};">
    Individual Transactions — CARD-{selected_card_str}
</h3>
""", unsafe_allow_html=True)

if len(card_txs) > 0:
    display_cols = ["TransactionID", "TransactionAmt", "HourOfDay",
                    "Probability", "Risk Tier", "Actual", "DeviceRisk"]
    available = [c for c in display_cols if c in card_txs.columns]
    disp_df = card_txs[available].copy()
    disp_df["Probability"] = (disp_df["Probability"] * 100).round(2)
    disp_df.rename(columns={"Probability": "Risk Score (%)", "Actual": "Confirmed Fraud"}, inplace=True)
    st.dataframe(
        disp_df.style.background_gradient(subset=["Risk Score (%)"], cmap="RdYlGn_r"),
        use_container_width=True, height=300
    )

st.markdown("---")

# ── Fleet Risk Register ───────────────────────────────────────
st.markdown(f"""
<h3 style="margin:0 0 0.5rem;font-size:1rem;font-weight:800;color:{v_text};">
    Top-30 Issuer Fleet Risk Register (Real Data)
</h3>
""", unsafe_allow_html=True)

display_fleet = top_cards.copy()
display_fleet["Card_ID"]    = "CARD-" + display_fleet["Card_ID"].astype(str)
display_fleet["Avg_Risk"]   = (display_fleet["Avg_Risk"] * 100).round(1)
display_fleet["Peak_Risk"]  = (display_fleet["Peak_Risk"] * 100).round(1)
display_fleet["Avg_Amount"] = display_fleet["Avg_Amount"].round(0).astype(int)
display_fleet.rename(columns={
    "Card_ID":    "Card Issuer",
    "Transactions": "Txs",
    "Avg_Amount": "Avg Amt ($)",
    "Total_Amount": "Total Vol ($)",
    "Avg_Risk":   "Avg Risk (%)",
    "Peak_Risk":  "Peak Risk (%)",
    "Actual_Fraud": "Fraud Txs",
    "Fraud_Rate": "Fraud Rate (%)",
    "Avg_Hour":   "Avg Hour",
    "Risk_Tier":  "Tier",
}, inplace=True)

st.dataframe(
    display_fleet.style.background_gradient(
        subset=["Avg Risk (%)","Peak Risk (%)","Fraud Rate (%)"], cmap="RdYlGn_r"
    ),
    use_container_width=True, height=380, hide_index=True
)

render_footer()
