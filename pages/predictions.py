import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import LabelEncoder

from data_loader import load_data


st.title("EV Range Estimation")
st.markdown("Predict the electric range of a vehicle based on its specs using a trained Random Forest model.")


# --- prepare training data ---

@st.cache_resource(show_spinner="Training model...")
def train_model():
    """Train a RandomForest model to predict electric range."""

    df = load_data()

    # keep only rows where range is known and positive
    df = df[df["Electric Range"] > 0].copy()

    # features we can use
    df = df[["Make", "Model Year", "Electric Vehicle Type", "Electric Range"]].dropna()

    # encode categorical features
    make_encoder = LabelEncoder()
    type_encoder = LabelEncoder()

    df["make_encoded"] = make_encoder.fit_transform(df["Make"])
    df["type_encoded"] = type_encoder.fit_transform(df["Electric Vehicle Type"])

    features = df[["Model Year", "make_encoded", "type_encoded"]]
    target = df["Electric Range"]

    # split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    # train random forest
    model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42)
    model.fit(X_train, y_train)

    # evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    return model, make_encoder, type_encoder, r2, mae


model, make_enc, type_enc, r2, mae = train_model()


st.markdown("---")


# --- model performance ---

st.subheader("Model Performance")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric("R² Score", f"{r2:.3f}")

with m2:
    st.metric("Mean Absolute Error", f"{mae:.1f} miles")

with m3:
    st.metric("Algorithm", "Random Forest")

st.info(f"The model explains **{r2 * 100:.1f}%** of the variance in EV range, with an average error of **{mae:.1f} miles**.")


st.markdown("---")


# --- user prediction form ---

st.subheader("Estimate Range for a Vehicle")

ev_data = load_data()

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    all_makes = sorted(ev_data["Make"].dropna().unique().tolist())
    user_make = st.selectbox("Manufacturer", all_makes, index=all_makes.index("TESLA") if "TESLA" in all_makes else 0)

with row1_col2:
    # filter models by selected manufacturer
    brand_models = sorted(ev_data[ev_data["Make"] == user_make]["Model"].dropna().unique().tolist())
    user_model = st.selectbox("Car Model", brand_models)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    yr_min = int(ev_data["Model Year"].min())
    yr_max = int(ev_data["Model Year"].max())
    user_year = st.slider("Model Year", yr_min, yr_max, yr_max)

with row2_col2:
    ev_types = sorted(ev_data["Electric Vehicle Type"].dropna().unique().tolist())
    user_type = st.selectbox("Vehicle Type", ev_types)


if st.button("Predict Range", type="primary", use_container_width=True):

    # encode inputs same way as training
    try:
        make_code = make_enc.transform([user_make])[0]
    except ValueError:
        st.warning(f"'{user_make}' wasn't in the training data. Using closest match.")
        make_code = 0

    try:
        type_code = type_enc.transform([user_type])[0]
    except ValueError:
        type_code = 0

    input_data = pd.DataFrame({
        "Model Year": [user_year],
        "make_encoded": [make_code],
        "type_encoded": [type_code]
    })

    predicted_range = model.predict(input_data)[0]
    predicted_range = max(predicted_range, 0)

    st.markdown("---")

    st.subheader("Prediction Result")

    r1, r2_col = st.columns(2)

    with r1:
        st.metric(
            f"{user_make} {user_model} ({user_year})",
            f"{predicted_range:.0f} miles",
            delta=f"{'BEV' if 'Battery' in user_type else 'PHEV'}"
        )

    with r2_col:
        # compare with actual average for this specific model
        actual = ev_data[(ev_data["Make"] == user_make) & (ev_data["Model"] == user_model) & (ev_data["Electric Range"] > 0)]
        if len(actual) > 0:
            avg_actual = actual["Electric Range"].mean()
            diff = predicted_range - avg_actual
            st.metric(
                f"Avg Range for {user_model}",
                f"{avg_actual:.0f} miles",
                delta=f"{diff:+.0f} mi vs prediction"
            )


st.markdown("---")


# --- feature importance ---

st.subheader("What Affects EV Range?")

feature_names = ["Model Year", "Manufacturer", "Vehicle Type"]
importances = model.feature_importances_

fig = px.bar(
    x=importances, y=feature_names, orientation="h",
    color=importances, color_continuous_scale="Blues",
    labels={"x": "Importance", "y": "Feature"}
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="#30363d"),
    yaxis=dict(gridcolor="#30363d"),
    margin=dict(l=20, r=20, t=40, b=20),
    height=300,
    showlegend=False
)
st.plotly_chart(fig, use_container_width=True)


st.markdown("---")


# --- range trends over time ---

st.subheader("Average Range by Year")

range_by_year = (
    ev_data[ev_data["Electric Range"] > 0]
    .groupby("Model Year")["Electric Range"]
    .mean()
    .reset_index()
)

fig = px.line(
    range_by_year, x="Model Year", y="Electric Range",
    markers=True, labels={"Electric Range": "Avg Range (miles)"}
)
fig.update_traces(line_color="#58a6ff", marker=dict(size=7, color="#a371f7"))
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#f0f6fc", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="#30363d"),
    yaxis=dict(gridcolor="#30363d"),
    margin=dict(l=20, r=20, t=40, b=20),
    height=380
)
st.plotly_chart(fig, use_container_width=True)


st.markdown("---")
st.caption("Model: Random Forest (100 trees) • Trained on Washington State DOL data")
