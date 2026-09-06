"""
Shared artifact loading + prediction logic used by both pages of the app.
"""
import json
import joblib
import pandas as pd
import streamlit as st

MODELS = "models"

CAT_ORDER = ["gender", "marital_status", "education", "employment_type",
             "company_type", "house_type", "existing_loans", "emi_scenario"]

VERDICT_COPY = {
    "Eligible": ("Eligible", "This applicant meets EMI eligibility criteria."),
    "High_Risk": ("High Risk", "Eligible with caution — affordability margin is thin."),
    "Not_Eligible": ("Not Eligible", "Current profile does not support this EMI request."),
}

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@600;700&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Source Serif 4', serif; }
#MainMenu, header, footer { visibility: hidden; }

/* --- animated depth background --- */
.stApp { background: transparent !important; }
body { background: #FAF9F6 !important; }
.bg-orbs { position: fixed; inset: 0; z-index: 0; overflow: hidden; pointer-events: none; }
.orb { position: absolute; border-radius: 50%; filter: blur(60px); opacity: .5; }
.orb1 { width: 460px; height: 460px; background: #0F766E; top: -140px; left: -110px;
        animation: drift1 22s ease-in-out infinite; }
.orb2 { width: 400px; height: 400px; background: #C9A227; bottom: -160px; right: -90px;
        animation: drift2 26s ease-in-out infinite; }
.orb3 { width: 340px; height: 340px; background: #A63A46; top: 35%; right: 12%;
        animation: drift3 30s ease-in-out infinite; opacity: .3; }
@keyframes drift1 { 0%,100%{transform:translate(0,0) scale(1);} 50%{transform:translate(60px,40px) scale(1.1);} }
@keyframes drift2 { 0%,100%{transform:translate(0,0) scale(1);} 50%{transform:translate(-50px,-30px) scale(1.15);} }
@keyframes drift3 { 0%,100%{transform:translate(0,0) scale(1);} 50%{transform:translate(-40px,50px) scale(.9);} }

.nav-bar { display:flex; gap:.4rem; justify-content:center; margin: 0 0 .6rem; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,.92); backdrop-filter: blur(6px);
    border-radius: 10px; border: 1px solid #E7E3D8 !important; padding: .4rem .4rem;
    position: relative; z-index: 1;
}
div[data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
</style>
<div class="bg-orbs"><div class="orb orb1"></div><div class="orb orb2"></div><div class="orb orb3"></div></div>
"""


def inject_background():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def nav_bar(active: str):
    """active: one of 'home', 'results', 'calculator'"""
    cols = st.columns(3)
    labels = [("app.py", "🏠 Applicant Form", "home"),
              ("pages/1_Results.py", "📊 Results", "results"),
              ("pages/2_EMI_Calculator.py", "🧮 EMI Calculator", "calculator")]
    for col, (target, label, key) in zip(cols, labels):
        with col:
            st.page_link(target, label=label, use_container_width=True,
                         disabled=(key == active))


@st.cache_resource
def load_artifacts():
    return {
        "classifier": joblib.load(f"{MODELS}/classifier.pkl"),
        "regressor": joblib.load(f"{MODELS}/regressor.pkl"),
        "scaler": joblib.load(f"{MODELS}/scaler.pkl"),
        "encoders": joblib.load(f"{MODELS}/encoders.pkl"),
        "target_encoder": joblib.load(f"{MODELS}/target_encoder.pkl"),
        "features": joblib.load(f"{MODELS}/feature_list.pkl"),
        "metrics": json.load(open(f"{MODELS}/metrics.json")),
    }


def engineer(raw: dict) -> dict:
    total_expenses = (
        raw["monthly_rent"] + raw["school_fees"] + raw["college_fees"]
        + raw["travel_expenses"] + raw["groceries_utilities"]
        + raw["other_monthly_expenses"] + raw["current_emi_amount"]
    )
    disposable_income = raw["monthly_salary"] - total_expenses
    return {
        **raw,
        "disposable_income": disposable_income,
        "affordability_ratio": disposable_income / max(raw["monthly_salary"], 1),
        "debt_to_income": raw["current_emi_amount"] / max(raw["monthly_salary"], 1),
        "savings_to_income": raw["bank_balance"] / max(raw["monthly_salary"], 1),
        "dependent_burden": raw["dependents"] + (raw["school_fees"] + raw["college_fees"]) / 5000,
        "requested_to_income": raw["requested_amount"] / max(raw["monthly_salary"] * raw["requested_tenure"], 1),
    }


def predict(raw: dict, art: dict):
    """raw: dict of the applicant's form inputs (before feature engineering)."""
    enriched = engineer(raw)
    df_row = pd.DataFrame([enriched])
    for col, le in art["encoders"].items():
        df_row[col] = le.transform(df_row[col])
    X = art["scaler"].transform(df_row[art["features"]])

    pred_class = art["classifier"].predict(X)[0]
    pred_label = art["target_encoder"].inverse_transform([pred_class])[0]
    pred_proba = art["classifier"].predict_proba(X)[0]
    pred_emi = float(art["regressor"].predict(X)[0])

    return {
        "label": pred_label,
        "proba": dict(zip(art["target_encoder"].classes_, pred_proba)),
        "max_emi": pred_emi,
        "disposable_income": enriched["disposable_income"],
    }