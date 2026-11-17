
import secrets
import sqlite3
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
import streamlit as st

from config.settings import (
    STRAVA_CLIENT_ID,
    STRAVA_CLIENT_SECRET,
    STRAVA_REDIRECT_URI,
)

AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"

DB_PATH = Path(__file__).resolve().parents[1] / "fyrst.db"
OAUTH_STATE_TTL = 600  # 10 minutos


def _get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS oauth_states (
            state TEXT PRIMARY KEY,
            created_at INTEGER NOT NULL
        )
    """)
    return conn


def get_authorization_url():
    """Genera una URL OAuth y guarda el state temporalmente en SQLite."""
    state = secrets.token_urlsafe(32)

    with _get_db_connection() as conn:
        # Limpiar estados antiguos
        conn.execute(
            "DELETE FROM oauth_states WHERE created_at < ?",
            (int(time.time()) - OAUTH_STATE_TTL,)
        )
        conn.execute(
            "INSERT INTO oauth_states (state, created_at) VALUES (?, ?)",
            (state, int(time.time()))
        )

    params = {
        "client_id": STRAVA_CLIENT_ID,
        "redirect_uri": STRAVA_REDIRECT_URI,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "read,activity:read_all",
        "state": state,
    }

    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def _validate_and_consume_state(state: str):
    """Valida el state y lo elimina para impedir su reutilización."""
    if not state:
        raise ValueError("No se ha recibido el estado OAuth.")

    with _get_db_connection() as conn:
        row = conn.execute(
            "SELECT created_at FROM oauth_states WHERE state = ?",
            (state,)
        ).fetchone()

        if row is None:
            raise ValueError("OAuth state inválido o ya utilizado.")

        created_at = row[0]

        conn.execute(
            "DELETE FROM oauth_states WHERE state = ?",
            (state,)
        )

    if int(time.time()) - created_at > OAUTH_STATE_TTL:
        raise ValueError("El intento de autenticación ha caducado. Vuelve a conectar Strava.")


def exchange_code(code: str, state: str):
    """Intercambia el authorization code por los tokens de Strava."""
    _validate_and_consume_state(state)

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
        timeout=20,
    )

    response.raise_for_status()
    token_data = response.json()

    st.session_state.strava_tokens = {
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "expires_at": token_data["expires_at"],
    }

    st.session_state.athlete = token_data["athlete"]

    return token_data


def refresh_access_token():
    """Renueva el token y guarda también el nuevo refresh token."""
    tokens = st.session_state.get("strava_tokens")

    if not tokens:
        raise RuntimeError("Usuario no autenticado.")

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": STRAVA_CLIENT_ID,
            "client_secret": STRAVA_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": tokens["refresh_token"],
        },
        timeout=20,
    )

    response.raise_for_status()
    new_tokens = response.json()

    st.session_state.strava_tokens = {
        "access_token": new_tokens["access_token"],
        "refresh_token": new_tokens["refresh_token"],
        "expires_at": new_tokens["expires_at"],
    }

    return new_tokens["access_token"]


def get_valid_access_token():
    """Devuelve un access token válido, renovándolo si es necesario."""
    tokens = st.session_state.get("strava_tokens")

    if not tokens:
        raise RuntimeError("No existe una sesión Strava.")

    if tokens["expires_at"] <= time.time() + 300:
        return refresh_access_token()

    return tokens["access_token"]


def logout():
    """Limpia la sesión local."""
    for key in [
        "strava_tokens",
        "athlete",
        "activities",
        "oauth_state",
    ]:
        st.session_state.pop(key, None)
