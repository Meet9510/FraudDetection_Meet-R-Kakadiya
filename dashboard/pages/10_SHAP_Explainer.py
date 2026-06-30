"""Sentinel AI — SHAP Explainer: user enters TransactionID and gets a SHAP waterfall + plain-English explanation."""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
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
    page_title="Sentinel AI — SHAP Explainer",
    page_icon="🧠",
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
        <h1>SHAP Explainer</h1>
        <p>Enter a TransactionID to see exactly which features drove the ML fraud decision — in plain English.</p>
    </div>
    <div class="saas-badge">
        <span class="status-dot"></span>
        Meet R Kakadiya
    </div>
</div>
""", unsafe_allow_html=True)

_loading_slot = st.empty()
with _loading_slot.container():
    render_skeleton_loading("Loading SHAP attribution engine…")
assets = load_dashboard_assets()
_loading_slot.empty()

if not assets:
    st.warning("⚠️ Model payload not found — place model.pkl in dashboard/")
    st.stop()

threshold    = st.session_state.custom_threshold
df           = assets['sample_txs'].copy()
shap_values  = assets['shap_values']
X_test_shap  = assets['X_test_shap']
le_map       = assets['label_encoders']

# Decode label-encoded columns for display
for col in ['card4', 'card6', 'P_emaildomain']:
    if col in df.columns and col in le_map:
        le = le_map[col]
        try:
            idxs = df[col].astype(int).clip(0, len(le.classes_) - 1)
            df[col] = [le.classes_[i] for i in idxs]
        except (ValueError, TypeError, KeyError):
            pass

shap_probs = assets['model'].predict_proba(X_test_shap)[:, 1]

# Map TransactionID → shap row index
shap_tx_ids = df['TransactionID'].values

# ── Quick-select preset cases ─────────────────────────────────
st.markdown(f"""
<p style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
          letter-spacing:0.1em;color:{primary};margin-bottom:0.5rem;">
    Quick-Select Notable Cases
