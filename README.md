# EMIPredict AI

**Financial risk assessment platform** that predicts EMI (loan) eligibility and the affordable monthly payment for an applicant, built as a full ML pipeline with an interactive Streamlit dashboard.

> Predicts **EMI Eligibility** (Eligible / High Risk / Not Eligible) and **Recommended Max Monthly EMI** from a 25-field applicant profile across 5 loan scenarios — e-commerce, home appliances, vehicle, personal loan, and education EMIs.

---

## Features

- **Two ML models** — a classifier for EMI eligibility and a regressor for the affordable monthly EMI, each selected as the best of 3 candidate algorithms on held-out test data
- **Multi-page interactive app** — a guided applicant intake form, a results dashboard with probability and budget-breakdown charts, and a standalone reducing-balance EMI calculator
- **Full pipeline included** — data generation/cleaning, EDA, feature engineering, model training, and the serving app are all in this repo
- **Explainable outputs** — eligibility probability breakdown, disposable income, debt-to-income ratio, and a monthly budget chart alongside every prediction

## Model Performance

| Task | Best Model | Metric |
|---|---|---|
| EMI Eligibility (classification) | Gradient Boosting Classifier | 88.3% accuracy · 0.80 macro-F1 |
| Max Monthly EMI (regression) | Gradient Boosting Regressor | R² 0.97 · MAE ≈ ₹1,430/month |

Each was chosen from 3 candidates (Logistic/Linear Regression, Random Forest, Gradient Boosting) evaluated on a held-out test split.

## Project Structure

```
emipredict-ai/
├── app.py                     # Applicant intake form (home page)
├── utils.py                   # Shared model loading + prediction logic
├── requirements.txt
├── .streamlit/config.toml     # App theme
├── pages/
│   ├── 1_Results.py           # Prediction results dashboard
│   └── 2_EMI_Calculator.py    # Standalone reducing-balance EMI calculator
├── models/                    # Trained model artifacts (pkl) + metrics.json
├── scripts/                   # Data pipeline (generation → cleaning → EDA → training)
│   ├── generate_data.py
│   ├── preprocess.py
│   ├── eda.py
│   └── train_models.py
├── charts/                    # EDA visualizations
├── reports/                   # Preprocessing & EDA write-ups
└── data/                      # Cleaned dataset + train/val/test splits
```

## Getting Started

### Prerequisites
- Python 3.12

### Installation

```bash
git clone https://github.com/<your-username>/emipredict-ai.git
cd emipredict-ai

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`.

### Re-run the training pipeline (optional)

Only needed if you want to retrain on new/real data:

```bash
python scripts/preprocess.py      # clean data, create train/val/test splits
python scripts/eda.py             # generate EDA charts + report
python scripts/train_models.py    # train & save classifier + regressor
```

## How It Works

1. **Input** — the applicant form on the home page collects 25 fields: demographics, income, employment, household expenses, credit profile, and the requested EMI details.
2. **Feature engineering** — six derived features are computed on the fly (disposable income, affordability ratio, debt-to-income, savings-to-income, dependent burden, requested-to-income ratio).
3. **Prediction** — the same feature vector is scored by both the classifier and the regressor.
4. **Output** — the Results page shows the eligibility verdict, confidence, recommended max EMI, disposable income, and visual breakdowns.

## Dataset

Model training used a synthetically generated dataset (400,000 records) built to match a 22-feature / 5-scenario specification, since the original dataset was not accessible from the development environment. The generation script (`scripts/generate_data.py`) is included — swap in a real dataset with matching column names and re-run the pipeline with no code changes required.

## Tech Stack

- **ML**: scikit-learn (Gradient Boosting, Random Forest, Logistic/Linear Regression)
- **App**: Streamlit, Plotly
- **Data**: pandas, NumPy

## License

This project was built as part of an academic capstone. Feel free to fork and adapt for learning purposes.
