# 🔋 EV Insights

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=flat-square&logo=streamlit)
![ML](https://img.shields.io/badge/ML-Random_Forest-green?style=flat-square&logo=scikit-learn)
![Data](https://img.shields.io/badge/Records-177K+-orange?style=flat-square)

ML-powered dashboard that predicts EV range and visualizes **177K+ electric vehicle records** from Washington State DOL. Random Forest model achieves **R² = 0.986** with **5.2 mile** average error.

---

**🌐 [Try it Live](https://ev-insights.streamlit.app/)** - No installation required

## 🔄 How It Works

```mermaid
graph TD
    subgraph Step 1: ML Training Pipeline
        A["Electric_Vehicle_Population_Data.csv"] -->|Read 177K records| B["data_loader.py"]
        B -->|Clean & filter| C["predictions.py"]
        C -->|Encode features| D{"Random Forest Model"}
        D -->|Train 80/20 split| E["R² = 0.986 | MAE = 5.2 mi"]
    end

    subgraph Step 2: User Prediction
        F["User selects Make"] -->|Filter| G["Car Model dropdown"]
        G --> H["Select Year & Type"]
        H -->|Encode inputs| D
        D -->|Predict| I["Estimated Range in miles"]
    end

    subgraph Step 3: Dashboard Analytics
        B -->|Load data| J["home.py"]
        J -->|Sidebar filters| K["Filtered Dataset"]
        K --> L["4 Metric Cards"]
        K --> M["4 Interactive Charts"]
    end
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/Deekshith06/EV-Range-Estimation-Insights-Dashboard.git
cd EV-Range-Estimation-Insights-Dashboard
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

> Download [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data) CSV into the project root before running.

---

## 📂 Project Structure

```
├── app.py              # Entry point + dark theme
├── data_loader.py      # Data loading & cleanup
├── pages/
│   ├── home.py         # Dashboard (filters, metrics, charts)
│   └── predictions.py  # ML range estimation
├── requirements.txt
└── .gitignore
```

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit, Plotly |
| ML Model | Scikit-learn (RandomForest) |
| Data | Pandas, NumPy |

---

## 📊 Model Performance

| Metric | Value |
|--------|-------|
| R² Score | 0.986 |
| MAE | 5.2 miles |
| Features | Model Year, Make, Vehicle Type |
| Training Data | 85K+ records |

---

## 👤 Author

**Seelaboyina Deekshith**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Deekshith06)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/deekshith030206)
[![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:seelaboyinadeekshith@gmail.com)

---

> ⭐ Star this repo if it helped you!
