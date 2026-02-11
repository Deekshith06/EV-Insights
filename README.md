# 🔋 EV Range Estimation & Insights Dashboard

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![ML](https://img.shields.io/badge/ML-Random_Forest-green?style=flat-square&logo=scikit-learn)
![Data](https://img.shields.io/badge/Records-177K+-orange?style=flat-square)

A data-driven platform analyzing **177,000+ electric vehicle records** from Washington State to provide ML-powered range estimation, adoption analytics, and interactive insights. Built for EV buyers, researchers, and enthusiasts.

---

## 🔄 How It Works

```
What it does:

177K+ vehicle records → Feature extraction & preprocessing
Multi-factor ML analysis → Range prediction (R² = 0.986)
Interactive dashboard → Real-time charts + filtered insights
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **ML Range Estimation** | Random Forest model predicts EV range with 98.6% accuracy (MAE: 5.2 mi) |
| **Dynamic Model Selection** | Cascading Make → Model dropdown filters by manufacturer |
| **Interactive Dashboard** | 4 metric cards + 4 responsive charts with sidebar filters |
| **Smart Filtering** | Filter by manufacturer, model year, and vehicle type with empty-state handling |
| **Feature Importance** | Visualize which factors (year, make, type) affect EV range most |
| **177K+ Records** | Complete Washington State DOL EV population dataset |

---

## 🚀 Quick Start

### Installation

```bash
# Clone and setup
git clone https://github.com/Deekshith06/EV-Range-Estimation-Insights-Dashboard.git
cd EV-Range-Estimation-Insights-Dashboard

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dataset

Download the [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data) and place `Electric_Vehicle_Population_Data.csv` in the project root.

### Usage

```bash
# Run the dashboard
streamlit run app.py
```

Access the app at **http://localhost:8501**

---

## 📂 Project Structure

```
├── app.py                 # Entry point + unified dark theme
├── data_loader.py         # Data loading & preprocessing
├── pages/
│   ├── home.py            # Dashboard with charts & filters
│   └── predictions.py     # ML range estimation model
├── requirements.txt       # Dependencies
├── .gitignore
└── README.md
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.8+ |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Plotly, Streamlit |
| **Machine Learning** | Scikit-learn (Random Forest) |
| **Encoding** | LabelEncoder for categorical features |

---

## 📊 Dataset Information

| Property | Value |
|----------|-------|
| **Source** | Washington State Department of Licensing |
| **Total Records** | 177,866 |
| **Training Samples** | 85,916 (with known range) |
| **Manufacturers** | 40+ |
| **Models** | 139 unique |
| **Time Range** | 1997–2024 |

---

## 🎯 ML Range Estimation

```python
Model: RandomForestRegressor(n_estimators=100, max_depth=15)

Features:
  → Model Year (numeric)
  → Manufacturer (label encoded, 40 classes)
  → Vehicle Type (BEV / PHEV)

Target: Electric Range (miles)
```

### Model Performance

| Metric | Value |
|--------|-------|
| **R² Score** | 0.986 |
| **Mean Absolute Error** | 5.2 miles |
| **Training Split** | 80/20 |

### Feature Importance

| Feature | Importance |
|---------|------------|
| Vehicle Type (BEV vs PHEV) | ~70% |
| Model Year | ~18% |
| Manufacturer | ~12% |

---

## 📈 Dashboard Analytics

### Home Page
- **Total Vehicles** — Filtered count of registered EVs
- **Avg Range** — Mean electric range across filtered data
- **Type Distribution** — BEV vs PHEV donut chart
- **Top Manufacturers/Models** — Dynamically switches when brand is selected
- **Registrations by Year** — Adoption trend line chart
- **Range Distribution** — Histogram of range values

### Range Estimation Page
- **Model Performance** — R², MAE, algorithm info
- **Prediction Form** — Select make, model, year, type → get predicted range
- **Comparison** — Shows predicted vs actual average range for that model
- **Feature Importance** — What drives range differences
- **Range Trends** — Average range evolution by year

---

## 🎓 Use Cases

**For EV Buyers:**
- Predict range for specific make/model combinations
- Compare predicted vs actual ranges across manufacturers

**For Researchers:**
- Analyze EV adoption trends by year
- Study range improvements across vehicle generations

**For Students:**
- Learn ML pipeline: data loading → encoding → training → evaluation
- Understand RandomForest for regression problems

---

## 🛠️ Future Scope

- [ ] Add weather/temperature impact on range
- [ ] Integrate charging station data
- [ ] Multi-state dataset expansion
- [ ] LSTM models for time-series forecasting
- [ ] Deploy to Streamlit Cloud

---

## 👤 Author

**Seelaboyina Deekshith**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Deekshith06)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/deekshith030206)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:seelaboyinadeekshith@gmail.com)

---

> ⭐ **Star this repo if it helped you!**
>
> Building the future of sustainable transportation 🚗⚡
