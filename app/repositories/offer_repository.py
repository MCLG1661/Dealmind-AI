from datetime import datetime, timezone
from app.database.db import get_connection
from app.integrations.mercado_livre import MercadoLivreOffer

def save_offer_snapshot(offer: MercadoLivreOffer) -> None:
    captured_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            '''
            INSERT INTO offer_history (
                external_id, title, price, original_price,
                permalink, category_id, captured_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                offer.external_id, offer.title, offer.price,
                offer.original_price, offer.permalink,
                offer.category_id, captured_at,
            ),
        )
        conn.commit()

def get_price_history(external_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            '''
            SELECT external_id, title, price, original_price,
                   permalink, category_id, captured_at
            FROM offer_history
            WHERE external_id = ?
            ORDER BY captured_at ASC
            ''',
            (external_id,),
        ).fetchall()
    return [dict(row) for row in rows]
