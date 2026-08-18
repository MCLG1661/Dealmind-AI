from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import requests

from app.database.db import get_connection, is_postgres


TOKEN_URL = "https://api.mercadolibre.com/oauth/token"


def _placeholder() -> str:
    return "%s" if is_postgres() else "?"


def save_tokens(
    access_token: str,
    refresh_token: str | None = None,
    expires_in: int | None = None,
) -> None:
    expires_at = None

    if expires_in:
        expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        ).isoformat()

    updated_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        if is_postgres():
            conn.execute(
                """
                INSERT INTO oauth_tokens (
                    singleton_key,
                    access_token,
                    refresh_token,
                    expires_at,
                    updated_at
                )
                VALUES (1, %s, %s, %s, %s)
                ON CONFLICT (singleton_key)
                DO UPDATE SET
                    access_token = EXCLUDED.access_token,
                    refresh_token = COALESCE(
                        EXCLUDED.refresh_token,
                        oauth_tokens.refresh_token
                    ),
                    expires_at = EXCLUDED.expires_at,
                    updated_at = EXCLUDED.updated_at
                """,
                (
                    access_token,
                    refresh_token,
                    expires_at,
                    updated_at,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO oauth_tokens (
                    singleton_key,
                    access_token,
                    refresh_token,
                    expires_at,
                    updated_at
                )
                VALUES (1, ?, ?, ?, ?)
                ON CONFLICT(singleton_key)
                DO UPDATE SET
                    access_token = excluded.access_token,
                    refresh_token = COALESCE(
                        excluded.refresh_token,
                        oauth_tokens.refresh_token
                    ),
                    expires_at = excluded.expires_at,
                    updated_at = excluded.updated_at
                """,
                (
                    access_token,
                    refresh_token,
                    expires_at,
                    updated_at,
                ),
            )

        conn.commit()


def _load_tokens() -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                access_token,
                refresh_token,
                expires_at,
                updated_at
            FROM oauth_tokens
            WHERE singleton_key = 1
            """
        ).fetchone()

    return dict(row) if row else None


def get_refresh_token() -> str | None:
    token_data = _load_tokens()

    if not token_data:
        return None

    return token_data.get("refresh_token")


def _refresh_access_token(refresh_token: str) -> str | None:
    client_id = os.getenv("MELI_CLIENT_ID")
    client_secret = os.getenv("MELI_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    payload = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
    }

    try:
        response = requests.post(
            TOKEN_URL,
            data=payload,
            timeout=15,
        )
        response.raise_for_status()
        token_data = response.json()
    except requests.RequestException:
        return None

    access_token = token_data.get("access_token")

    if not access_token:
        return None

    save_tokens(
        access_token=access_token,
        refresh_token=token_data.get("refresh_token") or refresh_token,
        expires_in=token_data.get("expires_in"),
    )

    return access_token


def get_access_token() -> str | None:
    token_data = _load_tokens()

    if not token_data:
        return None

    access_token = token_data.get("access_token")
    expires_at_raw = token_data.get("expires_at")

    if not access_token:
        return None

    if not expires_at_raw:
        return access_token

    expires_at = datetime.fromisoformat(expires_at_raw)

    if datetime.now(timezone.utc) < expires_at:
        return access_token

    refresh_token = token_data.get("refresh_token")

    if not refresh_token:
        return None

    return _refresh_access_token(refresh_token)


def token_status() -> dict:
    token_data = _load_tokens()

    if not token_data:
        return {
            "authenticated": False,
            "refresh_token_available": False,
            "expires_at": None,
        }

    access_token = get_access_token()

    refreshed_data = _load_tokens() or token_data

    return {
        "authenticated": bool(access_token),
        "refresh_token_available": bool(
            refreshed_data.get("refresh_token")
        ),
        "expires_at": refreshed_data.get("expires_at"),
    }