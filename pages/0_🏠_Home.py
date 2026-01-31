import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
from streamlit.components.v1 import html

from data_utils import get_vehicle_catalog, load_ev_data

# Note: Page config is set in the main Dashboard.py file

# Enforce dark theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Shared dark theme for the full dashboard surface.
def build_dashboard_theme():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* DARK THEME */
:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-card: #21262d;
    --text-primary: #f0f6fc;
    --text-secondary: #8b949e;
    --accent: #58a6ff;
    --accent-secondary: #a371f7;
    --border: #30363d;
}

.main {
    padding: 0.5rem 1.5rem;
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: var(--bg-primary) !important;
    line-height: 1.7;
}

[data-testid="stAppViewContainer"] { background-color: #0d1117 !important; }
[data-testid="stHeader"] { background-color: #0d1117 !important; }
[data-testid="stToolbar"] { background-color: #0d1117 !important; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInFromLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}

.stMarkdown, .stMetric, .stDataFrame, .stPlotlyChart { animation: fadeInUp 0.6s ease-out forwards; }

[data-testid="stMetricValue"] { 
    animation: fadeInUp 0.5s ease-out forwards; 
    font-weight: 700 !important; 
    font-size: 1.8rem !important; 
    color: #f0f6fc !important;
}

[data-testid="stMetricLabel"] { font-weight: 500 !important; color: #8b949e !important; }

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #21262d 0%, #161b22 100%) !important;
    border-radius: 16px !important;
    padding: 1.2rem !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    border: 1px solid #30363d !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
}

[data-testid="stMetric"]:hover { 
    transform: translateY(-4px) scale(1.02) !important; 
    box-shadow: 0 12px 40px rgba(88,166,255,0.15) !important; 
}

h1 {
    background: linear-gradient(135deg, #58a6ff 0%, #a371f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    animation: fadeInUp 0.8s ease-out;
}

h2, h3 { color: #f0f6fc !important; font-weight: 600 !important; animation: slideInFromLeft 0.6s ease-out; }

[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #161b22 0%, #0d1117 100%) !important; 
    border-right: 1px solid #30363d !important; 
}

.stButton > button {
    background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(35,134,54,0.3) !important;
}

.stButton > button:hover { transform: translateY(-2px) scale(1.03) !important; }

[data-testid="stSelectbox"] > div > div { 
    border-radius: 12px !important; 
    border: 2px solid #30363d !important; 
    background: #21262d !important;
}

.stAlert { border-radius: 12px !important; border: 1px solid #30363d !important; }

[data-testid="stDataFrame"] { 
    border-radius: 16px !important; 
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important; 
}

.js-plotly-plot { border-radius: 16px !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important; }

[data-testid="stExpander"] { 
    border-radius: 12px !important; 
    border: 1px solid #30363d !important; 
    background: #161b22 !important; 
}

[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #58a6ff 0%, #a371f7 100%) !important;
    border-radius: 12px !important;
    color: white !important;
}

hr { background: linear-gradient(90deg, transparent, #30363d, transparent) !important; height: 1px !important; border: none !important; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #21262d; border-radius: 4px; }
::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #58a6ff, #a371f7); border-radius: 4px; }

p, span, div { color: #c9d1d9; line-height: 1.7; }
</style>
"""

st.markdown(build_dashboard_theme(), unsafe_allow_html=True)


# Render a small browser widget that requests GPS access from the user.
def render_gps_request_widget():
    """Ask the browser for GPS permission and surface helpful status messages."""
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; padding: 10px; }
            .btn { 
                background: #1E88E5; 
                color: white; 
                border: none; 
                padding: 12px 24px; 
                border-radius: 5px; 
                cursor: pointer; 
                font-size: 16px; 
                font-weight: bold;
                width: 100%;
                margin-bottom: 10px;
            }
            .btn:hover { background: #1565C0; }
            .btn:disabled { background: #ccc; cursor: not-allowed; }
            .status { 
                padding: 10px; 
                border-radius: 5px; 
                margin: 10px 0; 
                text-align: left;
            }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .info { background: #d1ecf1; color: #0c5460; }
        </style>
    </head>
    <body>
        <button id="getLocationBtn" class="btn" onclick="getLocation()">
            📍 Get My Live GPS Location
        </button>
        <div id="status"></div>
        
        <script>
            let locationData = null;
            
            function getLocation() {
                const btn = document.getElementById('getLocationBtn');
                const statusDiv = document.getElementById('status');
                
                btn.disabled = true;
                btn.textContent = '🔄 Getting location...';
                
                statusDiv.innerHTML = '<div class="status info">⏳ Requesting location permission...</div>';
                
                if (!navigator.geolocation) {
                    statusDiv.innerHTML = '<div class="status error">❌ Geolocation is not supported by your browser.</div>';
                    btn.disabled = false;
                    btn.textContent = '📍 Get My Live GPS Location';
                    return;
                }
                
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        const accuracy = position.coords.accuracy;
                        
                        locationData = {
                            latitude: lat,
                            longitude: lon,
                            accuracy: accuracy,
                            timestamp: new Date().toISOString()
                        };
                        
                        // Store in localStorage for Streamlit to read
                        localStorage.setItem('gps_location', JSON.stringify(locationData));
                        
                        statusDiv.innerHTML = 
                            '<div class="status success">' +
                            '✅ <strong>Location Retrieved Successfully!</strong><br><br>' +
                            '📍 <strong>Latitude:</strong> ' + lat.toFixed(6) + '°<br>' +
                            '📍 <strong>Longitude:</strong> ' + lon.toFixed(6) + '°<br>' +
                            '🎯 <strong>Accuracy:</strong> ±' + accuracy.toFixed(0) + ' meters<br>' +
                            '⏰ <strong>Time:</strong> ' + new Date().toLocaleTimeString() +
                            '</div>';
                        
                        btn.disabled = false;
                        btn.textContent = '🔄 Refresh Location';
                        
                        // Trigger Streamlit rerun by setting a flag
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: locationData
                        }, '*');
                    },
                    function(error) {
                        let errorMsg = '';
                        switch(error.code) {
                            case error.PERMISSION_DENIED:
                                errorMsg = '❌ <strong>Permission Denied</strong><br>Please allow location access in your browser settings.';
                                break;
                            case error.POSITION_UNAVAILABLE:
                                errorMsg = '❌ <strong>Position Unavailable</strong><br>Location information is not available.';
                                break;
                            case error.TIMEOUT:
                                errorMsg = '❌ <strong>Request Timeout</strong><br>Location request timed out. Please try again.';
                                break;
                            default:
                                errorMsg = '❌ <strong>Unknown Error</strong><br>An error occurred while getting location.';
                        }
                        
                        statusDiv.innerHTML = '<div class="status error">' + errorMsg + '</div>';
                        btn.disabled = false;
                        btn.textContent = '📍 Get My Live GPS Location';
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 0
                    }
                );
            }
            
            // Check if location already exists in localStorage
            window.onload = function() {
                const stored = localStorage.getItem('gps_location');
                if (stored) {
                    try {
                        const data = JSON.parse(stored);
                        document.getElementById('status').innerHTML = 
                            '<div class="status info">' +
                            '💾 <strong>Cached Location Available</strong><br>' +
                            'Click button to get fresh location' +
                            '</div>';
                    } catch(e) {}
                }
            };
        </script>
    </body>
    </html>
    """
    return html_code

# Basic Haversine helper; keeps the math in one place.
def haversine_distance_miles(lat1, lon1, lat2, lon2):
    """Return the great-circle distance in miles between two latitude/longitude pairs."""
    from math import radians, sin, cos, sqrt, atan2
    
    # Earth's radius in miles
    R = 3959.0
    
    # Convert to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

# Initialize session state for live tracking
if 'tracking_enabled' not in st.session_state:
    st.session_state.tracking_enabled = False
if 'tracking_history' not in st.session_state:
    st.session_state.tracking_history = []
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.now()
if 'current_battery' not in st.session_state:
    st.session_state.current_battery = 100.0
if 'selected_vehicle_range' not in st.session_state:
    st.session_state.selected_vehicle_range = 250
if 'live_gps_enabled' not in st.session_state:
    st.session_state.live_gps_enabled = False
if 'live_location' not in st.session_state:
    st.session_state.live_location = None
if 'location_accuracy' not in st.session_state:
    st.session_state.location_accuracy = None
if 'current_speed' not in st.session_state:
    st.session_state.current_speed = 0
if 'speed_history' not in st.session_state:
    st.session_state.speed_history = []
if 'previous_gps_location' not in st.session_state:
    st.session_state.previous_gps_location = None
if 'previous_gps_time' not in st.session_state:
    st.session_state.previous_gps_time = None
if 'total_distance_gps' not in st.session_state:
    st.session_state.total_distance_gps = 0.0

# Load data
try:
    df = load_ev_data()
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

if df is None or df.empty:
    st.error("Failed to load the dataset. Please ensure 'Electric_Vehicle_Population_Data.csv' is in the correct location.")
    st.stop()

vehicle_catalog = get_vehicle_catalog()

# Navigation info
st.info("👈 **Navigate:** Use the sidebar to switch between pages - 🏠 Home | 🔮 Predictions")

# Title and description
st.title("🏠 Home | Electric Vehicle Population Dashboard")
st.markdown("### Comprehensive analysis of Electric Vehicle registrations in Washington State")

# Problem statement in an expander
with st.expander("📋 About This Dashboard", expanded=False):
    st.markdown("""
    **Dataset:** Electric Vehicle Population Data from Washington State
    
    **Description:** This dashboard provides comprehensive insights into the electric vehicle 
    population, including distribution by make, model, type, geographic location, and trends over time.
    
    **Key Features:**
    - Real-time filtering and analysis
    - Live GPS location tracking
    - Geographic distribution visualization
    - Manufacturer and model insights
    - Electric range analysis
    - Year-over-year trends
    
    **🌐 How to Use Live GPS:**
    1. Enable "Live Range Tracking" in sidebar
    2. Select "Use Live GPS" as location source
    3. Click "📍 Get My Live GPS Location" button
    4. Allow location permission when browser asks
    5. Copy the displayed coordinates into the input fields below
    6. Your location will be used for nearest EV calculations!
    """)

# Theme selector at top of sidebar
st.sidebar.markdown("### 🎨 Theme")
theme_col1, theme_col2 = st.sidebar.columns(2)
with theme_col1:
    if st.button("☀️ Light", use_container_width=True, type="secondary" if st.session_state.dark_mode else "primary"):
        st.session_state.dark_mode = False
        st.rerun()
with theme_col2:
    if st.button("🌙 Dark", use_container_width=True, type="primary" if st.session_state.dark_mode else "secondary"):
        st.session_state.dark_mode = True
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filters")

# Live Range Tracking Section
st.sidebar.markdown("---")
st.sidebar.subheader("📡 Live Range Tracking")
tracking_enabled = st.sidebar.toggle(
    "Enable Live Tracking",
    value=st.session_state.tracking_enabled,
    help="Monitor EV range in real-time simulation"
)

if tracking_enabled != st.session_state.tracking_enabled:
    st.session_state.tracking_enabled = tracking_enabled
    if tracking_enabled:
        st.session_state.start_time = datetime.now()
        st.session_state.tracking_history = []
        st.session_state.current_battery = 100.0

if st.session_state.tracking_enabled:
    # Vehicle selection for tracking
    if not vehicle_catalog.empty:
        vehicle_options = vehicle_catalog.head(20).index.tolist()
        selected_vehicle = st.sidebar.selectbox(
            "Select Vehicle for Tracking",
            options=vehicle_options,
            help="Choose a vehicle to simulate range tracking"
        )
        
        if selected_vehicle:
            st.session_state.selected_vehicle_range = vehicle_catalog.loc[selected_vehicle, 'mean']
            st.sidebar.info(f"📊 Avg Range: {st.session_state.selected_vehicle_range:.0f} miles")
    else:
        st.sidebar.warning("No vehicles with range data found. Try disabling filters.")
    
    # GPS Location Input
    st.sidebar.markdown("**📍 Your GPS Location**")
    
    location_mode = st.sidebar.radio(
        "Location Source",
        options=["Use Live GPS", "Manual Input", "Default (Seattle)"],
        help="Choose how to set your location"
    )
    
    if location_mode == "Use Live GPS":
        st.sidebar.markdown("**🌐 Browser GPS Location**")
        
        # Display GPS component in an expander
        with st.sidebar.expander("📍 Get GPS Location", expanded=True):
            location_data = html(render_gps_request_widget(), height=300)
        
        # Manual coordinate input for GPS location
        st.sidebar.markdown("**Enter coordinates from above:**")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            user_lat = st.number_input("Lat", value=47.6062, format="%.6f", step=0.0001, key="gps_lat")
        with col2:
            user_lon = st.number_input("Lon", value=-122.3321, format="%.6f", step=0.0001, key="gps_lon")
        
        # Update location
        st.session_state.user_location = (user_lat, user_lon)
        
        # Show current location
        if user_lat != 47.6062 or user_lon != -122.3321:
            st.sidebar.success(f"✅ Using: {user_lat:.4f}°, {user_lon:.4f}°")
            st.session_state.live_location = (user_lat, user_lon)
        else:
            st.sidebar.info("👆 Copy coordinates from GPS widget above")
    
    elif location_mode == "Manual Input":
        user_lat = st.sidebar.number_input("Latitude", value=47.6062, format="%.4f", step=0.0001, key="manual_lat")
        user_lon = st.sidebar.number_input("Longitude", value=-122.3321, format="%.4f", step=0.0001, key="manual_lon")
        st.session_state.user_location = (user_lat, user_lon)
        st.sidebar.success(f"📍 {user_lat:.4f}, {user_lon:.4f}")
    
    else:  # Default (Seattle)
        st.session_state.user_location = (47.6062, -122.3321)
        st.sidebar.info(f"📍 Seattle, WA (Default)")
    
    # Find nearest EVs
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df_with_gps = df.dropna(subset=['Latitude', 'Longitude']).copy()
        if len(df_with_gps) > 0:
            # Calculate distance to user location
            df_with_gps['distance'] = np.sqrt(
                (df_with_gps['Latitude'] - st.session_state.user_location[0])**2 + 
                (df_with_gps['Longitude'] - st.session_state.user_location[1])**2
            ) * 69  # Approximate miles
            
            nearest = df_with_gps.nsmallest(5, 'distance')
            if len(nearest) > 0:
                st.sidebar.markdown("**🎯 Nearest EVs**")
                for idx, row in nearest.iterrows():
                    st.sidebar.text(f"• {row['Make']} {row['Model']}")
                    st.sidebar.text(f"  {row['distance']:.1f} mi away")
    
    avg_speed = st.sidebar.slider(
        "Average Speed (mph)",
        min_value=20,
        max_value=80,
        value=45,
        help="Simulated driving speed"
    )
    
    driving_style = st.sidebar.select_slider(
        "Driving Style",
        options=["Eco", "Normal", "Sport"],
        value="Normal"
    )
    
    refresh_rate = st.sidebar.slider(
        "Refresh Rate (seconds)",
        min_value=1,
        max_value=10,
        value=3
    )
    
    if st.sidebar.button("🔄 Reset Tracking", width="stretch"):
        st.session_state.tracking_history = []
        st.session_state.start_time = datetime.now()
        st.session_state.current_battery = 100.0
        st.rerun()

st.sidebar.markdown("---")

# Range Prediction Calculator
st.sidebar.subheader("🔮 Range Prediction")
st.sidebar.markdown("Calculate remaining range based on conditions:")

enable_range_prediction = st.sidebar.checkbox("Enable Range Calculator", value=False)

# Store prediction variables in session state
if 'prediction_vars' not in st.session_state:
    st.session_state.prediction_vars = {}

if enable_range_prediction:
    with st.sidebar:
        st.markdown("### ⚡ Range Calculator Settings")
        st.markdown("**Vehicle Selection:**")
        
        if not vehicle_catalog.empty:
            catalog_preview = vehicle_catalog.head(25)
            vehicle_list = ['Custom'] + catalog_preview.index.tolist()
            
            selected_vehicle_pred = st.selectbox(
                "Choose Vehicle",
                vehicle_list,
                key="pred_vehicle"
            )
            
            if selected_vehicle_pred == 'Custom':
                base_range = st.number_input(
                    "Full Range (miles)",
                    min_value=50,
                    max_value=500,
                    value=250,
                    step=10
                )
            else:
                base_range = catalog_preview.loc[selected_vehicle_pred, 'mean']
                st.caption("Using average EPA range from Washington registrations.")
                st.info(f"📊 Avg Range: {base_range:.0f} mi")
        else:
            base_range = st.number_input(
                "Full Range (miles)",
                min_value=50,
                max_value=500,
                value=250,
                step=10
            )
        
        st.markdown("---")
        st.markdown("**Current Conditions:**")
        
        # Current battery level
        battery_level = st.slider(
            "Battery Level (%)",
            min_value=0,
            max_value=100,
            value=80,
            step=5
        )
        
        # Driving conditions
        col1, col2 = st.columns(2)
        with col1:
            speed_pred = st.number_input(
                "Speed (mph)",
                min_value=20,
                max_value=80,
                value=55,
                step=5
            )
        
        with col2:
            temp = st.number_input(
                "Temp (°F)",
                min_value=-20,
                max_value=120,
                value=70,
                step=5
            )
        
        # Additional factors
        terrain = st.select_slider(
            "Terrain",
            options=["Flat", "Rolling", "Hilly", "Mountain"],
            value="Flat"
        )
        
        climate_control = st.checkbox("Climate Control On", value=False)
        highway_driving = st.checkbox("Highway Driving", value=True)
    
    # Calculate predicted range
    current_range = base_range * (battery_level / 100)
    
    # Speed efficiency factor (optimal at 45 mph)
    if speed_pred <= 45:
        speed_factor = 1.0
    else:
        speed_factor = 1.0 - ((speed_pred - 45) * 0.01)
    
    # Temperature factor (optimal at 70°F)
    if 60 <= temp <= 80:
        temp_factor = 1.0
    elif temp < 60:
        temp_factor = 1.0 - ((60 - temp) * 0.01)
    else:
        temp_factor = 1.0 - ((temp - 80) * 0.005)
    
    # Terrain factor
    terrain_factors = {
        "Flat": 1.0,
        "Rolling": 0.9,
        "Hilly": 0.8,
        "Mountain": 0.7
    }
    terrain_factor = terrain_factors[terrain]
    
    # Climate control penalty
    climate_factor = 0.85 if climate_control else 1.0
    
    # Highway vs city
    highway_factor = 0.9 if highway_driving else 1.0
    
    # Calculate final predicted range
    predicted_range = current_range * speed_factor * temp_factor * terrain_factor * climate_factor * highway_factor
    
    # Store in session state for main page display
    st.session_state.prediction_vars = {
        'base_range': base_range,
        'current_range': current_range,
        'predicted_range': predicted_range,
        'speed_factor': speed_factor,
        'temp_factor': temp_factor,
        'terrain_factor': terrain_factor,
        'climate_factor': climate_factor,
        'highway_factor': highway_factor,
        'climate_control': climate_control,
        'highway_driving': highway_driving,
        'efficiency': (predicted_range / current_range) * 100
    }

st.sidebar.markdown("---")

# Year filter
if 'Model Year' in df.columns:
    min_year = int(df['Model Year'].min())
    max_year = int(df['Model Year'].max())
    
    if min_year < max_year:
        year_range = st.sidebar.slider(
            "Model Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
        df_filtered = df[(df['Model Year'] >= year_range[0]) & (df['Model Year'] <= year_range[1])]
    else:
        # Only one year in dataset
        st.sidebar.info(f"📅 All vehicles are from year {min_year}")
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# EV Type filter
if 'Electric Vehicle Type' in df.columns:
    ev_types = ['All'] + sorted(df['Electric Vehicle Type'].dropna().unique().tolist())
    selected_ev_type = st.sidebar.selectbox("Electric Vehicle Type", ev_types)
    if selected_ev_type != 'All':
        df_filtered = df_filtered[df_filtered['Electric Vehicle Type'] == selected_ev_type]

# Make filter
if 'Make' in df.columns:
    makes = ['All'] + sorted(df_filtered['Make'].dropna().unique().tolist())
    selected_make = st.sidebar.selectbox("Manufacturer", makes)
    if selected_make != 'All':
        df_filtered = df_filtered[df_filtered['Make'] == selected_make]

# County filter
if 'County' in df.columns:
    counties = ['All'] + sorted(df_filtered['County'].dropna().unique().tolist())
    selected_county = st.sidebar.selectbox("County", counties)
    if selected_county != 'All':
        df_filtered = df_filtered[df_filtered['County'] == selected_county]

# Electric Range filter
if 'Electric Range' in df.columns:
    range_values = df_filtered['Electric Range'].dropna()
    if len(range_values) > 0:
        min_range = int(range_values.min())
        max_range = int(range_values.max())
        if min_range < max_range:
            range_filter = st.sidebar.slider(
                "Minimum Electric Range (miles)",
                min_value=min_range,
                max_value=max_range,
                value=min_range
            )
            df_filtered = df_filtered[df_filtered['Electric Range'] >= range_filter]

st.sidebar.markdown("---")
st.sidebar.info(f"📊 Showing **{len(df_filtered):,}** of **{len(df):,}** vehicles")

# Main Dashboard
st.markdown("---")

# Check if we should show only tracking/prediction or full dashboard
show_only_tracking = st.session_state.tracking_enabled
show_only_prediction = enable_range_prediction

# Show message if tracking or prediction is enabled
if show_only_tracking:
    st.info("📡 **Live Range Tracking Mode** - Dashboard visualizations hidden. Disable tracking in sidebar to view full dashboard.")
elif show_only_prediction:
    st.info("🔮 **Range Prediction Mode** - Dashboard visualizations hidden. Disable prediction calculator in sidebar to view full dashboard.")

# Only show main dashboard if tracking and prediction are disabled
if not show_only_tracking and not show_only_prediction:
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total EVs",
            value=f"{len(df_filtered):,}",
            delta=f"{(len(df_filtered)/len(df)*100):.1f}% of total"
        )
    
    with col2:
        if 'Make' in df_filtered.columns:
            unique_makes = df_filtered['Make'].nunique()
            st.metric(
                label="Manufacturers",
                value=f"{unique_makes}",
                delta=None
            )
    
    with col3:
        if 'Electric Range' in df_filtered.columns:
            avg_range = df_filtered['Electric Range'].mean()
            st.metric(
                label="Avg Range",
                value=f"{avg_range:.0f} mi",
                delta=None
            )
    
    with col4:
        if 'County' in df_filtered.columns:
            unique_counties = df_filtered['County'].nunique()
            st.metric(
                label="Counties",
                value=f"{unique_counties}",
                delta=None
            )
    
    # Live GPS Location Status Display
    if st.session_state.live_gps_enabled and st.session_state.live_location:
        st.markdown("---")
        st.subheader("🌐 Live GPS Location Status")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📍 Your Latitude",
                value=f"{st.session_state.live_location[0]:.4f}°",
                delta=None
            )
        
        with col2:
            st.metric(
                label="📍 Your Longitude",
                value=f"{st.session_state.live_location[1]:.4f}°",
                delta=None
            )
        
        with col3:
            if st.session_state.location_accuracy:
                st.metric(
                    label="🎯 GPS Accuracy",
                    value=f"±{st.session_state.location_accuracy:.0f}m",
                    delta=None
                )
        
        with col4:
            # Count nearby EVs (within 10 miles)
            if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns:
                df_nearby = df_filtered.dropna(subset=['Latitude', 'Longitude']).copy()
                df_nearby['distance'] = np.sqrt(
                    (df_nearby['Latitude'] - st.session_state.live_location[0])**2 + 
                    (df_nearby['Longitude'] - st.session_state.live_location[1])**2
                ) * 69
                nearby_count = len(df_nearby[df_nearby['distance'] <= 10])
                st.metric(
                    label="🚗 EVs Nearby",
                    value=f"{nearby_count}",
                    delta="within 10 miles"
                )
        
        # Show user location on mini map
        if st.checkbox("📍 Show My Location on Map", value=False):
            user_map_df = pd.DataFrame({
                'Latitude': [st.session_state.live_location[0]],
                'Longitude': [st.session_state.live_location[1]],
                'Location': ['Your Location']
            })
            
            fig = px.scatter_mapbox(
                user_map_df,
                lat='Latitude',
                lon='Longitude',
                hover_name='Location',
                zoom=12,
                height=400,
                color_discrete_sequence=['red']
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig, width="stretch")

# Live Tracking Display
if st.session_state.tracking_enabled:
    st.markdown("---")
    
    # Show tracking mode
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📡 Live GPS-Based Range Tracking")
    with col2:
        st.info("🌐 GPS Mode")
    
    st.markdown("""
    **📍 Real GPS Tracking:** Speed and distance are calculated from actual GPS location changes.
    - ✅ **Stationary = 0 mph** - If you don't move, speed stays at 0
    - ✅ **Accurate distance** - Uses Haversine formula for real distance
    - 🔄 **Updates every refresh** - Change your location to see speed increase
    """)
    
    # Calculate elapsed time
    elapsed_time = (datetime.now() - st.session_state.start_time).total_seconds() / 60  # minutes
    current_time = datetime.now()
    
    # Calculate actual speed based on GPS location changes
    current_gps = st.session_state.user_location
    
    if st.session_state.previous_gps_location is not None and st.session_state.previous_gps_time is not None:
        # Calculate distance moved using Haversine formula
        prev_lat, prev_lon = st.session_state.previous_gps_location
        curr_lat, curr_lon = current_gps
        
        distance_moved = calculate_gps_distance(prev_lat, prev_lon, curr_lat, curr_lon)
        
        # Calculate time difference in hours
        time_diff = (current_time - st.session_state.previous_gps_time).total_seconds() / 3600
        
        # Calculate actual speed (mph)
        if time_diff > 0:
            st.session_state.current_speed = distance_moved / time_diff
        else:
            st.session_state.current_speed = 0
        
        # Add to total distance
        st.session_state.total_distance_gps += distance_moved
    else:
        # First reading - speed is 0
        st.session_state.current_speed = 0
        st.session_state.total_distance_gps = 0
    
    # Update previous location and time
    st.session_state.previous_gps_location = current_gps
    st.session_state.previous_gps_time = current_time
    
    # Calculate speed delta (acceleration/deceleration)
    if len(st.session_state.speed_history) > 0:
        speed_delta = st.session_state.current_speed - st.session_state.speed_history[-1]['speed']
    else:
        speed_delta = 0
    
    # Add to speed history
    st.session_state.speed_history.append({
        'timestamp': datetime.now(),
        'speed': st.session_state.current_speed,
        'elapsed_minutes': elapsed_time,
        'speed_delta': speed_delta
    })
    
    # Keep only last 100 speed data points
    if len(st.session_state.speed_history) > 100:
        st.session_state.speed_history = st.session_state.speed_history[-100:]
    
    # Calculate drain rate based on driving parameters
    style_factor = {"Eco": 0.7, "Normal": 1.0, "Sport": 1.4}
    drain_multiplier = style_factor.get(driving_style, 1.0)
    
    # Speed efficiency (optimal at 45 mph) - use current speed
    speed_efficiency = 1.0 if st.session_state.current_speed <= 45 else 1.0 + ((st.session_state.current_speed - 45) / 100)
    
    # Calculate battery drain per hour
    drain_rate = (speed_efficiency * drain_multiplier * 2.0)  # % per hour
    battery_drain = drain_rate * (elapsed_time / 60)
    st.session_state.current_battery = max(0, 100 - battery_drain)
    
    # Calculate remaining range
    current_range = (st.session_state.current_battery / 100) * st.session_state.selected_vehicle_range
    
    # Use actual GPS distance traveled
    distance_traveled = st.session_state.total_distance_gps
    
    # Add to tracking history
    st.session_state.tracking_history.append({
        'timestamp': datetime.now(),
        'battery_percent': st.session_state.current_battery,
        'range_miles': current_range,
        'elapsed_minutes': elapsed_time,
        'distance_traveled': distance_traveled,
        'current_speed': st.session_state.current_speed
    })
    
    # Keep only last 100 data points
    if len(st.session_state.tracking_history) > 100:
        st.session_state.tracking_history = st.session_state.tracking_history[-100:]
    
    # Live metrics - Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔋 Battery Level",
            value=f"{st.session_state.current_battery:.1f}%",
            delta=f"-{battery_drain:.2f}%" if battery_drain > 0 else "0%"
        )
    
    with col2:
        # Show live speed with acceleration/deceleration indicator
        speed_emoji = "⚡" if speed_delta > 2 else "🐌" if speed_delta < -2 else "➡️"
        st.metric(
            label=f"{speed_emoji} Current Speed",
            value=f"{st.session_state.current_speed:.1f} mph",
            delta=f"{speed_delta:+.1f} mph" if abs(speed_delta) > 0.1 else "steady"
        )
    
    with col3:
        st.metric(
            label="📍 Remaining Range",
            value=f"{current_range:.1f} mi",
            delta=None
        )
    
    with col4:
        st.metric(
            label="⏱️ Elapsed Time",
            value=f"{int(elapsed_time)} min",
            delta=None
        )
    
    # Live metrics - Row 2
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🛣️ Distance Traveled",
            value=f"{distance_traveled:.1f} mi",
            delta=None
        )
    
    with col2:
        # Average speed over session
        if len(st.session_state.speed_history) > 0:
            avg_session_speed = np.mean([s['speed'] for s in st.session_state.speed_history])
            st.metric(
                label="📊 Avg Speed",
                value=f"{avg_session_speed:.1f} mph",
                delta=None
            )
    
    with col3:
        # Max speed reached
        if len(st.session_state.speed_history) > 0:
            max_speed = max([s['speed'] for s in st.session_state.speed_history])
            st.metric(
                label="🏁 Max Speed",
                value=f"{max_speed:.1f} mph",
                delta=None
            )
    
    with col4:
        # Energy efficiency
        efficiency = current_range / st.session_state.selected_vehicle_range * 100
        st.metric(
            label="⚡ Efficiency",
            value=f"{efficiency:.1f}%",
            delta=None
        )
    
    # Live tracking charts
    if len(st.session_state.tracking_history) > 1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Battery Level Over Time")
            tracking_df = pd.DataFrame(st.session_state.tracking_history)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tracking_df['elapsed_minutes'],
                y=tracking_df['battery_percent'],
                mode='lines+markers',
                name='Battery %',
                line=dict(color='#2E7D32', width=3),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(46, 125, 50, 0.1)'
            ))
            
            fig.update_layout(
                xaxis_title="Time (minutes)",
                yaxis_title="Battery Level (%)",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.subheader("🎯 Remaining Range Over Time")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tracking_df['elapsed_minutes'],
                y=tracking_df['range_miles'],
                mode='lines+markers',
                name='Range (mi)',
                line=dict(color='#1976D2', width=3),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(25, 118, 210, 0.1)'
            ))
            
            fig.update_layout(
                xaxis_title="Time (minutes)",
                yaxis_title="Remaining Range (miles)",
                height=300,
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")
        
        # Speed tracking chart (full width)
        if len(st.session_state.speed_history) > 1:
            st.subheader("🚗 Live Speed Tracking (Ups & Downs)")
            speed_df = pd.DataFrame(st.session_state.speed_history)
            
            fig = go.Figure()
            
            # Speed line
            fig.add_trace(go.Scatter(
                x=speed_df['elapsed_minutes'],
                y=speed_df['speed'],
                mode='lines+markers',
                name='Current Speed',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=6),
                fill='tozeroy',
                fillcolor='rgba(255, 107, 107, 0.1)'
            ))
            
            # Target speed line (average)
            fig.add_trace(go.Scatter(
                x=speed_df['elapsed_minutes'],
                y=[avg_speed] * len(speed_df),
                mode='lines',
                name='Target Speed',
                line=dict(color='#4ECDC4', width=2, dash='dash')
            ))
            
            # Add acceleration zones (green) and deceleration zones (red)
            for i in range(1, len(speed_df)):
                if speed_df.iloc[i]['speed_delta'] > 1:
                    # Acceleration - green background
                    fig.add_vrect(
                        x0=speed_df.iloc[i-1]['elapsed_minutes'],
                        x1=speed_df.iloc[i]['elapsed_minutes'],
                        fillcolor="green",
                        opacity=0.1,
                        layer="below",
                        line_width=0
                    )
                elif speed_df.iloc[i]['speed_delta'] < -1:
                    # Deceleration - red background
                    fig.add_vrect(
                        x0=speed_df.iloc[i-1]['elapsed_minutes'],
                        x1=speed_df.iloc[i]['elapsed_minutes'],
                        fillcolor="red",
                        opacity=0.1,
                        layer="below",
                        line_width=0
                    )
            
            fig.update_layout(
                xaxis_title="Time (minutes)",
                yaxis_title="Speed (mph)",
                height=350,
                margin=dict(l=0, r=0, t=30, b=0),
                hovermode='x unified',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, width="stretch")
            
            # Speed statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                accelerations = sum(1 for s in st.session_state.speed_history if s['speed_delta'] > 1)
                st.metric("⚡ Accelerations", accelerations)
            with col2:
                decelerations = sum(1 for s in st.session_state.speed_history if s['speed_delta'] < -1)
                st.metric("🐌 Decelerations", decelerations)
            with col3:
                speed_variance = np.std([s['speed'] for s in st.session_state.speed_history])
                st.metric("📊 Speed Variance", f"{speed_variance:.1f} mph")
            with col4:
                smooth_score = max(0, 100 - (accelerations + decelerations) * 2)
                st.metric("🎯 Smoothness", f"{smooth_score:.0f}%")
    
    # Auto-refresh for live tracking
    time.sleep(refresh_rate)
    st.rerun()

# Range Prediction Display - show on main page when enabled
if show_only_prediction and st.session_state.prediction_vars:
    st.markdown("---")
    st.subheader("🔮 EV Range Prediction Results")
    
    vars = st.session_state.prediction_vars
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🔋 Base Range",
            f"{vars['current_range']:.0f} mi",
            delta=None
        )
    
    with col2:
        st.metric(
            "🎯 Predicted Range",
            f"{vars['predicted_range']:.0f} mi",
            delta=f"{vars['efficiency']:.0f}%"
        )
    
    with col3:
        range_loss = vars['current_range'] - vars['predicted_range']
        st.metric(
            "📉 Range Loss",
            f"{range_loss:.0f} mi",
            delta=f"-{(range_loss/vars['current_range']*100):.0f}%"
        )
    
    with col4:
        if vars['predicted_range'] < 30:
            status = "⚠️ Low"
            status_color = "🔴"
        elif vars['predicted_range'] < 60:
            status = "⚡ Moderate"
            status_color = "🟡"
        else:
            status = "✅ Good"
            status_color = "🟢"
        st.metric("Status", status)
    
    # Efficiency breakdown
    st.markdown("---")
    st.subheader("📊 Efficiency Factor Breakdown")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("⚡ Speed", f"{vars['speed_factor']*100:.0f}%")
    
    with col2:
        st.metric("🌡️ Temperature", f"{vars['temp_factor']*100:.0f}%")
    
    with col3:
        st.metric("⛰️ Terrain", f"{vars['terrain_factor']*100:.0f}%")
    
    with col4:
        if vars['climate_control']:
            st.metric("❄️ Climate", f"{vars['climate_factor']*100:.0f}%")
        else:
            st.metric("❄️ Climate", "Off")
    
    with col5:
        if vars['highway_driving']:
            st.metric("🛣️ Highway", f"{vars['highway_factor']*100:.0f}%")
        else:
            st.metric("🛣️ Highway", "Off")
    
    # Visual chart
    st.markdown("---")
    st.subheader("📈 Range Comparison")
    
    import plotly.graph_objects as go
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=['Full Range', 'Current Range', 'Predicted Range'],
        y=[vars['base_range'], vars['current_range'], vars['predicted_range']],
        marker_color=['#1E88E5', '#FFA726', '#66BB6A'],
        text=[f"{vars['base_range']:.0f} mi", f"{vars['current_range']:.0f} mi", f"{vars['predicted_range']:.0f} mi"],
        textposition='auto',
    ))
    
    fig.update_layout(
        title="Range Analysis",
        yaxis_title="Range (miles)",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, width="stretch")
    
    # Range alert
    st.markdown("---")
    if vars['predicted_range'] < 30:
        st.error("⚠️ **Low Range Alert** - Charge your vehicle soon! You have less than 30 miles of predicted range.")
    elif vars['predicted_range'] < 60:
        st.warning("⚡ **Moderate Range** - Plan your charging stops. Consider finding a charging station within the next 30 miles.")
    else:
        st.success("✅ **Good Range** - You're safe to drive! Your vehicle has sufficient range for normal driving.")

