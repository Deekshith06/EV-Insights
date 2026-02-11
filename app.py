import streamlit as st

# page setup
st.set_page_config(
    page_title="EV Range Estimation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# simple dark theme - defined once, used everywhere
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body, [data-testid="stAppViewContainer"] {
    background: #0d1117 !important;
    color: #f0f6fc !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #161b22, #0d1117) !important;
    border-right: 1px solid #30363d;
}

h1 {
    background: linear-gradient(135deg, #58a6ff, #a371f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

h2, h3 { color: #f0f6fc !important; font-weight: 600 !important; }
p, span, label { color: #8b949e !important; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #21262d, #161b22) !important;
    border: 1px solid #30363d !important;
    border-radius: 14px !important;
    padding: 1.2rem !important;
}

[data-testid="stMetricValue"] { color: #f0f6fc !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; }

.stButton > button {
    background: linear-gradient(135deg, #238636, #2ea043) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}

.js-plotly-plot {
    border-radius: 14px !important;
    border: 1px solid #30363d;
}

hr {
    background: linear-gradient(90deg, transparent, #30363d, transparent) !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)


# navigation
home = st.Page("pages/home.py", title="Dashboard")
predictions = st.Page("pages/predictions.py", title="Range Estimation")

nav = st.navigation([home, predictions])
nav.run()
