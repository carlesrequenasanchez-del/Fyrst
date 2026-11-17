
import json
import pandas as pd

from analytics.metrics import (
    weekly_volume,
    calculate_summary
)

from integrations.ai_provider import generate_ai_response
from coach.prompts import SYSTEM_PROMPT


def build_athlete_context(df):

    if df.empty:
        raise ValueError("No training data available.")

    data = df.copy()

    last_date = data["start_date"].max()

    # Últimas 4 semanas.
    recent = data[
        data["start_date"] >=
        last_date - pd.Timedelta(days=28)
    ].copy()

    weekly = weekly_volume(recent)

    summary = calculate_summary(recent)

    context = {
        "period": "Last 28 days",
        "summary": summary,
        "weekly_metrics": weekly.to_dict(
            orient="records"
        ),
        "recent_activities": recent[
            [
                "start_date",
                "sport_type",
                "distance_km",
                "duration_min",
                "pace_min_km",
                "total_elevation_gain",
                "average_heartrate"
            ]
        ].tail(30).to_dict(orient="records")
    }

    return context


def ask_coach(df, question, athlete_profile=None):

    context = build_athlete_context(df)

    prompt = f"""
    ATHLETE DATA:

    {json.dumps(context, default=str, indent=2)}

    ATHLETE PROFILE:

    {json.dumps(athlete_profile or {}, indent=2)}

    ATHLETE QUESTION:

    {question}

    Analyze the actual training data and provide
    a personalized and actionable response.
    """

    return generate_ai_response(
        SYSTEM_PROMPT,
        prompt
    )
