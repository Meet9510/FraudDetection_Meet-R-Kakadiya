"""Sentinel AI — Batch Predictor Hub: bulk transaction scoring via CSV upload."""

import numpy as np
import pandas as pd
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
    page_title="Sentinel AI — Batch Predictor Hub",
    page_icon="⚙",
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
primary = "#6001FC" if is_white else "#7C3AED"
v_card = THEME_VARS['card_bg']
v_text = THEME_VARS['text_color']
v_muted = THEME_VARS['text_muted']
v_border = THEME_VARS['border_color_hex']

st.markdown("""
<div class="saas-header">
    <div class="saas-header-title">
        <h1>Batch Predictor Hub</h1>
        <p>Upload a CSV of transactions and receive bulk ML risk scores in seconds.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Initialising batch inference engine…")
assets = load_dashboard_assets()
_loading_slot.empty()

if not assets:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

threshold = st.session_state.custom_threshold

# ── Instructions ──────────────────────────────────────────────
st.markdown(f"""
<p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
          letter-spacing:0.1em;color:{primary};margin-bottom:0.5rem;">
    How To Use
</p>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
for col, (num, title, desc) in zip([c1, c2, c3], [
    ("01", "Upload CSV", "Your file must contain at least: TransactionAmt, card1, card4, card6, P_emaildomain columns."),
    ("02", "Auto-Score", "Sentinel AI engineers features and runs LightGBM inference on every row instantly."),
    ("03", "Download", "Export the enriched result CSV with RiskScore, RiskTier, and Decision columns appended."),
]):
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

# ── Sample CSV download ───────────────────────────────────────
sample_df = pd.DataFrame({
    "TransactionAmt": [150.0, 680.0, 1820.0, 45.0, 320.0],
    "card1":          [9500,  15000, 18200,  7800, 11000],
    "card4":          ["visa", "mastercard", "american express", "visa", "discover"],
    "card6":          ["debit", "credit", "credit", "debit", "credit"],
    "P_emaildomain":  ["gmail.com", "outlook.com", "protonmail.com", "gmail.com", "yahoo.com"],
    "HourOfDay":      [13, 22, 3, 10, 17],
})

st.download_button(
    "⬇ Download Sample CSV Template",
    data=sample_df.to_csv(index=False),
    file_name="sentinel_sample_transactions.csv",
    mime="text/csv",
)

st.markdown("---")

# ── File uploader ─────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload Transaction CSV",
    type=["csv"],
    help="Must include: TransactionAmt, card1, card4, card6, P_emaildomain"
)


def score_batch(df: pd.DataFrame) -> pd.DataFrame:
    results = []
    le_map = assets['label_encoders']
    scaler = assets['scaler']
    model = assets['model']
    num_cols = assets['numeric_cols']
    feats = assets['features']

    for _, row in df.iterrows():
        ir = pd.DataFrame(0.0, index=[0], columns=feats)
        amt = float(row.get("TransactionAmt", 150))
        card1 = float(row.get("card1", 10000))
        hour = int(row.get("HourOfDay", 12))
        card4 = str(row.get("card4", "visa")).lower()
        card6 = str(row.get("card6", "debit")).lower()
        email = str(row.get("P_emaildomain", "gmail.com")).lower()

        ir['TransactionAmt'] = amt
        ir['card1'] = card1
        ir['HourOfDay'] = hour
        ir['AmtToMeanRatio'] = amt / 135.0
        ir['DeviceRisk'] = 1 if 'credit' in card6 else 0
        ir['LogTransactionAmt'] = np.log1p(amt)
        ir['Card1AmtRatio'] = 1.0
        ir['EmailDomainRisk'] = 1 if email in ['mail.com',
                                               'protonmail.com', 'outlook.com', 'hotmail.com'] else 0
        ir['Card1Freq'] = 10

        for col_name, col_val in [('card4', card4), ('card6', card6), ('P_emaildomain', email)]:
            if col_name in le_map:
                le = le_map[col_name]
                v = col_val if col_val in le.classes_ else le.classes_[0]
                ir[col_name] = le.transform([v])[0]

        scaled = ir.copy()
        scaled[num_cols] = scaler.transform(ir[num_cols])
        prob = model.predict_proba(scaled)[:, 1][0]

        tier = "Critical" if prob >= 0.75 else (
            "Suspicious" if prob >= threshold else "Clear")
        decision = "DECLINE" if prob >= 0.75 else (
            "MFA CHALLENGE" if prob >= threshold else "APPROVE")
        results.append({**row.to_dict(), "RiskScore": round(prob, 4),
                        "RiskTier": tier, "Decision": decision})
    return pd.DataFrame(results)


if uploaded:
    try:
        raw = pd.read_csv(uploaded)
        required = {"TransactionAmt", "card1",
                    "card4", "card6", "P_emaildomain"}
        missing_cols = required - set(raw.columns)
        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            st.stop()

        st.markdown(
            f"**{len(raw):,} transactions loaded** — running inference…")
        with st.spinner("Scoring batch…"):
            results_df = score_batch(raw)

        # ── Summary KPIs ──────────────────────────────────────
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        total = len(results_df)
        clear = (results_df['RiskTier'] == 'Clear').sum()
        sus = (results_df['RiskTier'] == 'Suspicious').sum()
        crit = (results_df['RiskTier'] == 'Critical').sum()
        avg_risk = results_df['RiskScore'].mean() * 100

        k1, k2, k3, k4 = st.columns(4)
        for col, (label, val, accent) in zip([k1, k2, k3, k4], [
            ("Total Transactions", f"{total:,}",         primary),
            ("Clear (Approve)",    f"{clear:,}",         "#10B981"),
            ("Suspicious (MFA)",   f"{sus:,}",           "#F59E0B"),
            ("Critical (Decline)", f"{crit:,}",          "#EF4444"),
        ]):
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

        st.markdown("<div style='height:1.5rem'></div>",
                    unsafe_allow_html=True)

        # ── Result table ──────────────────────────────────────
        st.markdown(f"""
        <h3 style="margin:0 0 0.5rem 0;font-size:1rem;font-weight:800;color:{v_text};">
            Scored Transaction Results
        </h3>
        """, unsafe_allow_html=True)
        st.dataframe(
            results_df.style.background_gradient(
                subset=["RiskScore"], cmap="RdYlGn_r"),
            use_container_width=True, height=380
        )

        # ── Download ──────────────────────────────────────────
        csv_out = results_df.to_csv(index=False)
        st.download_button(
            "⬇ Download Scored Results CSV",
            data=csv_out,
            file_name="sentinel_scored_batch.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.markdown(f"""
    <div style="background:{v_card};border:2px dashed {v_border};border-radius:14px;
                padding:3rem;text-align:center;margin-top:1rem;">
        <p style="font-size:2rem;margin:0 0 0.5rem 0;">📂</p>
        <p style="font-size:0.95rem;font-weight:700;color:{v_text};margin:0 0 0.3rem 0;">
            Upload a CSV to begin batch scoring
        </p>
        <p style="font-size:0.8rem;color:{v_muted};margin:0;">
            Use the sample template above to format your data correctly.
        </p>
    </div>
    """, unsafe_allow_html=True)

render_footer()
