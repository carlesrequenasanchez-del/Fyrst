
import requests

from core.auth import get_valid_access_token

STRAVA_API_URL = "https://www.strava.com/api/v3"


def get_activities(
    per_page: int = 200,
    max_pages: int | None = None,
) -> list[dict]:
    """
    Descarga las actividades del atleta autenticado.

    Strava permite un máximo de 200 actividades por página.
    Si max_pages es None, descarga todas las páginas disponibles.
    """
    if not 1 <= per_page <= 200:
        raise ValueError("per_page debe estar entre 1 y 200.")

    access_token = get_valid_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    activities = []
    page = 1

    while True:
        response = requests.get(
            f"{STRAVA_API_URL}/athlete/activities",
            headers=headers,
            params={
                "page": page,
                "per_page": per_page,
            },
            timeout=30,
        )

        # Si Strava rechaza el token, renovarlo y reintentar una vez.
        if response.status_code == 401:
            access_token = get_valid_access_token()
            headers["Authorization"] = f"Bearer {access_token}"

            response = requests.get(
                f"{STRAVA_API_URL}/athlete/activities",
                headers=headers,
                params={
                    "page": page,
                    "per_page": per_page,
                },
                timeout=30,
            )

        response.raise_for_status()

        batch = response.json()

        if not batch:
            break

        activities.extend(batch)

        if len(batch) < per_page:
            break

        page += 1

        if max_pages is not None and page > max_pages:
            break

    return activities
