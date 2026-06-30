# Sentinel AI — Fraud Detection Intelligence Platform

> **IEEE-CIS Credit Card Fraud Detection · End-to-End ML Pipeline · Enterprise Dashboard**  
> Author: **Meet R Kakadiya** | Role: Machine Learning Intern | Year: 2026

---

## What Is This Project?

**Sentinel AI** is a production-grade, real-time **Credit Card Fraud Detection System** built on the IEEE-CIS Kaggle dataset. It trains a LightGBM classifier to detect fraudulent financial transactions with high precision and recall, then exposes a live, interactive **Streamlit dashboard** — styled like a real SaaS security product — where analysts can monitor threats, simulate scenarios, tune risk policies, and audit ledger entries.

### Real-World Analogy

Imagine you're shopping online and you tap "Pay Now" for a $1,800 item at 3 AM using a foreign credit card. Behind the scenes:

1. Your payment processor sends the transaction details (amount, card type, email domain, hour) to a fraud engine.
2. The fraud engine — powered by a ML model like ours — scores the transaction in **under 15ms**.
3. If the score is high (e.g., 82% fraud probability), the engine automatically **declines** the transaction or triggers an **OTP/MFA challenge**.
4. The analyst dashboard logs the event, shows the risk breakdown (SHAP attribution), and records it for compliance audit.

**This is exactly what Sentinel AI does** — simulating a real fraud-intelligence system at every layer.

---

## Project Structure

```text
FraudDetection_Meet R Kakadiya/
├── index.html                  # Marketing/landing page (open in browser)
├── dashboard/
│   ├── app.py                  # Streamlit app entry point
│   ├── model.pkl               # Trained LightGBM payload (model + scaler + SHAP)
│   ├── theme.py                # Global CSS injection, sidebar, and asset loader
│   └── pages/
│       ├── 1_Command_Center_Hub.py     # Live alert queue + risk scatter map
│       ├── 2_Threat_Simulator_Lab.py   # Interactive transaction scoring + SHAP
│       ├── 3_Risk_Policy_Optimizer.py  # Threshold tuning + cost curve analysis
│       ├── 4_SMOTE_&_AI_Science.py     # Model benchmarks + feature engineering
│       └── 5_Audit_Compliance_Ledger.py # Searchable, exportable transaction log
├── data/
│   ├── train_transaction.csv   # ~590K transaction records
│   └── train_identity.csv      # ~144K identity/device records
├── analysis.ipynb              # Full data science pipeline notebook
├── model_comparison.png        # Benchmarking chart (root copy)
├── shap_summary.png            # Global SHAP importance chart
├── requirements.txt            # Python dependencies
├── REPORT.md                   # Project report (methodology, results, findings)
└── README.md                   # This file
```

---

## How to Start the Project

### Prerequisites
- Python 3.10 or higher
- pip (package manager)

### Step 1 — Clone / Navigate to project folder

```bash
cd "d:\Xylofy AI\FraudDetection_Meet R Kakadiya"
```

### Step 2 — Activate virtual environment

```bash
# Windows (PowerShell)
.venv\Scripts\activate

# If .venv doesn't exist, create one first:
python -m venv .venv
.venv\Scripts\activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `shap` and `lightgbm` may take 2–3 minutes to install. This is normal.

### Step 4 — Open the Landing Page (Optional)

Open `index.html` directly in any browser — no server needed:

```bash
start index.html
```

This shows the product marketing page with a **"Launch Console"** button that links to the dashboard at `http://localhost:8501`.

### Step 5 — Launch the Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will open automatically at **http://localhost:8501**

> **Tip:** Always run this from the **project root** directory, not from inside `dashboard/`.

### Step 6 — (Optional) Run the Jupyter Notebook

To re-run the full ML pipeline (training, evaluation, SHAP):

```bash
jupyter notebook analysis.ipynb
```

---

## How It Works — End-to-End Pipeline

