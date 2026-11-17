import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_setting(key: str, default=None):
    """Lee primero Streamlit Secrets y después variables de entorno."""
    try:
        value = st.secrets.get(key)
        if value:
            return value
    except Exception:
        pass

    return os.getenv(key, default)


STRAVA_CLIENT_ID = get_setting("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = get_setting("STRAVA_CLIENT_SECRET")

STRAVA_REDIRECT_URI = get_setting(
    "STRAVA_REDIRECT_URI",
    "http://localhost:8501"
)

GEMINI_API_KEY = get_setting("GEMINI_API_KEY")
GROQ_API_KEY = get_setting("GROQ_API_KEY")

AI_PROVIDER = get_setting("AI_PROVIDER", "gemini")
AI_MODEL = get_setting("AI_MODEL", "gemini-2.5-flash")
