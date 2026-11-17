
import pandas as pd
import numpy as np


def weekly_volume(df):

    if df.empty:
        return pd.DataFrame()

    data = df.copy()

    data["week"] = (
        data["start_date"]
        .dt.tz_convert("UTC")
        .dt.tz_localize(None)
        .dt.to_period("W-SUN")
        .dt.start_time
    )

    weekly = (
        data.groupby("week")
        .agg(
            distance_km=("distance_km", "sum"),
            duration_min=("duration_min", "sum"),
            elevation=("total_elevation_gain", "sum"),
            sessions=("id", "count")
        )
        .reset_index()
    )

    return weekly


def monthly_volume(df):

    if df.empty:
        return pd.DataFrame()

    data = df.copy()

    data["month"] = (
        data["start_date"]
        .dt.tz_convert("UTC")
        .dt.strftime("%Y-%m")
    )

    return (
        data.groupby("month")
        .agg(
            distance_km=("distance_km", "sum"),
            duration_min=("duration_min", "sum"),
            sessions=("id", "count")
        )
        .reset_index()
    )


def calculate_summary(df):

    if df.empty:
        return {}

    return {
        "total_activities": len(df),
        "total_km": round(df["distance_km"].sum(), 2),
        "total_hours": round(
            df["duration_min"].sum() / 60, 2
        ),
        "total_elevation": round(
            df["total_elevation_gain"].sum(), 0
        ),
        "average_pace": round(
            df["moving_time"].sum() / 60 /
            df["distance_km"].sum(), 2
        ) if df["distance_km"].sum() > 0 else None
    }


def calculate_training_load(df):

    """
    Primera aproximación a la carga de entrenamiento.

    Si Strava proporciona suffer_score, utilizamos
    esa métrica. En caso contrario, empleamos un
    proxy de duración x intensidad percibida estimada.

    El proxy no equivale a una carga fisiológica real.
    """

    data = df.copy()

    if data.empty:
        return data

    if data["suffer_score"].notna().any():
        data["load"] = data["suffer_score"].fillna(0)
    else:
        data["load"] = (
            data["duration_min"] *
            (data["average_heartrate"] / 100)
        ).fillna(data["duration_min"] * 0.6)

    data["date"] = pd.to_datetime(data["date"])

    daily = (
        data.groupby("date")["load"]
        .sum()
        .asfreq("D", fill_value=0)
    )

    # EWMA: carga aguda y crónica.
    daily_load = daily.to_frame("daily_load")

    daily_load["acute_load"] = (
        daily.ewm(span=7, adjust=False).mean()
    )

    daily_load["chronic_load"] = (
        daily.ewm(span=28, adjust=False).mean()
    )

    daily_load["acwr"] = (
        daily_load["acute_load"] /
        daily_load["chronic_load"].replace(0, np.nan)
    )

    return daily_load.reset_index()
