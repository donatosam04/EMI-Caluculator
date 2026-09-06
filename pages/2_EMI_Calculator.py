"""
EMIPredict AI — Quick EMI Calculator.
A standard loan-amortization calculator (principal, rate, tenure -> EMI),
inspired by emicalculator.net: live sliders, instant recompute, pie chart
of principal vs interest, and a year-wise payment schedule chart.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from utils import inject_background, nav_bar

st.set_page_config(page_title="EMIPredict AI — EMI Calculator", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")
inject_background()

st.markdown("""
<style>
.top { padding: 1rem 0 .6rem; }
.top h1 { font-size:1.7rem; margin:0; }
.metric-box { background:#FFFFFF; border:1px solid #E7E3D8; border-radius:10px; padding:1.1rem 1.3rem; text-align:center; }
.metric-box .label { color:#5B655F; font-size:.82rem; }
.metric-box .value { color:#1F2421; font-size:1.6rem; font-family:'Source Serif 4', serif; font-weight:700; margin-top:.2rem;}
.section-title { font-size:1.05rem; font-weight:600; color:#0F766E; margin:1.6rem 0 .7rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="top"><h1>Quick EMI Calculator</h1></div>', unsafe_allow_html=True)
nav_bar("calculator")
st.write("")

with st.container(border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        principal = st.slider("Loan Amount (₹)", 50_000, 10_000_000, 1_000_000, step=25_000)
    with c2:
        rate = st.slider("Interest Rate (% p.a.)", 5.0, 20.0, 10.5, step=0.1)
    with c3:
        tenure_years = st.slider("Loan Tenure (years)", 1, 30, 10)

tenure_months = tenure_years * 12
r = rate / 12 / 100

if r > 0:
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
else:
    emi = principal / tenure_months

total_payment = emi * tenure_months
total_interest = total_payment - principal

st.write("")
m1, m2, m3 = st.columns(3)
m1.markdown(f'<div class="metric-box"><div class="label">Loan EMI</div><div class="value">₹{emi:,.0f}</div></div>', unsafe_allow_html=True)
m2.markdown(f'<div class="metric-box"><div class="label">Total Interest Payable</div><div class="value">₹{total_interest:,.0f}</div></div>', unsafe_allow_html=True)
m3.markdown(f'<div class="metric-box"><div class="label">Total Payment</div><div class="value">₹{total_payment:,.0f}</div></div>', unsafe_allow_html=True)

st.write("")
left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="section-title">Principal vs Interest</div>', unsafe_allow_html=True)
    fig = go.Figure(data=[go.Pie(
        labels=["Principal", "Interest"], values=[principal, total_interest], hole=.58,
        marker=dict(colors=["#0F766E", "#C9A227"], line=dict(color="#FAF9F6", width=3)),
        textinfo="label+percent",
    )])
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Year-wise Payment Schedule</div>', unsafe_allow_html=True)
    balance = principal
    rows = []
    for year in range(1, tenure_years + 1):
        year_principal = 0.0
        year_interest = 0.0
        for _ in range(12):
            if balance <= 0:
                break
            interest_part = balance * r
            principal_part = emi - interest_part
            balance -= principal_part
            year_principal += principal_part
            year_interest += interest_part
        rows.append({"Year": year, "Principal": max(year_principal, 0), "Interest": max(year_interest, 0)})
    sched = pd.DataFrame(rows)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=sched["Year"], y=sched["Principal"], name="Principal", marker_color="#0F766E"))
    fig2.add_trace(go.Bar(x=sched["Year"], y=sched["Interest"], name="Interest", marker_color="#C9A227"))
    fig2.update_layout(barmode="stack", margin=dict(t=10, b=10, l=10, r=10), height=300,
                        legend=dict(orientation="h", yanchor="bottom", y=1.02),
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

st.caption("Standard reducing-balance EMI formula — independent of the ML risk model on the other pages. "
           "Use this to sanity-check requested EMI amounts against a real interest rate and tenure.")
