"""
EMIPredict AI — Home / Applicant Input page.
Run with: streamlit run app.py
"""
import streamlit as st
from utils import load_artifacts, inject_background, nav_bar

st.set_page_config(page_title="EMIPredict AI", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")
art = load_artifacts()
inject_background()

st.markdown("""
<style>
.hero { text-align: center; padding: 1.6rem 1rem 1.2rem; }
.hero .tag { display:inline-block; background:#E4F0EC; color:#0F766E; font-size:.78rem;
             font-weight:600; letter-spacing:.04em; padding:.3rem .8rem; border-radius:99px; margin-bottom:.9rem;}
.hero h1 { font-size:2.4rem; color:#1F2421; margin:0; }
.hero p { color:#5B655F; font-size:1.02rem; margin:.5rem 0 0; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background:#FFFFFF; border-radius:10px; border:1px solid #E7E3D8 !important;
    padding: .4rem .4rem;
}
.grp-title { font-size:1.02rem; font-weight:600; color:#0F766E; margin: 0 0 .7rem 2px; }

div.stButton > button {
    background:#0F766E; color:#fff; border:none; border-radius:8px;
    padding:.7rem 1.4rem; font-weight:600; font-size:1.02rem;
}
div.stButton > button:hover { background:#0B5C55; color:#fff; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <span class="tag">FINANCIAL RISK ASSESSMENT</span>
  <h1>EMIPredict AI</h1>
  <p>Tell us about the applicant — we'll assess EMI eligibility and the affordable monthly payment.</p>
</div>
""", unsafe_allow_html=True)

nav_bar("home")
st.write("")

_, mid, _ = st.columns([1, 8, 1])
with mid:
    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            st.markdown('<div class="grp-title">Applicant</div>', unsafe_allow_html=True)
            scenario = st.selectbox("EMI Scenario", list(art["encoders"]["emi_scenario"].classes_))
            a, b = st.columns(2)
            age = a.slider("Age", 21, 65, 32)
            gender = b.selectbox("Gender", list(art["encoders"]["gender"].classes_))
            c, d = st.columns(2)
            marital_status = c.selectbox("Marital Status", list(art["encoders"]["marital_status"].classes_))
            education = d.selectbox("Education", list(art["encoders"]["education"].classes_))

        st.write("")
        with st.container(border=True):
            st.markdown('<div class="grp-title">Income & Employment</div>', unsafe_allow_html=True)
            monthly_salary = st.slider("Monthly Salary (₹)", 10000, 300000, 55000, step=1000)
            e, f = st.columns(2)
            employment_type = e.selectbox("Employment Type", list(art["encoders"]["employment_type"].classes_))
            company_type = f.selectbox("Company Type", list(art["encoders"]["company_type"].classes_))
            years_of_employment = st.slider("Years of Employment", 0, 40, 5)

        st.write("")
        with st.container(border=True):
            st.markdown('<div class="grp-title">Requested EMI</div>', unsafe_allow_html=True)
            requested_amount = st.slider("Requested Amount (₹)", 5000, 2_000_000, 150000, step=5000)
            requested_tenure = st.slider("Requested Tenure (months)", 3, 84, 24)

    with col2:
        with st.container(border=True):
            st.markdown('<div class="grp-title">Household & Expenses</div>', unsafe_allow_html=True)
            g, h = st.columns(2)
            house_type = g.selectbox("Housing", list(art["encoders"]["house_type"].classes_))
            monthly_rent = h.slider("Monthly Rent (₹)", 0, 100000, 10000, step=500)
            i, j = st.columns(2)
            family_size = i.slider("Family Size", 1, 10, 3)
            dependents = j.slider("Dependents", 0, 6, 1)
            school_fees = st.slider("School Fees (₹/mo)", 0, 50000, 0, step=500)
            college_fees = st.slider("College Fees (₹/mo)", 0, 80000, 0, step=500)
            k, l = st.columns(2)
            travel_expenses = k.slider("Travel (₹/mo)", 0, 30000, 3000, step=500)
            groceries_utilities = l.slider("Groceries/Utilities (₹/mo)", 0, 50000, 8000, step=500)
            other_monthly_expenses = st.slider("Other Expenses (₹/mo)", 0, 50000, 2000, step=500)

        st.write("")
        with st.container(border=True):
            st.markdown('<div class="grp-title">Credit & Savings</div>', unsafe_allow_html=True)
            m, n = st.columns(2)
            existing_loans = m.selectbox("Existing Loans", list(art["encoders"]["existing_loans"].classes_))
            current_emi_amount = n.slider("Current EMI (₹/mo)", 0, 100000, 0, step=500)
            credit_score = st.slider("Credit Score", 300, 850, 700)
            o, p = st.columns(2)
            bank_balance = o.slider("Bank Balance (₹)", 0, 5_000_000, 80000, step=5000)
            emergency_fund = p.slider("Emergency Fund (₹)", 0, 2_000_000, 40000, step=5000)

    st.write("")
    left, right = st.columns([5, 2])
    with right:
        submit = st.button("Assess Application →", use_container_width=True)

if submit:
    st.session_state["applicant"] = {
        "age": age, "gender": gender, "marital_status": marital_status, "education": education,
        "monthly_salary": monthly_salary, "employment_type": employment_type,
        "years_of_employment": years_of_employment, "company_type": company_type,
        "house_type": house_type, "monthly_rent": monthly_rent, "family_size": family_size,
        "dependents": dependents, "school_fees": school_fees, "college_fees": college_fees,
        "travel_expenses": travel_expenses, "groceries_utilities": groceries_utilities,
        "other_monthly_expenses": other_monthly_expenses, "existing_loans": existing_loans,
        "current_emi_amount": current_emi_amount, "credit_score": credit_score,
        "bank_balance": bank_balance, "emergency_fund": emergency_fund, "emi_scenario": scenario,
        "requested_amount": requested_amount, "requested_tenure": requested_tenure,
    }
    st.switch_page("pages/1_Results.py")
