"""
EMIPredict AI — Results page.
"""
import plotly.graph_objects as go
import streamlit as st
from utils import load_artifacts, predict, VERDICT_COPY, inject_background, nav_bar

st.set_page_config(page_title="EMIPredict AI — Results", page_icon="◆", layout="wide", initial_sidebar_state="collapsed")
art = load_artifacts()
inject_background()

st.markdown("""
<style>
.top { display:flex; justify-content:space-between; align-items:center; padding: 1rem 0 .6rem; }
.top h1 { font-size:1.7rem; margin:0; }

.verdict { border-radius:12px; padding:1.8rem 2rem; color:#fff; margin: 1rem 0 1.4rem; }
.v-eligible { background:#0F766E; }
.v-highrisk { background:#B9772E; }
.v-noteligible { background:#A63A46; }
.verdict h2 { color:#fff; margin:0 0 .3rem; font-size:1.7rem; }
.verdict p { margin:0; opacity:.92; }

.metric-box { background:#FFFFFF; border:1px solid #E7E3D8; border-radius:10px; padding:1.1rem 1.3rem; }
.metric-box .label { color:#5B655F; font-size:.8rem; }
.metric-box .value { color:#1F2421; font-size:1.45rem; font-family:'Source Serif 4', serif; font-weight:700; }

.section-title { font-size:1.05rem; font-weight:600; color:#0F766E; margin:1.6rem 0 .7rem; }

div.stButton > button { background:#1F2421; color:#fff; border:none; border-radius:8px; padding:.55rem 1.2rem; font-weight:600;}
div.stButton > button:hover { background:#39423C; color:#fff; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="top"><h1>Assessment Result</h1></div>', unsafe_allow_html=True)
nav_bar("results")
st.write("")

if "applicant" not in st.session_state:
    st.warning("No applicant profile submitted yet.")
    if st.button("← Go to Applicant Form"):
        st.switch_page("app.py")
    st.stop()

if st.button("← Edit Applicant"):
    st.switch_page("app.py")

raw = st.session_state["applicant"]
result = predict(raw, art)
title, sub = VERDICT_COPY[result["label"]]
style = {"Eligible": "v-eligible", "High_Risk": "v-highrisk", "Not_Eligible": "v-noteligible"}[result["label"]]

st.markdown(f"""
<div class="verdict {style}"><h2>{title}</h2><p>{sub}</p></div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
conf = max(result["proba"].values()) * 100
dti = (raw["current_emi_amount"] / max(raw["monthly_salary"], 1)) * 100
for col, label, value in zip(
    (c1, c2, c3, c4),
    ("Recommended Max EMI", "Disposable Income", "Confidence", "Debt-to-Income"),
    (f"₹{result['max_emi']:,.0f}/mo", f"₹{result['disposable_income']:,.0f}/mo",
     f"{conf:.0f}%", f"{dti:.1f}%"),
):
    col.markdown(f'<div class="metric-box"><div class="label">{label}</div>'
                  f'<div class="value">{value}</div></div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="section-title">Eligibility Probability</div>', unsafe_allow_html=True)
    colors = {"Eligible": "#0F766E", "High_Risk": "#B9772E", "Not_Eligible": "#A63A46"}
    labels = [k.replace("_", " ") for k in result["proba"].keys()]
    values = list(result["proba"].values())
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=.58,
        marker=dict(colors=[colors[k] for k in result["proba"].keys()], line=dict(color="#FAF9F6", width=3)),
        textinfo="label+percent", textfont=dict(family="Inter", size=13),
    )])
    fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300,
                       annotations=[dict(text=title, x=0.5, y=0.5, font_size=18, showarrow=False)])
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown('<div class="section-title">Monthly Budget Breakdown</div>', unsafe_allow_html=True)
    items = ["Rent", "School Fees", "College Fees", "Travel", "Groceries/Utilities",
             "Other", "Current EMI", "Disposable"]
    amounts = [raw["monthly_rent"], raw["school_fees"], raw["college_fees"], raw["travel_expenses"],
               raw["groceries_utilities"], raw["other_monthly_expenses"], raw["current_emi_amount"],
               max(result["disposable_income"], 0)]
    bar_colors = ["#C9A227" if it != "Disposable" else "#0F766E" for it in items]
    fig2 = go.Figure(go.Bar(
        x=amounts, y=items, orientation="h", marker_color=bar_colors,
        text=[f"₹{a:,.0f}" for a in amounts], textposition="outside",
    ))
    fig2.update_layout(margin=dict(t=10, b=10, l=10, r=30), height=300,
                        xaxis_title=None, yaxis_title=None,
                        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig2, use_container_width=True)

with st.expander("Model performance (held-out test set)"):
    m = art["metrics"]
    st.write(f"**Classifier:** {m['classification']['best_model']} — "
             f"accuracy {m['classification']['test_accuracy']:.3f}, "
             f"macro-F1 {m['classification']['test_macro_f1']:.3f}")
    st.write(f"**Regressor:** {m['regression']['best_model']} — "
             f"R² {m['regression']['test_r2']:.3f}, "
             f"MAE ₹{m['regression']['test_mae']:.0f}")
