from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class OAuthTokenState:
    access_token: str | None = None
    refresh_token: str | None = None
    expires_at: datetime | None = None


_state = OAuthTokenState()


def save_tokens(
    access_token: str,
    refresh_token: str | None = None,
    expires_in: int | None = None,
) -> None:
    _state.access_token = access_token
    _state.refresh_token = refresh_token

    if expires_in:
        _state.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    else:
        _state.expires_at = None


def get_access_token() -> str | None:
    if not _state.access_token:
        return None

    if _state.expires_at and datetime.now(timezone.utc) >= _state.expires_at:
        return None

    return _state.access_token


def get_refresh_token() -> str | None:
    return _state.refresh_token


def token_status() -> dict:
    return {
        "authenticated": bool(get_access_token()),
        "refresh_token_available": bool(_state.refresh_token),
        "expires_at": _state.expires_at.isoformat() if _state.expires_at else None,
    }
