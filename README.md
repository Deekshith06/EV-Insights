# EV Range Estimation Dashboard

Predict electric vehicle battery range using machine learning, and explore EV adoption trends across Washington State.

## Features

- **Range Estimation** — Random Forest model predicts EV range from manufacturer, model year, and vehicle type
- **Dashboard** — Interactive charts showing EV adoption trends, type distribution, and top manufacturers
- **Filters** — Filter by manufacturer, year range, and vehicle type

## Tech Stack

Python · Pandas · Scikit-learn · Streamlit · Plotly

## Setup

```bash
git clone https://github.com/Deekshith06/EV-Range-Estimation-Insights-Dashboard.git
cd EV-Range-Estimation-Insights-Dashboard

python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

## Dataset

Download the [Electric Vehicle Population Data](https://catalog.data.gov/dataset/electric-vehicle-population-data) and place `Electric_Vehicle_Population_Data.csv` in the project root.

## Run

```bash
streamlit run app.py
```

## Project Structure

```
├── app.py               # Entry point + theme
├── data_loader.py        # Data loading and cleanup
├── pages/
│   ├── home.py           # Dashboard with charts and filters
│   └── predictions.py    # ML range estimation model
├── requirements.txt
└── README.md
```

## How It Works

1. Loads 177K+ EV registration records from Washington State DOL
2. Trains a Random Forest model on vehicle specs to predict electric range
3. Shows model accuracy (R² score, MAE) and feature importance
4. Users can input vehicle details and get predicted range

## Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/deekshith030206)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Deekshith06)
