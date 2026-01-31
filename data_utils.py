from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "Electric_Vehicle_Population_Data.csv"

CATEGORICAL_DTYPES: Dict[str, str] = {
    "County": "category",
    "City": "category",
    "State": "category",
    "Electric Vehicle Type": "category",
    "Clean Alternative Fuel Vehicle (CAFV) Eligibility": "category",
}

NUMERIC_COLUMNS: Dict[str, Tuple[str, str]] = {
    "Model Year": ("integer", "coerce"),
    "Electric Range": ("integer", "coerce"),
    "Base MSRP": ("float", "coerce"),
}

COORD_REGEX = r"POINT \((-?[\d.]+) (-?[\d.]+)\)"
ESSENTIAL_COLUMNS = ["Make", "Model", "Electric Vehicle Type"]


@st.cache_data(ttl=3600, show_spinner="Loading EV data...")
def load_ev_data() -> pd.DataFrame:
    """Load the canonical dataset and perform lightweight normalization."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "Electric_Vehicle_Population_Data.csv not found in project root"
        )

    df = pd.read_csv(
        DATA_PATH,
        dtype=CATEGORICAL_DTYPES,
        low_memory=False,
    )
    df.columns = df.columns.str.strip()

    for column, (downcast, error_handling) in NUMERIC_COLUMNS.items():
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column], errors=error_handling, downcast=downcast
            )

    if "Vehicle Location" in df.columns:
        coords = df["Vehicle Location"].str.extract(COORD_REGEX)
        df["Longitude"] = pd.to_numeric(coords[0], errors="coerce")
        df["Latitude"] = pd.to_numeric(coords[1], errors="coerce")

    available_columns = [col for col in ESSENTIAL_COLUMNS if col in df.columns]
    if available_columns:
        df = df.dropna(subset=available_columns)

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def get_vehicle_catalog() -> pd.DataFrame:
    """Return aggregated vehicle range stats for fast lookups."""
    df = load_ev_data()
    if "Electric Range" not in df.columns:
        return pd.DataFrame(columns=["Vehicle", "mean", "count"])

    df_with_range = df[df["Electric Range"] > 0].copy()
    if df_with_range.empty:
        return pd.DataFrame(columns=["Vehicle", "mean", "count"])

    df_with_range["Vehicle"] = (
        df_with_range["Make"].astype(str) + " " + df_with_range["Model"].astype(str)
    )

    catalog = (
        df_with_range.groupby("Vehicle", observed=True)["Electric Range"]
        .agg(["mean", "count"])
        .sort_values(["count", "mean"], ascending=[False, False])
    )
    return catalog


@st.cache_data(ttl=3600, show_spinner=False)
def get_yearly_counts(min_year: int = 2010) -> pd.DataFrame:
    """Return yearly registration counts for downstream charts."""
    df = load_ev_data()
    if "Model Year" not in df.columns:
        return pd.DataFrame(columns=["Model Year", "Count"])

    yearly = (
        df[df["Model Year"].notna() & (df["Model Year"] >= min_year)]
        .groupby("Model Year", observed=True)
        .size()
        .reset_index(name="Count")
        .sort_values("Model Year")
    )
    return yearly


@st.cache_data(ttl=3600, show_spinner=False)
def get_market_share_history(min_year: int = 2015) -> pd.DataFrame:
    """Return EV-type share history, ready for modeling."""
    df = load_ev_data()
    required_cols = {"Model Year", "Electric Vehicle Type"}
    if not required_cols.issubset(df.columns):
        return pd.DataFrame(columns=["Model Year", "Electric Vehicle Type", "Count"])

    yearly_breakdown = (
        df[df["Model Year"].notna() & (df["Model Year"] >= min_year)]
        .groupby(["Model Year", "Electric Vehicle Type"], observed=True)
        .size()
        .reset_index(name="Count")
    )

    yearly_totals = yearly_breakdown.groupby("Model Year", observed=True)["Count"].sum()
    yearly_breakdown = yearly_breakdown.join(
        yearly_totals, on="Model Year", rsuffix="_total"
    )
    yearly_breakdown["Percentage"] = (
        yearly_breakdown["Count"] / yearly_breakdown["Count_total"] * 100
    )
    return yearly_breakdown.rename(columns={"Count_total": "Total"})


@st.cache_data(ttl=3600, show_spinner=False)
def get_range_trends(min_year: int = 2012) -> pd.DataFrame:
    """Summarize average and max electric range by year."""
    df = load_ev_data()
    if "Electric Range" not in df.columns or "Model Year" not in df.columns:
        return pd.DataFrame(columns=["Model Year", "mean", "max"])

    return (
        df[
            (df["Electric Range"].notna())
            & (df["Model Year"].notna())
            & (df["Model Year"] >= min_year)
        ]
        .groupby("Model Year", observed=True)["Electric Range"]
        .agg(["mean", "max"])
        .reset_index()
        .sort_values("Model Year")
    )
