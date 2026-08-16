from app.database.db import get_connection, is_postgres

def create_alert(product_id: str, target_price: float, contact: str | None = None) -> dict:
    with get_connection() as conn:
        if is_postgres():
            row = conn.execute("""
                INSERT INTO price_alerts (product_id, target_price, contact)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (product_id, target_price, contact)).fetchone()
        else:
            cursor = conn.execute("""
                INSERT INTO price_alerts (product_id, target_price, contact)
                VALUES (?, ?, ?)
            """, (product_id, target_price, contact))
            row = conn.execute(
                "SELECT * FROM price_alerts WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        conn.commit()
    return dict(row)

def list_alerts() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM price_alerts ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]

def get_active_alerts_for_product(product_id: str) -> list[dict]:
    placeholder = "%s" if is_postgres() else "?"
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT *
            FROM price_alerts
            WHERE product_id = {placeholder}
              AND active = 1
            ORDER BY id ASC
            """,
            (product_id,),
        ).fetchall()
    return [dict(row) for row in rows]

def deactivate_alert(alert_id: int) -> None:
    placeholder = "%s" if is_postgres() else "?"
    with get_connection() as conn:
        conn.execute(
            f"UPDATE price_alerts SET active = 0 WHERE id = {placeholder}",
            (alert_id,),
        )
        conn.commit()
