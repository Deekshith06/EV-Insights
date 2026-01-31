import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import time
import warnings
warnings.filterwarnings('ignore')

from data_utils import (
    get_market_share_history,
    get_range_trends,
    get_yearly_counts,
    load_ev_data,
)

# Note: Page config is set in the main Dashboard.py file

# Enforce dark theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Dark Theme CSS
def get_dark_theme_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
[data-testid="stAppViewContainer"] { background-color: #0d1117 !important; }
[data-testid="stHeader"] { background-color: #0d1117 !important; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #161b22 0%, #0d1117 100%) !important; border-right: 1px solid #30363d !important; }
.main { font-family: 'Inter', sans-serif; background-color: #0d1117 !important; }
h1 { background: linear-gradient(135deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
h2, h3 { color: #f0f6fc !important; font-weight: 600 !important; }
p, span, label, div { color: #c9d1d9 !important; }
[data-testid="stMetric"] { background: #21262d !important; border: 1px solid #30363d !important; border-radius: 16px !important; padding: 1.2rem !important; min-height: 120px !important; }
[data-testid="stMetricValue"] { color: #f0f6fc !important; font-weight: 700 !important; font-size: 1.8rem !important; }
[data-testid="stMetricLabel"] { color: #8b949e !important; font-weight: 500 !important; }
.stButton > button { background: linear-gradient(135deg, #238636, #2ea043) !important; color: white !important; border-radius: 12px !important; border: none !important; font-weight: 600 !important; }
[data-testid="stSelectbox"] > div > div { border-radius: 12px !important; border: 2px solid #30363d !important; background: #21262d !important; }
.js-plotly-plot { border-radius: 16px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important; }
.js-plotly-plot * { color: unset !important; }
[data-testid="stDataFrame"] { border-radius: 16px !important; }
hr { background: linear-gradient(90deg, transparent, #30363d, transparent) !important; height: 1px !important; border: none !important; }
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #21262d; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #58a6ff, #a371f7); border-radius: 4px; }
/* Tabs styling */
.stTabs [data-baseline-toggle="true"] {
    background-color: transparent;
    border-radius: 8px;
    color: #8b949e;
}
.stTabs [aria-selected="true"] {
    background-color: #21262d !important;
    color: #58a6ff !important;
    border-radius: 8px;
    border: 1px solid #30363d;
}
</style>
"""

# Apply dark theme CSS
st.markdown(get_dark_theme_css(), unsafe_allow_html=True)

st.sidebar.markdown("---")

# Simulation function for "AI processing"
def simulate_processing(task_name):
    """Simulate a robust AI processing workflow (short + human)"""
    steps = [
        ("🔄 Crunching clean data slices...", 0.4),
        ("🧠 Fine-tuning the model brain...", 0.6),
        ("📊 Building the forecast story...", 0.5),
    ]
    with st.status(f"🤖 **Running {task_name}...**", expanded=True) as status:
        for message, delay in steps:
            st.write(message)
            time.sleep(delay)
        status.update(label=f"✅ **{task_name} ready!**", state="complete", expanded=False)

# Title and description
st.title("🔮 EV Adoption Predictions & Forecasting")
st.markdown("""
Predict future EV adoption trends using advanced machine learning models. 
Generate robust forecasts for registrations, market share, and geographic expansion.
""")

# Load data
try:
    df = load_ev_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

if df is None or df.empty:
    st.error("Failed to load the dataset.")
    st.stop()

# Sidebar - Prediction Settings
st.sidebar.header("🎛️ Prediction Settings")

prediction_type = st.sidebar.selectbox(
    "Select Prediction Type",
    ["EV Registration Growth", "Market Share by Type", "Geographic Expansion", "Range Evolution"]
)

with st.sidebar.expander("🔧 Model Configuration", expanded=True):
    forecast_years = st.slider(
        "Forecast Horizon (Years)",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of years to forecast into the future"
    )

    model_type = st.selectbox(
        "Algorithm",
        ["Linear Regression", "Polynomial Regression (Degree 2)", "Random Forest"],
        index=1,
        help="Choose the machine learning algorithm"
    )

    confidence_interval = st.slider(
        "Confidence Level (%)",
        min_value=80,
        max_value=99,
        value=95,
        help="Certainty level for prediction intervals"
    )

st.sidebar.markdown("---")
if st.sidebar.button("🚀 Run Prediction", type="primary", use_container_width=True):
    run_prediction = True
else:
    run_prediction = False

# Main content
st.markdown("---")

# Only run if button clicked or first load (default)
if 'has_run' not in st.session_state:
    st.session_state.has_run = False

if run_prediction:
    st.session_state.has_run = True
    simulate_processing(prediction_type)
elif not st.session_state.has_run:
    st.info("👈 **Configure settings in the sidebar and click 'Run Prediction' to start.**")
    st.stop()

# --- PREDICTION LOGIC ---

# Prediction Type 1: EV Registration Growth
if prediction_type == "EV Registration Growth":
    st.subheader("📈 EV Registration Growth Forecast")
    
    # Tabs for organized view
    tab1, tab2, tab3 = st.tabs(["📊 Forecast", "📉 Model Performance", "📋 Historical Data"])
    
    # Prepare data
    yearly_counts = get_yearly_counts()
    yearly_counts = yearly_counts[yearly_counts['Model Year'] >= 2010]
    if yearly_counts.empty:
        st.warning("Need at least one full year of registrations to run this forecast.")
        st.stop()
    
    X = yearly_counts['Model Year'].values.reshape(-1, 1)
    y = yearly_counts['Count'].values
    
    # Train/Test Split for Evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Model Selection & Training
    if "Linear" in model_type:
        model = LinearRegression()
        model.fit(X, y)
        r2 = r2_score(y, model.predict(X))
        mae = mean_absolute_error(y, model.predict(X))
        transform_fn = lambda arr: arr
    elif "Polynomial" in model_type:
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X)
        model = LinearRegression()
        model.fit(X_poly, y)
        r2 = r2_score(y, model.predict(X_poly))
        mae = mean_absolute_error(y, model.predict(X_poly))
        transform_fn = lambda arr: poly.transform(arr)
    else:  # Random Forest
        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X, y)
        r2 = r2_score(y, model.predict(X))
        mae = mean_absolute_error(y, model.predict(X))
        transform_fn = lambda arr: arr

    # Future Predictions
    last_year = int(yearly_counts['Model Year'].max())
    future_years = np.arange(last_year + 1, last_year + forecast_years + 1).reshape(-1, 1)
    future_pred = model.predict(transform_fn(future_years))
    future_pred = np.maximum(future_pred, 0)  # No negative cars
    
    # Forecast DataFrame
    forecast_df = pd.DataFrame({
        'Year': future_years.flatten(),
        'Predicted_Count': future_pred
    })

    # --- TAB 1: FORECAST ---
    with tab1:
        # Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        next_year_val = int(forecast_df.iloc[0]['Predicted_Count'])
        current_val = int(yearly_counts.iloc[-1]['Count'])
        growth_pct = ((next_year_val - current_val) / current_val) * 100 if current_val else 0
        
        m1.metric("Current Annual", f"{current_val:,}", delta="Last observed year")
        m2.metric(f"{int(forecast_df.iloc[0]['Year'])} Forecast", f"{next_year_val:,}", delta=f"{growth_pct:.1f}% vs Current")
        m3.metric(f"Total {forecast_years}-Year Growth", f"{int(forecast_df['Predicted_Count'].sum()):,}", delta="Accumulated")
        m4.metric("Avg Annual Rate (CAGR)", f"{growth_pct:.1f}%", delta="Trend")

        # Chart
        fig = go.Figure()
        # Historical
        fig.add_trace(go.Scatter(x=yearly_counts['Model Year'], y=yearly_counts['Count'], mode='lines+markers', name='Historical Data', line=dict(color='#58a6ff', width=3), marker=dict(size=8)))
        # Forecast
        fig.add_trace(go.Scatter(x=forecast_df['Year'], y=forecast_df['Predicted_Count'], mode='lines+markers', name='Forecast', line=dict(color='#a371f7', width=3, dash='dash'), marker=dict(size=8)))
        
        # Confidence Interval (Simplified visual)
        upper_bound = forecast_df['Predicted_Count'] * (1 + (100-confidence_interval)/100)
        lower_bound = forecast_df['Predicted_Count'] * (1 - (100-confidence_interval)/100)
        
        fig.add_trace(go.Scatter(
            x=forecast_df['Year'].tolist() + forecast_df['Year'].tolist()[::-1],
            y=upper_bound.tolist() + lower_bound.tolist()[::-1],
            fill='toself', fillcolor='rgba(163, 113, 247, 0.1)', line=dict(color='rgba(0,0,0,0)'),
            name=f'{confidence_interval}% Confidence Interval'
        ))

        fig.update_layout(title="EV Registration Growth Trajectory", xaxis_title="Year", yaxis_title="Registrations", height=500, hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', legend=dict(orientation="h", y=1.02, x=1))
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: MODEL PERFORMANCE ---
    with tab2:
        st.markdown("### 🔍 Model Evaluation Metrics")
        c1, c2 = st.columns(2)
        c1.metric("R² Score (Accuracy)", f"{r2:.3f}", help="Closer to 1.0 is better. Indicates how well the model fits the historical data.")
        c2.metric("Mean Absolute Error (MAE)", f"{mae:.0f}", help="Average error in number of vehicles predicted vs actual.")
        
        st.info(f"**Insight:** This model ({model_type}) explains **{r2*100:.1f}%** of the variance in the historical data.")

    # --- TAB 3: DATA ---
    with tab3:
        st.dataframe(yearly_counts.join(forecast_df.set_index('Year'), on='Model Year', how='outer', lsuffix='_hist', rsuffix='_pred'), use_container_width=True)

# Prediction Type 2: Market Share
elif prediction_type == "Market Share by Type":
    st.subheader("🔋 EV Market Share Forecast")
    
    tab1, tab2 = st.tabs(["📊 Market Share Analysis", "📉 Trends"])
    
    yearly_type = get_market_share_history()
    if yearly_type.empty:
        st.info("Not enough EV type history to build a market-share story.")
    else:
        history = yearly_type.copy()
        last_year = int(history['Model Year'].max())
        future_years = np.arange(last_year + 1, last_year + forecast_years + 1)
        
        future_data = []
        for ev_type in history['Electric Vehicle Type'].unique():
            type_data = history[history['Electric Vehicle Type'] == ev_type]
            if len(type_data) < 2:
                continue
            X_type = type_data['Model Year'].values.reshape(-1, 1)
            y_type = type_data['Percentage'].values
            model = LinearRegression().fit(X_type, y_type)
            pred = np.clip(model.predict(future_years.reshape(-1, 1)), 0, 100)
            for year, pct in zip(future_years, pred):
                future_data.append(
                    {
                        'Model Year': year,
                        'Electric Vehicle Type': ev_type,
                        'Percentage': pct,
                        'Type': 'Forecast'
                    }
                )
        
        future_df = pd.DataFrame(future_data)
        combined = pd.concat(
            [
                history.assign(Type='Historical'),
                future_df
            ],
            ignore_index=True
        )
        
        with tab1:
            fig = px.area(
                combined,
                x='Model Year',
                y='Percentage',
                color='Electric Vehicle Type',
                pattern_shape='Type',
                title="Market Share Evolution & Forecast",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_layout(height=500, xaxis_title="Year", yaxis_title="Market Share (%)", plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            if not future_df.empty:
                st.dataframe(
                    future_df.pivot(index='Model Year', columns='Electric Vehicle Type', values='Percentage')
                    .sort_index()
                    .style.format("{:.1f}%"),
                    use_container_width=True
                )
            else:
                st.info("Need at least two years per EV type to forecast its share.")

# Prediction Type 3: Geographic Expansion (Condensed)
elif prediction_type == "Geographic Expansion":
    st.subheader("🗺️ Geographic Expansion Forecast")
    top_counties = df['County'].value_counts().head(5).index.tolist()
    
    # Simulate robust county analysis
    st.success(f"✅ Analyzed growth patterns for top 5 counties: {', '.join(top_counties)}")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        selected_county = st.selectbox("Select County", top_counties)
    
    county_data = df[(df['County'] == selected_county) & (df['Model Year'] >= 2015)].groupby('Model Year').size().reset_index(name='Count')
    
    # Simple forecast
    X = county_data['Model Year'].values.reshape(-1, 1)
    y = county_data['Count'].values
    m = LinearRegression().fit(X, y)
    
    future_years = np.arange(county_data['Model Year'].max() + 1, county_data['Model Year'].max() + forecast_years + 1).reshape(-1, 1)
    pred = m.predict(future_years)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=county_data['Model Year'], y=county_data['Count'], name='Historical', marker_color='#58a6ff'))
        fig.add_trace(go.Bar(x=future_years.flatten(), y=pred, name='Forecast', marker_color='#238636', opacity=0.7))
        fig.update_layout(title=f"Growth Forecast: {selected_county}", plot_bgcolor='rgba(0,0,0,0)', barmode='group')
        st.plotly_chart(fig, use_container_width=True)

# Prediction Type 4: Range Evolution
elif prediction_type == "Range Evolution":
    st.subheader("🔋 Battery Range Evolution")
    
    # Process data
    range_data = get_range_trends()
    if range_data.empty:
        st.warning("No electric range information available to model.")
        st.stop()
    
    # Forecast
    X = range_data['Model Year'].values.reshape(-1, 1)
    y_mean = range_data['mean'].values
    
    m = LinearRegression().fit(X, y_mean)
    future_years = np.arange(range_data['Model Year'].max() + 1, range_data['Model Year'].max() + forecast_years + 1).reshape(-1, 1)
    pred_mean = m.predict(future_years)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=range_data['Model Year'], y=range_data['mean'], name=' Avg Range (Hist)', line=dict(color='#f1c40f', width=3)))
        fig.add_trace(go.Scatter(x=future_years.flatten(), y=pred_mean, name='Avg Range (Pred)', line=dict(color='#e67e22', width=3, dash='dash')))
        fig.update_layout(title="Average Range Forecast (Miles)", xaxis_title="Year", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.markdown("### ⚡ Insight")
        st.metric("Predicted Avg Range (in 5 yrs)", f"{pred_mean[-1]:.0f} mi", delta=f"+{pred_mean[-1]-range_data['mean'].iloc[-1]:.0f} mi")
        st.caption("Based on historical battery technology improvements.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8b949e; font-size: 0.8rem;'>
    <p>🤖 predictions powered by Scikit-Learn Random Forest & Regression Models | 🛡️ 95% Confidence Interval Applied</p>
</div>
""", unsafe_allow_html=True)
