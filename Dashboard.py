import streamlit as st
import pandas as pd
import plotly.express as px

from data_utils import load_ev_data
from improved_ev_advisor import create_improved_ev_advisor


# -----------------------------------------------------------------------------
# Page configuration & global styles
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EV Range & Insights Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_global_styles() -> None:
    """Inject dark theme styles, typography, and component overrides."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        :root {
            --bg: #0d1117;
            --panel: #161b22;
            --panel-soft: #1f2430;
            --border: #30363d;
            --text: #f0f6fc;
            --secondary: #8b949e;
            --accent: #58a6ff;
            --accent-2: #a371f7;
        }

        body, [data-testid="stAppViewContainer"] {
            background: var(--bg) !important;
            color: var(--text) !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #161b22 0%, #0d1117 100%) !important;
            border-right: 1px solid var(--border);
        }

        h1, h2, h3 {
            color: var(--text) !important;
            font-weight: 600 !important;
        }

        h1 {
            font-size: 2.35rem !important;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.75rem !important;
        }

        h2 {
            font-size: 1.6rem !important;
            margin: 2rem 0 0.75rem 0 !important;
        }

        h3 {
            font-size: 1.2rem !important;
            margin: 1.5rem 0 0.5rem 0 !important;
        }

        p, label, span, li {
            color: var(--secondary) !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #238636, #2ea043) !important;
            color: #fff !important;
            border-radius: 10px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: transform 0.2s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px) scale(1.01);
        }

        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(88,166,255,.08), rgba(163,113,247,.08)) !important;
            border: 1px solid rgba(48,54,61,.7) !important;
            border-radius: 18px !important;
            padding: 1.2rem 1rem !important;
            min-height: 130px;
        }

        [data-testid="stMetricLabel"] {
            color: var(--secondary) !important;
            letter-spacing: 0.02em;
        }

        [data-testid="stMetricValue"] {
            color: var(--text) !important;
        }

        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiselect"] > div > div,
        [data-testid="stTextInput"] > div > input,
        [data-testid="stSlider"] > div > div,
        [data-baseweb="select"] > div {
            background: var(--panel-soft) !important;
            color: var(--text) !important;
            border-radius: 12px !important;
            border: 1px solid var(--border) !important;
        }

        [data-baseweb="tag"] {
            background: rgba(88,166,255,.15) !important;
            color: var(--text) !important;
            border: none !important;
        }

        .js-plotly-plot {
            border-radius: 18px !important;
            border: 1px solid rgba(48,54,61,.6);
            padding: 0.5rem;
            background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(255,255,255,.01));
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_filters(ev_df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar controls and return filtered dataframe."""
    st.sidebar.header("🔍 Filter Options")

    filtered = ev_df.copy()

    makes = ["All"] + sorted(ev_df["Make"].dropna().unique().tolist())
    manufacturer = st.sidebar.selectbox("Manufacturer", makes)
    if manufacturer != "All":
        filtered = filtered[filtered["Make"] == manufacturer]

    if "Model Year" in ev_df.columns:
        year_min = int(ev_df["Model Year"].min())
        year_max = int(ev_df["Model Year"].max())
        year_range = st.sidebar.slider(
            "Model Year Range",
            min_value=year_min,
            max_value=year_max,
            value=(year_min, year_max),
        )
        filtered = filtered[
            (filtered["Model Year"] >= year_range[0]) &
            (filtered["Model Year"] <= year_range[1])
        ]

    return filtered


def _render_metrics(ev_df: pd.DataFrame) -> None:
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🚗 Total Vehicles", f"{len(ev_df):,}")

    with col2:
        st.metric("🏭 Manufacturers", f"{ev_df['Make'].nunique():,}")

    with col3:
        if "Electric Range" in ev_df.columns and not ev_df["Electric Range"].empty:
            st.metric("⚡ Average Range", f"{ev_df['Electric Range'].mean():.0f} mi")
        else:
            st.metric("⚡ Average Range", "N/A")

    with col4:
        county_count = ev_df["County"].nunique() if "County" in ev_df.columns else 0
        st.metric("📍 Counties", f"{county_count:,}")


def _render_distribution_charts(ev_df: pd.DataFrame) -> None:
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🔋 Vehicle Type Distribution")
        if "Electric Vehicle Type" in ev_df.columns and not ev_df.empty:
            type_counts = ev_df["Electric Vehicle Type"].value_counts()
            chart = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            chart.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f0f6fc", family="Inter, sans-serif"),
            )
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Vehicle type information is unavailable for the current filters.")

    with col2:
        st.subheader("🏭 Top 10 Manufacturers")
        if "Make" in ev_df.columns and not ev_df.empty:
            top_makes = ev_df["Make"].value_counts().head(10)
            chart = px.bar(
                x=top_makes.values,
                y=top_makes.index,
                orientation="h",
                color=top_makes.values,
                color_continuous_scale="Blues",
                labels={"x": "Number of Vehicles", "y": "Manufacturer"},
            )
            chart.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                yaxis={"categoryorder": "total ascending"},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f0f6fc", family="Inter, sans-serif"),
                xaxis=dict(gridcolor="#30363d"),
                showlegend=False,
            )
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.info("Manufacturer data is unavailable for the current filters.")


def _render_trend_chart(ev_df: pd.DataFrame) -> None:
    st.markdown("---")
    st.subheader("📈 Registration Trends by Model Year")
    if "Model Year" not in ev_df.columns or ev_df.empty:
        st.info("Model year trend cannot be calculated.")
        return

    year_counts = ev_df["Model Year"].value_counts().sort_index()
    chart = px.line(
        x=year_counts.index,
        y=year_counts.values,
        markers=True,
        labels={"x": "Model Year", "y": "Number of Vehicles"},
    )
    chart.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0f6fc", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#30363d", linecolor="#30363d"),
        yaxis=dict(gridcolor="#30363d", linecolor="#30363d"),
    )
    chart.update_traces(
        line_color="#58a6ff",
        marker=dict(size=8, color="#a371f7"),
    )
    st.plotly_chart(chart, use_container_width=True)


def _render_footer() -> None:
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align:center; padding:2rem 1.5rem; background:rgba(88,166,255,0.05);
            border-radius:16px; border:1px solid rgba(88,166,255,0.1);'>
            <div style='margin-bottom:0.5rem;'>
                <span style='font-size:1.4rem'>📊</span>
                <span style='margin-left:0.4rem; font-size:1.1rem; font-weight:600;
                    background:linear-gradient(135deg,#58a6ff,#a371f7);-webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;'>EV Range & Insights Dashboard</span>
            </div>
            <p style='color:#8b949e; font-size:0.9rem;'>Built with Streamlit & Plotly • Data source: Washington State Department of Licensing</p>
            <p style='color:#8b949e; font-size:0.85rem;'>Use the navigation sidebar to explore more pages including ML predictions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_global_styles()

    try:
        ev_data = load_ev_data()
    except FileNotFoundError as exc:
        st.error(f"Unable to load EV dataset: {exc}")
        return

    st.title("EV Population Dashboard")
    st.markdown(
        """
        Explore live insights into Washington State's electric vehicle adoption, compare
        manufacturers, and receive research-based recommendations tailored to your needs.
        """
    )

    filtered_data = apply_filters(ev_data)

    _render_metrics(filtered_data)

    st.subheader("�� Smart EV Match Finder")
    create_improved_ev_advisor(filtered_data)

    _render_distribution_charts(filtered_data)
    _render_trend_chart(filtered_data)
    _render_footer()


if __name__ == "__main__":
    main()
