
import streamlit as st

from integrations.strava_api import get_activities
from data.ingestion import normalize_activities
from analytics.metrics import calculate_summary


def render_dashboard():

    st.title("Training Overview")

    if "activities" not in st.session_state:

        with st.spinner("Loading Strava activities..."):

            raw = get_activities()

            st.session_state.activities = (
                normalize_activities(raw)
            )

    df = st.session_state.activities

    if df.empty:
        st.info("No activities found.")
        return

    summary = calculate_summary(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total kilometers",
        f"{summary['total_km']:.1f} km"
    )

    col2.metric(
        "Training hours",
        f"{summary['total_hours']:.1f} h"
    )

    col3.metric(
        "Elevation",
        f"{summary['total_elevation']:.0f} m"
    )

    col4.metric(
        "Activities",
        summary["total_activities"]
    )

    st.divider()

    st.subheader("Recent activities")

    st.dataframe(
        df[
            [
                "start_date",
                "sport_type",
                "distance_km",
                "duration_min",
                "pace_min_km",
                "total_elevation_gain"
            ]
        ].sort_values(
            "start_date",
            ascending=False
        ),
        width="stretch",
        hide_index=True
    )
