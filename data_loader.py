import pandas as pd
import streamlit as st
from pathlib import Path

DATA_FILE = Path(__file__).parent / "Electric_Vehicle_Population_Data.csv"


@st.cache_data(show_spinner="Loading EV data...")
def load_data():
    """Read the EV dataset and do basic cleanup."""

    if not DATA_FILE.exists():
        raise FileNotFoundError("Dataset not found. Place Electric_Vehicle_Population_Data.csv in the project root.")

    df = pd.read_csv(DATA_FILE, low_memory=False)
    df.columns = df.columns.str.strip()

    # convert numeric columns
    for col in ["Model Year", "Electric Range", "Base MSRP"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # drop rows missing essential info
    df = df.dropna(subset=["Make", "Model", "Electric Vehicle Type"])

    return df