</p>
""", unsafe_allow_html=True)

fraud_idx      = int(np.argmax(shap_probs))
legit_idx      = int(np.argmin(shap_probs))
borderline_idx = int(np.argmin(np.abs(shap_probs - 0.50)))

fraud_txid      = int(shap_tx_ids[fraud_idx])      if fraud_idx      < len(shap_tx_ids) else None
legit_txid      = int(shap_tx_ids[legit_idx])      if legit_idx      < len(shap_tx_ids) else None
borderline_txid = int(shap_tx_ids[borderline_idx]) if borderline_idx < len(shap_tx_ids) else None

q1, q2, q3 = st.columns(3)
for col, (label, txid, color, score) in zip([q1,q2,q3], [
    ("Highest Fraud Risk",  fraud_txid,      "#EF4444", shap_probs[fraud_idx]*100),
    ("Borderline Case",     borderline_txid, "#F59E0B", shap_probs[borderline_idx]*100),
    ("Legitimate (Lowest)", legit_txid,      "#10B981", shap_probs[legit_idx]*100),
]):
    with col:
        c_bg  = color + "12"
        c_bdr = color + "33"
        if st.button(
            f"{label}\nID: {txid} · {score:.1f}%",
            key=f"preset_{txid}",
            use_container_width=True
        ):
            st.session_state["shap_txid_input"] = str(txid)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── TransactionID input ───────────────────────────────────────
tx_input = st.text_input(
    "Enter TransactionID",
    value=st.session_state.get("shap_txid_input", ""),
    placeholder="e.g. 3089777",
    key="shap_txid_field"
)

if tx_input.strip():
    try:
        target_id = int(tx_input.strip())

        # Find in df
        tx_match = df[df['TransactionID'] == target_id]
        if len(tx_match) == 0:
            st.error(f"TransactionID {target_id} not found. Use IDs visible in Transaction Explorer.")
            st.stop()

        tx_row = tx_match.iloc[0]
        prob   = float(tx_row['Probability'])
        tier   = "Critical" if prob >= 0.75 else ("Suspicious" if prob >= threshold else "Clear")
        t_col  = "#EF4444" if tier == "Critical" else ("#F59E0B" if tier == "Suspicious" else "#10B981")
        t_bg   = t_col + "12"
        t_bdr  = t_col + "33"
        decision = "DECLINE" if prob >= 0.75 else ("MFA CHALLENGE" if prob >= threshold else "APPROVE")

        # Find shap index
        shap_match = np.where(shap_tx_ids == target_id)[0]
        if len(shap_match) == 0:
            # Fall back to card1-based mapping (same as Threat Simulator)
            shap_idx = int(tx_row['card1']) % len(X_test_shap)
        else:
            shap_idx = int(shap_match[0])

        st.markdown("---")

        # ── Transaction summary banner ────────────────────────
        b1, b2, b3, b4, b5 = st.columns(5)
        for col, (lbl, val, accent) in zip([b1,b2,b3,b4,b5], [
            ("TransactionID", f"#{target_id}",          primary),
            ("Amount",        f"${tx_row['TransactionAmt']:.2f}", v_text),
            ("Hour",          f"{int(tx_row['HourOfDay'])}:00",   v_text),
            ("Risk Score",    f"{prob*100:.1f}%",        t_col),
            ("Decision",      decision,                   t_col),
        ]):
            with col:
                st.markdown(f"""
                <div style="background:{v_card};border:1px solid {v_border};border-radius:10px;
                            padding:0.9rem 1rem;text-align:center;">
                    <p style="margin:0;font-size:0.6rem;font-weight:700;text-transform:uppercase;
                              letter-spacing:0.09em;color:{v_muted};">{lbl}</p>
                    <p style="margin:0.2rem 0 0;font-size:1rem;font-weight:900;color:{accent};
                              font-family:'JetBrains Mono',monospace;">{val}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

        # ── SHAP Waterfall ────────────────────────────────────
        st.markdown(f"""
        <h3 style="margin:0 0 0.3rem;font-size:1rem;font-weight:800;color:{v_text};">
            SHAP Feature Attribution Waterfall
        </h3>
        <p style="margin:0 0 0.75rem;font-size:0.78rem;color:{v_muted};">
            Each bar shows how much a feature pushed the score <b style="color:#EF4444;">up (fraud)</b>
            or <b style="color:#10B981;">down (legitimate)</b> from the baseline.
        </p>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            _, col_shap, _ = st.columns([0.5, 9, 0.5])
            with col_shap:
                fig_att = plt.figure(figsize=(10, 4))
                plt.clf()
                fig_att.patch.set_alpha(0.0)
                shap.plots.waterfall(shap_values[shap_idx], max_display=12, show=False)
                ax = plt.gca()
                ax.patch.set_alpha(0.0)
                ax.tick_params(axis='both', colors=THEME_VARS['text_muted'], labelsize=8)
                for spine in ax.spines.values():
                    spine.set_color(THEME_VARS['border_color_hex'])
                try:
                    for txt in ax.texts:
                        txt.set_fontsize(8)
                        txt.set_color(THEME_VARS['text_color'])
                except AttributeError:
                    pass
                st.pyplot(fig_att, bbox_inches='tight', clear_figure=True)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Plain-English Explanation ─────────────────────────
        st.markdown(f"""
        <h3 style="margin:0 0 0.75rem;font-size:1rem;font-weight:800;color:{v_text};">
            Plain-English Explanation
        </h3>
        """, unsafe_allow_html=True)

        # Build dynamic explanation from actual values
        amt       = tx_row['TransactionAmt']
        avg_amt   = df['TransactionAmt'].mean()
        hour      = int(tx_row['HourOfDay'])
        device    = int(tx_row.get('DeviceRisk', 0))
        email     = str(tx_row.get('P_emaildomain', ''))
        is_fraud  = int(tx_row['Actual'])
        amt_ratio = float(tx_row.get('AmtToMeanRatio', amt / avg_amt))

        # Identify top SHAP drivers
        sv = shap_values[shap_idx].values
        feature_names = X_test_shap.columns.tolist()
        top_pos = sorted(zip(sv, feature_names), reverse=True)[:3]
        top_neg = sorted(zip(sv, feature_names))[:3]

        risk_drivers = []
        risk_mitigators = []

        for val, name in top_pos:
            if val > 0.01:
                if 'Amt' in name or 'amt' in name.lower():
                    risk_drivers.append(f"transaction amount (${amt:.2f}, {amt_ratio:.1f}× the average)")
                elif 'Hour' in name:
                    risk_drivers.append(f"transaction time ({hour}:00 {'— late-night pattern' if hour in [0,1,2,3,4,22,23] else ''})")
                elif 'card1' in name:
                    risk_drivers.append(f"card issuer profile ({int(tx_row['card1'])})")
                elif 'Domain' in name or 'email' in name.lower():
                    risk_drivers.append(f"email domain ({email})")
                elif 'Device' in name:
                    risk_drivers.append(f"device risk flag ({'high' if device else 'low'})")
                else:
                    risk_drivers.append(f"{name} feature value")

        for val, name in top_neg:
            if val < -0.01:
                if 'Amt' in name or 'amt' in name.lower():
                    risk_mitigators.append("amount within normal range for this card")
                elif 'Hour' in name:
                    risk_mitigators.append("standard business-hours timing")
                elif 'card1' in name:
                    risk_mitigators.append("low-risk issuer history")
                else:
                    risk_mitigators.append(f"{name} within expected baseline")

        if tier == "Critical":
            verdict_text = f"This transaction was scored <b style='color:#EF4444;'>CRITICAL RISK ({prob*100:.1f}%)</b> and received an automated <b>DECLINE</b> directive."
            action_text = "The card has been flagged for immediate block. The fraud operations team has been notified for manual review."
        elif tier == "Suspicious":
            verdict_text = f"This transaction scored <b style='color:#F59E0B;'>SUSPICIOUS ({prob*100:.1f}%)</b> and triggered a <b>Multi-Factor Authentication challenge</b>."
            action_text = "The cardholder must verify via 3D-Secure OTP or biometric before the transaction proceeds."
        else:
            verdict_text = f"This transaction scored <b style='color:#10B981;'>CLEAR ({prob*100:.1f}%)</b> and received frictionless <b>APPROVAL</b>."
            action_text = "No additional verification was required. The transaction was authorized immediately."

        drivers_html = "".join([f"<li>{d}</li>" for d in risk_drivers[:3]]) if risk_drivers else "<li>No dominant fraud signals identified</li>"
        mitigators_html = "".join([f"<li>{m}</li>" for m in risk_mitigators[:3]]) if risk_mitigators else "<li>Standard baseline — no strong protective features</li>"
        ground_truth_color = "#EF4444" if is_fraud else "#10B981"
        ground_truth_label = "✓ CONFIRMED FRAUD" if is_fraud else "✓ LEGITIMATE"

        st.markdown(f"""
<div style="background:{v_card};border:1px solid {v_border};border-radius:14px;padding:1.5rem 1.75rem;">
<p style="margin:0 0 0.75rem;font-size:0.9rem;line-height:1.7;color:{v_text};">
{verdict_text}
</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.25rem;margin-bottom:1rem;">
<div style="background:{t_bg};border:1px solid {t_bdr};border-radius:10px;padding:1rem;">
<p style="margin:0 0 0.4rem;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:{t_col};">Risk Drivers (pushed score UP)</p>
<ul style="margin:0;padding-left:1.2rem;font-size:0.8rem;color:{v_text};line-height:1.8;">
{drivers_html}
</ul>
</div>
<div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);border-radius:10px;padding:1rem;">
<p style="margin:0 0 0.4rem;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#10B981;">Mitigating Factors (pushed score DOWN)</p>
<ul style="margin:0;padding-left:1.2rem;font-size:0.8rem;color:{v_text};line-height:1.8;">
{mitigators_html}
</ul>
</div>
</div>
<p style="margin:0 0 0.5rem;font-size:0.82rem;color:{v_muted};line-height:1.6;">
<b>Action Taken:</b> {action_text}
</p>
<div style="display:flex;justify-content:space-between;align-items:center;padding-top:0.75rem;border-top:1px solid {v_border};">
<span style="font-size:0.72rem;color:{v_muted};">Ground Truth (Actual Label)</span>
<span style="font-weight:800;color:{ground_truth_color};font-size:0.82rem;">{ground_truth_label}</span>
</div>
</div>
""", unsafe_allow_html=True)

        # ── Top feature importance table ──────────────────────
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <h3 style="margin:0 0 0.5rem;font-size:1rem;font-weight:800;color:{v_text};">
            Top 10 Feature Contributions
        </h3>
        """, unsafe_allow_html=True)

        shap_df = pd.DataFrame({
            'Feature': feature_names,
            'SHAP Value': sv,
            'Direction': ['↑ Fraud Risk' if v > 0 else '↓ Reduces Risk' for v in sv]
        }).reindex(np.argsort(np.abs(sv))[::-1]).head(10).reset_index(drop=True)
        shap_df['SHAP Value'] = shap_df['SHAP Value'].round(5)
        shap_df.index = shap_df.index + 1

        st.dataframe(
            shap_df.style.background_gradient(subset=['SHAP Value'], cmap='RdYlGn'),
            use_container_width=True,
            height=320,
            hide_index=False
        )

    except ValueError:
        st.error("Please enter a valid numeric TransactionID.")
else:
    st.markdown(f"""
    <div style="background:{v_card};border:2px dashed {v_border};border-radius:14px;
                padding:3rem;text-align:center;margin-top:1rem;">
        <p style="font-size:2rem;margin:0 0 0.5rem;">🧠</p>
        <p style="font-size:0.95rem;font-weight:700;color:{v_text};margin:0 0 0.3rem;">
            Enter a TransactionID above or click a preset case
        </p>
        <p style="font-size:0.8rem;color:{v_muted};margin:0;">
            SHAP waterfall + plain-English explanation will appear here.
            Available IDs: see Transaction Explorer page.
        </p>
    </div>
    """, unsafe_allow_html=True)

render_footer()