# Visualizations - only show when tracking and prediction are disabled
if not show_only_tracking and not show_only_prediction:
    st.markdown("---")
    
    # Row 1: EV Type Distribution and Top Manufacturers
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔋 EV Type Distribution")
        if 'Electric Vehicle Type' in df_filtered.columns:
            ev_type_counts = df_filtered['Electric Vehicle Type'].value_counts()
            fig = px.pie(
                values=ev_type_counts.values,
                names=ev_type_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("🏭 Top 10 Manufacturers")
        if 'Make' in df_filtered.columns:
            top_makes = df_filtered['Make'].value_counts().head(10)
            fig = px.bar(
                x=top_makes.values,
                y=top_makes.index,
                orientation='h',
                color=top_makes.values,
                color_continuous_scale='Blues',
                labels={'x': 'Number of Vehicles', 'y': 'Manufacturer'}
            )
            fig.update_layout(
                height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, width="stretch")

    # Row 2: Model Year Trends and Electric Range Distribution
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 EV Registrations by Year")
        if 'Model Year' in df_filtered.columns:
            year_counts = df_filtered['Model Year'].value_counts().sort_index()
            fig = px.line(
                x=year_counts.index,
                y=year_counts.values,
                markers=True,
                labels={'x': 'Model Year', 'y': 'Number of Vehicles'}
            )
            fig.update_traces(line_color='#1E88E5', line_width=3, marker=dict(size=8))
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                hovermode='x unified'
            )
            st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("🔌 Electric Range Distribution")
        if 'Electric Range' in df_filtered.columns:
            range_data = df_filtered[df_filtered['Electric Range'] > 0]['Electric Range']
            fig = px.histogram(
                range_data,
                nbins=30,
                labels={'value': 'Electric Range (miles)', 'count': 'Number of Vehicles'},
                color_discrete_sequence=['#1E88E5']
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, width="stretch")

    # Row 3: County Distribution and Top Models
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🗺️ Top 10 Counties")
        if 'County' in df_filtered.columns:
            top_counties = df_filtered['County'].value_counts().head(10)
        fig = px.bar(
            x=top_counties.values,
            y=top_counties.index,
            orientation='h',
            color=top_counties.values,
            color_continuous_scale='Teal',
            labels={'x': 'Number of Vehicles', 'y': 'County'}
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("🚗 Top 10 Models")
        if 'Make' in df_filtered.columns and 'Model' in df_filtered.columns:
            df_filtered['Make_Model'] = df_filtered['Make'].astype(str) + ' ' + df_filtered['Model'].astype(str)
        top_models = df_filtered['Make_Model'].value_counts().head(10)
        fig = px.bar(
            x=top_models.values,
            y=top_models.index,
            orientation='h',
            color=top_models.values,
            color_continuous_scale='Purples',
            labels={'x': 'Number of Vehicles', 'y': 'Model'}
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, width="stretch")

    # Row 4: CAFV Eligibility and City Distribution
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✅ CAFV Eligibility Status")
        if 'Clean Alternative Fuel Vehicle (CAFV) Eligibility' in df_filtered.columns:
            cafv_counts = df_filtered['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].value_counts()
        fig = px.bar(
            x=cafv_counts.index,
            y=cafv_counts.values,
            color=cafv_counts.values,
            color_continuous_scale='Greens',
            labels={'x': 'CAFV Eligibility', 'y': 'Number of Vehicles'}
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("🏙️ Top 10 Cities")
        if 'City' in df_filtered.columns:
            top_cities = df_filtered['City'].value_counts().head(10)
        fig = px.bar(
            x=top_cities.values,
            y=top_cities.index,
            orientation='h',
            color=top_cities.values,
            color_continuous_scale='Oranges',
            labels={'x': 'Number of Vehicles', 'y': 'City'}
        )
        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        st.plotly_chart(fig, width="stretch")

    # GPS Location Map Section
    st.markdown("---")
    st.subheader("🗺️ GPS Location Map")

    # Check if we have location data
    if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns:
        df_map = df_filtered.dropna(subset=['Latitude', 'Longitude'])
    
        if len(df_map) > 0:
            # Map display options
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                # Ensure min_value < max_value for slider
                max_map_size = min(10000, len(df_map))
                min_map_size = min(100, len(df_map))
                
                if max_map_size > min_map_size:
                    map_sample_size = st.slider(
                        "Number of vehicles to display on map",
                        min_value=min_map_size,
                        max_value=max_map_size,
                        value=min(1000, len(df_map)),
                        step=min(100, max(1, (max_map_size - min_map_size) // 10)),
                        help="Displaying too many points may slow down the map"
                    )
                else:
                    # If dataset is too small, just use all records
                    map_sample_size = len(df_map)
                    st.info(f"📊 Showing all {len(df_map)} vehicles (dataset too small for sampling)")
            
            with col2:
                color_by = st.selectbox(
                    "Color markers by",
                    options=['Electric Vehicle Type', 'Make', 'County'],
                    help="Choose how to color the map markers"
                )
            
            with col3:
                show_map = st.checkbox("📍 Load Map", value=False, help="Click to load interactive map")
            
            if show_map:
                # Sample data for performance
                df_map_sample = df_map.sample(n=min(map_sample_size, len(df_map)), random_state=42).copy()
                
                # Create hover text
                df_map_sample['hover_text'] = (
                    df_map_sample['Make'].astype(str) + ' ' + df_map_sample['Model'].astype(str) + '<br>' +
                    'Year: ' + df_map_sample['Model Year'].astype(str) + '<br>' +
                    'Range: ' + df_map_sample['Electric Range'].astype(str) + ' mi<br>' +
                    'City: ' + df_map_sample['City'].astype(str) + ', ' + df_map_sample['County'].astype(str)
                )
                
                # Create the map
                fig = px.scatter_mapbox(
                    df_map_sample,
                    lat='Latitude',
                    lon='Longitude',
                    color=color_by,
                    hover_name='hover_text',
                    zoom=7,
                    height=600,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                
                fig.update_layout(
                    mapbox_style="open-street-map",
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="top",
                        y=0.99,
                        xanchor="left",
                        x=0.01,
                        bgcolor="rgba(255, 255, 255, 0.8)"
                    )
                )
                
                st.plotly_chart(fig, width="stretch")
                
                # Map statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📍 Shown", f"{len(df_map_sample):,}")
                with col2:
                    st.metric("🌍 Total GPS", f"{len(df_map):,}")
                with col3:
                    coverage = (len(df_map) / len(df_filtered)) * 100
                    st.metric("📊 Coverage", f"{coverage:.1f}%")
                with col4:
                    st.metric("⚡ Status", "✅ Loaded")
        else:
            st.info("No GPS location data available for the current filter selection.")
    else:
        st.warning("GPS location data not available in the dataset.")

    # Data Table Section
    st.markdown("---")
    st.subheader("📋 Detailed Data View")

    # Display options
    show_columns = st.multiselect(
        "Select columns to display",
        options=df_filtered.columns.tolist(),
        default=['Make', 'Model', 'Model Year', 'Electric Vehicle Type', 'Electric Range', 'County', 'City']
    )

    if show_columns:
        st.dataframe(
        df_filtered[show_columns].head(100),
        width="stretch",
        height=400
        )
    
        # Download button
        csv = df_filtered[show_columns].to_csv(index=False)
        st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name=f"ev_data_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
        )

    # Statistics Section
    st.markdown("---")
    st.subheader("📊 Statistical Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        if 'Electric Range' in df_filtered.columns:
            st.markdown("**Electric Range Statistics**")
        range_data = df_filtered[df_filtered['Electric Range'] > 0]['Electric Range']
        st.write(f"- Mean: {range_data.mean():.1f} miles")
        st.write(f"- Median: {range_data.median():.1f} miles")
        st.write(f"- Max: {range_data.max():.0f} miles")
        st.write(f"- Min: {range_data.min():.0f} miles")

    with col2:
        if 'Model Year' in df_filtered.columns:
            st.markdown("**Model Year Statistics**")
        st.write(f"- Newest: {int(df_filtered['Model Year'].max())}")
        st.write(f"- Oldest: {int(df_filtered['Model Year'].min())}")
        st.write(f"- Most Common: {int(df_filtered['Model Year'].mode()[0])}")

    with col3:
        st.markdown("**Dataset Statistics**")
        st.write(f"- Total Records: {len(df_filtered):,}")
        st.write(f"- Unique Makes: {df_filtered['Make'].nunique()}")
        st.write(f"- Unique Models: {df_filtered['Model'].nunique()}")
        st.write(f"- Unique Counties: {df_filtered['County'].nunique()}")

# Footer with premium animated design
st.markdown("""
<div style='
    text-align: center; 
    padding: 2rem 1rem;
    margin-top: 2rem;
    background: linear-gradient(135deg, rgba(0,122,255,0.05) 0%, rgba(88,86,214,0.05) 100%);
    border-radius: 20px;
    border: 1px solid rgba(0,122,255,0.1);
    animation: fadeInUp 0.8s ease-out forwards;
'>
    <div style='
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 0.5rem;
    '>
        <span style='font-size: 1.5rem;'>⚡</span>
        <span style='
            font-size: 1.1rem;
            font-weight: 600;
            background: linear-gradient(135deg, #007AFF, #5856D6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        '>Electric Vehicle Population Dashboard</span>
    </div>
    <p style='
        color: #64748b; 
        font-size: 0.85rem;
        margin: 0.5rem 0 0 0;
    '>
        Built with ❤️ using Streamlit & Plotly | Data: Washington State DOL
    </p>
</div>
""", unsafe_allow_html=True)
