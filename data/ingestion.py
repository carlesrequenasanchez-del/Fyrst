
import pandas as pd


def normalize_activities(raw_activities):

    if not raw_activities:
        return pd.DataFrame()

    df = pd.DataFrame(raw_activities)

    columns = [
        "id",
        "name",
        "type",
        "sport_type",
        "start_date",
        "distance",
        "moving_time",
        "elapsed_time",
        "total_elevation_gain",
        "average_speed",
        "max_speed",
        "average_heartrate",
        "max_heartrate",
        "suffer_score",
        "average_cadence"
    ]

    # Evitamos fallos si faltan campos opcionales.
    df = df.reindex(columns=columns)

    df["start_date"] = pd.to_datetime(
        df["start_date"],
        utc=True
    )

    # Conversiones de unidades.
    df["distance_km"] = df["distance"] / 1000

    df["duration_min"] = df["moving_time"] / 60

    df["pace_min_km"] = (
        df["moving_time"] / 60
    ) / df["distance_km"].replace(0, float("nan"))

    df["speed_kmh"] = df["average_speed"] * 3.6

    df["elevation_per_km"] = (
        df["total_elevation_gain"] /
        df["distance_km"].replace(0, float("nan"))
    )

    df["date"] = df["start_date"].dt.date

    return df.sort_values("start_date").reset_index(drop=True)
