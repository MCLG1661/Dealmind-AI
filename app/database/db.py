import os
import sqlite3
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


DB_PATH = Path(__file__).resolve().parents[2] / "data" / "dealmind.db"


def get_database_url() -> str | None:
    value = os.getenv("DATABASE_URL")
    return value.strip() if value else None


def is_postgres() -> bool:
    return bool(get_database_url())


def get_connection():
    database_url = get_database_url()

    if database_url:
        return psycopg.connect(
            database_url,
            row_factory=dict_row,
        )

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        if is_postgres():
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id BIGSERIAL PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    target_price DOUBLE PRECISION NOT NULL,
                    contact TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP::text
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offer_history (
                    id BIGSERIAL PRIMARY KEY,
                    external_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    original_price DOUBLE PRECISION,
                    permalink TEXT NOT NULL,
                    category_id TEXT,
                    captured_at TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    singleton_key INTEGER PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    expires_at TEXT,
                    updated_at TEXT NOT NULL,
                    CHECK (singleton_key = 1)
                )
                """
            )

        else:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    contact TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offer_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    external_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    original_price REAL,
                    permalink TEXT NOT NULL,
                    category_id TEXT,
                    captured_at TEXT NOT NULL
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS oauth_tokens (
                    singleton_key INTEGER PRIMARY KEY,
                    access_token TEXT NOT NULL,
                    refresh_token TEXT,
                    expires_at TEXT,
                    updated_at TEXT NOT NULL,
                    CHECK (singleton_key = 1)
                )
                """
            )

        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_offer_history_external_id
            ON offer_history (external_id)
            """
        )

        conn.commit()