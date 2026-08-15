from app.database.db import get_connection


def create_alert(
    product_id: str,
    target_price: float,
    contact: str | None = None
) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            '''
            INSERT INTO price_alerts (product_id, target_price, contact)
            VALUES (?, ?, ?)
            ''',
            (product_id, target_price, contact),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM price_alerts WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return dict(row)


def list_alerts() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM price_alerts ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]
