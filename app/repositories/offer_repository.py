from datetime import datetime, timezone

from app.database.db import get_connection, is_postgres
from app.integrations.mercado_livre import MercadoLivreOffer

def save_price_snapshot(
    external_id: str,
    title: str,
    price: float,
    original_price: float | None,
    permalink: str,
    category_id: str | None = None,
) -> dict:
    captured_at = datetime.now(timezone.utc).isoformat()

    with get_connection() as conn:
        if is_postgres():
            row = conn.execute("""
                INSERT INTO offer_history (
                    external_id, title, price, original_price,
                    permalink, category_id, captured_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, external_id, title, price, original_price,
                          permalink, category_id, captured_at
            """, (
                external_id, title, price, original_price,
                permalink, category_id, captured_at,
            )).fetchone()
        else:
            cursor = conn.execute("""
                INSERT INTO offer_history (
                    external_id, title, price, original_price,
                    permalink, category_id, captured_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                external_id, title, price, original_price,
                permalink, category_id, captured_at,
            ))
            row = conn.execute("""
                SELECT id, external_id, title, price, original_price,
                       permalink, category_id, captured_at
                FROM offer_history
                WHERE id = ?
            """, (cursor.lastrowid,)).fetchone()
        conn.commit()
    return dict(row)

def save_offer_snapshot(offer: MercadoLivreOffer) -> dict:
    return save_price_snapshot(
        external_id=offer.external_id,
        title=offer.title,
        price=offer.price,
        original_price=offer.original_price,
        permalink=offer.permalink,
        category_id=offer.category_id,
    )

def get_price_history(external_id: str) -> list[dict]:
    placeholder = "%s" if is_postgres() else "?"
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT id, external_id, title, price, original_price,
                   permalink, category_id, captured_at
            FROM offer_history
            WHERE external_id = {placeholder}
            ORDER BY captured_at ASC
            """,
            (external_id,),
        ).fetchall()
    return [dict(row) for row in rows]
