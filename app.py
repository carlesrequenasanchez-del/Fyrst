
import streamlit as st
import pandas as pd
from integrations.strava_api import get_activities

from core.auth import (
    get_authorization_url,
    exchange_code,
    logout
)

st.set_page_config(
    page_title="Fyrst",
    page_icon="🏃",
    layout="wide"
)

st.title("Fyrst")
st.caption("Your personal endurance intelligence platform")

# 1. Gestionar errores OAuth
if st.query_params.get("error"):
    st.error("Has cancelado la autorización de Strava.")
    st.query_params.clear()

# 2. Gestionar callback OAuth
code = st.query_params.get("code")
state = st.query_params.get("state")

if code and state:
    try:
        exchange_code(code, state)
        st.query_params.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Error de autenticación: {e}")

# 3. Comprobar autenticación
if "strava_tokens" not in st.session_state:

    st.markdown("### Connect your Strava account")

    auth_url = get_authorization_url()

    st.link_button(
        "Connect with Strava",
        auth_url,
        type="primary"
    )

    st.stop()

# 4. Usuario autenticado
athlete = st.session_state.athlete

st.sidebar.success(
    f"Connected: {athlete.get('firstname', 'Athlete')}"
)

if st.sidebar.button("Logout"):
    logout()
    st.rerun()

st.success("Successfully connected to Strava!")

st.title("Your training dashboard")

st.subheader("Activity synchronization")

if st.button("Sync Strava activities", type="primary"):
    try:
        with st.spinner("Downloading your Strava activities..."):
            activities = get_activities()

        st.session_state.activities = activities

        st.success(
            f"Successfully downloaded {len(activities)} activities."
        )

    except Exception as e:
        st.error(f"Error downloading activities: {e}")


# Mostrar actividades
activities = st.session_state.get("activities", [])

if activities:
    df = pd.DataFrame(activities)

    # Normalizar algunos campos
    df["start_date"] = pd.to_datetime(
        df["start_date"],
        utc=True
    )

    df["distance_km"] = df["distance"] / 1000
    df["duration_min"] = df["moving_time"] / 60

    df["pace_min_km"] = (
        df["moving_time"] / 60 / df["distance_km"].replace(0, float("nan"))
    )

    # Seleccionar columnas para visualizar
    columns = [
        "name",
        "sport_type",
        "start_date",
        "distance_km",
        "duration_min",
        "total_elevation_gain",
        "average_heartrate",
        "pace_min_km",
    ]

    available_columns = [
        col for col in columns if col in df.columns
    ]

    st.subheader("Your activities")

    st.metric("Total activities", len(df))

    st.dataframe(
        df[available_columns].sort_values(
            "start_date",
            ascending=False
        ),
        width="stretch",
        hide_index=True,
    )

else:
    st.info("No activities downloaded yet. Click Sync Strava activities.")
