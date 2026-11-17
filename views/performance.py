
import streamlit as st
import plotly.express as px

from analytics.metrics import (
    weekly_volume,
    monthly_volume,
    calculate_training_load
)


def render_performance(df):

    if df.empty:
        st.warning("No activities available.")
        return

    weekly = weekly_volume(df)
    monthly = monthly_volume(df)

    st.subheader("Weekly training volume")

    fig = px.bar(
        weekly,
        x="week",
        y="distance_km",
        title="Weekly running volume",
        labels={
            "week": "Week",
            "distance_km": "Kilometers"
        }
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Monthly training volume")

    fig = px.line(
        monthly,
        x="month",
        y="distance_km",
        markers=True,
        title="Monthly kilometers"
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Training load")

    load = calculate_training_load(df)

    fig = px.line(
        load,
        x="date",
        y=["acute_load", "chronic_load"],
        title="Acute vs chronic training load"
    )

    st.plotly_chart(fig, width="stretch")