```
Raw CSV Data
    │
    ▼
[Data Preprocessing]
  - Merge transaction + identity tables
  - Drop high-null columns (>50% missing)
  - Label-encode categoricals (card4, card6, P_emaildomain)
  - RobustScaler for numeric features
    │
    ▼
[Feature Engineering]
  - LogTransactionAmt      → compress skewed values
  - AmtToMeanRatio         → detect unusual spend size
  - HourOfDay              → time-of-day risk signal
  - DeviceRisk             → credit vs debit flag
  - EmailDomainRisk        → high-risk email providers
  - Card1AmtRatio          → issuer-level anomaly score
    │
    ▼
[Class Imbalance — SMOTE]
  - Only ~3.5% of rows are fraud
  - SMOTE generates synthetic fraud samples via k-NN interpolation
  - Result: balanced training set
    │
    ▼
[Model Training — LightGBM]
  - Optuna hyperparameter search (100 trials)
  - Trained on SMOTE-balanced, RobustScaler-scaled data
    │
    ▼
[Evaluation]
  - AUC-ROC, Precision, Recall, F1 on held-out test set
    │
    ▼
[SHAP Attribution]
  - TreeExplainer computes per-feature impact scores
  - Waterfall plots explain individual predictions
    │
    ▼
[Payload Export → model.pkl]
  - model, scaler, label_encoders, features list,
    sample_txs, X_test_shap, shap_values, performance metrics
    │
    ▼
[Streamlit Dashboard — 5 pages]
  - Command Center Hub      → live alert queue
  - Threat Simulator Lab    → manual transaction scoring
  - Risk Policy Optimizer   → threshold cost curves
  - SMOTE & AI Science      → model benchmarks
  - Audit Compliance Ledger → exportable transaction log
```

---

## Real-World Example Walkthrough

### Scenario: Late-Night High-Value Transaction

**Input at 3 AM:**
| Field | Value |
|-------|-------|
| Amount | $1,820.00 |
| Card Network | American Express |
| Funding Type | Credit |
| Email Domain | protonmail.com |
| Hour of Day | 3 |
| Card Issuer Code | 18200 |

**System Processing:**
1. `LogTransactionAmt = log(1821) = 7.51` → very high value
2. `AmtToMeanRatio = 1820 / 135 = 13.48` → 13× the average — extremely unusual
3. `EmailDomainRisk = 1` → protonmail is a high-risk domain
4. `HourOfDay = 3` → late-night carries elevated risk weight
5. `DeviceRisk = 1` → credit card has higher fraud correlation

**Model Output:**
```
Fraud Probability: 87.4%  →  CRITICAL — AUTOMATED DECLINE
```

**Policy Enforcement:**
- Score ≥ 75% → **Auto-Decline** → card block initiated, merchant notified
- Event logged to Audit Compliance Ledger

---

## Model Benchmarking Results

| Model | AUC-ROC | PR-AUC | Recall | Precision | F1-Score |
|-------|---------|--------|--------|-----------|----------|
| **LightGBM (Tuned via Optuna)** | **0.9787** | **0.8490** | **83.1%** | **86.7%** | **84.9%** |
| XGBoost Classifier | 0.8616 | 0.4970 | 40.0% | 67.7% | 50.3% |
| Isolation Forest (Unsupervised) | 0.7355 | 0.1149 | 5.2% | 16.7% | 7.9% |

**Why LightGBM?**
- Sub-15ms inference per transaction (real-time capable)
- Superior Optuna tuning stability vs XGBoost
- High recall (83%) → catches most actual fraud
- High precision (86.7%) → fewer false declines (customer friction)

---

## Risk Policy Framework

| Risk Score | Policy | Rationale |
|------------|--------|-----------|
| ≥ 75% | **Auto-Decline** | Imminent threat — card blocked immediately |
| 40%–74% | **MFA Challenge** | Suspicious — 3D-Secure / OTP verification |
| < 40% | **Auto-Approve** | Clear — frictionless checkout |

The **Risk Policy Optimizer** page lets you drag the threshold slider and see the real financial impact — how much fraud you block vs. how much customer friction you create.

---

## Known Issues Fixed

| # | Issue | Fix Applied |
|---|-------|------------|
| 1 | `ModuleNotFoundError: No module named 'dashboard'` in page files | All 5 page files now use `try/except` dual-import: `from theme import ...` first, fallback to `from dashboard.theme import ...` |
| 2 | Dashboard must be started from project root | README now explicitly states: run `streamlit run dashboard/app.py` from root |
| 3 | Landing page "Launch Console" link had no target | `href="http://localhost:8501"` with `target="_blank"` already present in `index.html` |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| Data | pandas, numpy |
| ML Models | LightGBM, XGBoost, Isolation Forest |
| Hyperparameter Search | Optuna |
| Class Balancing | imbalanced-learn (SMOTE) |
| Scaling | scikit-learn RobustScaler |
| Explainability | SHAP (SHapley Additive exPlanations) |
| Dashboard | Streamlit + Plotly |
| Visualizations | Matplotlib, Seaborn, Plotly Express |
| Serialization | joblib |
| Frontend (Landing) | Vanilla HTML + CSS |

---

## Author

**Meet R Kakadiya**  
Machine Learning Intern  
IEEE-CIS Fraud Detection Operational Integration — 2026
