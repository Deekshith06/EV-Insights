import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_data


# load dataset
ev_data = load_data()

st.title("EV Population Dashboard")
st.markdown("Explore electric vehicle registrations across Washington State — filter by manufacturer, year, and type.")

st.markdown("---")


# --- sidebar filters ---

st.sidebar.header("Filters")

# manufacturer filter
makes = ["All"] + sorted(ev_data["Make"].dropna().unique().tolist())
selected_make = st.sidebar.selectbox("Manufacturer", makes)

# year range filter
if "Model Year" in ev_data.columns:
    yr_min = int(ev_data["Model Year"].min())
    yr_max = int(ev_data["Model Year"].max())
    year_range = st.sidebar.slider("Model Year", yr_min, yr_max, (yr_min, yr_max))

# ev type filter
ev_types = sorted(ev_data["Electric Vehicle Type"].dropna().unique().tolist())
selected_type = st.sidebar.multiselect("Vehicle Type", ev_types, default=[])


# apply filters
filtered = ev_data.copy()

if selected_make != "All":
    filtered = filtered[filtered["Make"] == selected_make]

if "Model Year" in ev_data.columns:
    filtered = filtered[
        (filtered["Model Year"] >= year_range[0]) &
        (filtered["Model Year"] <= year_range[1])
    ]

if selected_type:
    filtered = filtered[filtered["Electric Vehicle Type"].isin(selected_type)]


# --- empty check ---

if len(filtered) == 0:
    st.warning("No vehicles match the selected filters. Try adjusting manufacturer, year range, or vehicle type.")
    st.stop()


# --- key metrics ---

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Vehicles", f"{len(filtered):,}")

with col2:
    avg_range = filtered[filtered["Electric Range"] > 0]["Electric Range"].mean()
    st.metric("Avg Range", f"{avg_range:.0f} mi" if pd.notna(avg_range) else "N/A")

with col3:
    st.metric("Unique Models", f"{filtered['Model'].nunique():,}")

with col4:
    st.metric("Manufacturers", f"{filtered['Make'].nunique():,}")


st.markdown("---")


# --- charts ---

# plotly theme helper
def chart_style():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f0f6fc", family="Inter, sans-serif"),
        xaxis=dict(gridcolor="#30363d"),
        yaxis=dict(gridcolor="#30363d"),
        margin=dict(l=20, r=20, t=40, b=20)
    )


chart_col1, chart_col2 = st.columns(2)

# pie chart - vehicle type distribution
with chart_col1:
    st.subheader("Vehicle Type Distribution")

    type_counts = filtered["Electric Vehicle Type"].value_counts()
    if len(type_counts) > 0:
        fig = px.pie(values=type_counts.values, names=type_counts.index, hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(**chart_style(), height=380, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No vehicle type data available for this filter.")

# bar chart - top models or manufacturers
with chart_col2:
    if selected_make != "All":
        st.subheader(f"Top {selected_make} Models")
        top_data = filtered["Model"].value_counts().head(10).reset_index()
        top_data.columns = ["Model", "Vehicles"]
        label_col = "Model"
    else:
        st.subheader("Top 10 Manufacturers")
        top_data = filtered["Make"].value_counts().head(10).reset_index()
        top_data.columns = ["Manufacturer", "Vehicles"]
        label_col = "Manufacturer"

    if len(top_data) > 0:
        fig = px.bar(top_data, x="Vehicles", y=label_col, orientation="h",
                     color="Vehicles", color_continuous_scale="Blues")
        style = chart_style()
        style["yaxis"]["categoryorder"] = "total ascending"
        fig.update_layout(**style, height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for this filter.")


st.markdown("---")


trend_col1, trend_col2 = st.columns(2)

# line chart - registrations by year
with trend_col1:
    st.subheader("Registrations by Year")

    if "Model Year" in filtered.columns:
        year_counts = filtered["Model Year"].value_counts().sort_index().reset_index()
        year_counts.columns = ["Model Year", "Vehicles"]
        if len(year_counts) > 1:
            fig = px.line(year_counts, x="Model Year", y="Vehicles", markers=True)
            fig.update_traces(line_color="#58a6ff", marker=dict(size=7, color="#a371f7"))
            fig.update_layout(**chart_style(), height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough year data to show a trend.")

# histogram - range distribution
with trend_col2:
    st.subheader("Range Distribution")

    range_data = filtered[filtered["Electric Range"] > 0][["Electric Range"]]
    if len(range_data) > 0:
        fig = px.histogram(range_data, x="Electric Range", nbins=30,
                           labels={"Electric Range": "Range (miles)"},
                           color_discrete_sequence=["#2ea043"])
        fig.update_layout(**chart_style(), height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No range data available for this filter.")


st.markdown("---")

# footer
st.caption("Built with Streamlit & Plotly • Data: Washington State DOL")
