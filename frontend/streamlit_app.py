from __future__ import annotations

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st


API_URL = os.getenv(
    "DEALMIND_API_URL",
    "https://dealmind-ai-9hme.onrender.com",
).rstrip("/")

LOGO_PATH = "assets/dealmind-logo-horizontal.png"

st.set_page_config(
    page_title="DealMind AI",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        :root {
            --dm-bg: #f6f8fb;
            --dm-surface: #ffffff;
            --dm-text: #111827;
            --dm-muted: #6b7280;
            --dm-border: #e5e7eb;
        }

        .stApp {
            background:
                radial-gradient(circle at 90% 0%, rgba(79,70,229,.08), transparent 28%),
                radial-gradient(circle at 0% 10%, rgba(14,165,233,.06), transparent 24%),
                var(--dm-bg);
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.25rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 { letter-spacing: -0.025em; }

        .dm-hero {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #312e81 100%);
            border-radius: 28px;
            padding: 34px 38px;
            color: white;
            box-shadow: 0 18px 50px rgba(15, 23, 42, .14);
            margin-bottom: 1rem;
        }

        .dm-hero h1 {
            margin: 0 0 8px 0;
            color: white;
            font-size: 2.35rem;
            line-height: 1.05;
        }

        .dm-hero p {
            margin: 0;
            max-width: 780px;
            color: rgba(255,255,255,.76);
            line-height: 1.55;
            font-size: 1rem;
        }

        .dm-chip {
            display: inline-block;
            padding: 6px 11px;
            margin-bottom: 14px;
            border: 1px solid rgba(255,255,255,.18);
            border-radius: 999px;
            background: rgba(255,255,255,.10);
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .04em;
            text-transform: uppercase;
        }

        .dm-section { margin-bottom: 1rem; }

        .dm-section-title {
            color: var(--dm-text);
            font-size: 1.15rem;
            font-weight: 850;
            margin-bottom: .2rem;
        }

        .dm-muted {
            color: var(--dm-muted);
            font-size: .92rem;
        }

        .dm-product-title {
            color: var(--dm-text);
            font-size: 1.05rem;
            font-weight: 850;
            line-height: 1.3;
            margin-bottom: 3px;
        }

        .dm-store {
            color: var(--dm-muted);
            font-size: .88rem;
            margin-bottom: 8px;
        }

        .dm-price {
            color: var(--dm-text);
            font-size: 1.65rem;
            font-weight: 900;
            letter-spacing: -.025em;
            margin: 5px 0;
        }

        .dm-score {
            display: inline-block;
            border-radius: 999px;
            padding: 7px 11px;
            font-size: .82rem;
            font-weight: 850;
        }

        .dm-excellent {
            color: #047857;
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
        }

        .dm-good {
            color: #1d4ed8;
            background: #eff6ff;
            border: 1px solid #bfdbfe;
        }

        .dm-fair {
            color: #a16207;
            background: #fffbeb;
            border: 1px solid #fde68a;
        }

        .dm-weak {
            color: #b91c1c;
            background: #fef2f2;
            border: 1px solid #fecaca;
        }

        .dm-tech-note {
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            background: #ffffff;
            color: #64748b;
            font-size: .86rem;
        }

        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid var(--dm-border);
            border-radius: 18px;
            padding: 14px 16px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, .04);
        }

        div[data-testid="stMetricLabel"] { color: var(--dm-muted); }

        div[data-testid="stForm"] {
            background: white;
            border: 1px solid var(--dm-border);
            border-radius: 22px;
            padding: 18px 18px 10px 18px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, .045);
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 22px !important;
            border-color: var(--dm-border) !important;
            background: white;
            box-shadow: 0 8px 26px rgba(15, 23, 42, .04);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: .35rem;
            background: white;
            border: 1px solid var(--dm-border);
            padding: .35rem;
            border-radius: 16px;
            margin-bottom: 1.1rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 12px;
            padding: .55rem 1rem;
            height: auto;
            color: #475569;
            font-weight: 750;
        }

        .stTabs [aria-selected="true"] {
            background: #eef2ff !important;
            color: #3730a3 !important;
            border: 1px solid #c7d2fe !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.08);
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: #f8fafc !important;
            color: #111827 !important;
        }

        .stButton > button,
        .stLinkButton > a {
            border-radius: 12px !important;
            font-weight: 800 !important;
        }

        .dm-footer {
            color: #94a3b8;
            text-align: center;
            font-size: .78rem;
            margin-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def api_get(path: str, params: dict | None = None, silent: bool = False):
    try:
        response = requests.get(
            f"{API_URL}{path}",
            params=params,
            timeout=25,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        if not silent:
            st.error(f"Não foi possível consultar a API: {exc}")
        return None


def api_post(path: str, payload: dict):
    try:
        response = requests.post(
            f"{API_URL}{path}",
            json=payload,
            timeout=25,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Não foi possível enviar os dados: {exc}")
        return None


def brl(value: Any) -> str:
    if value is None:
        return "—"
    return (
        f"R$ {float(value):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def provider_name(value: str) -> str:
    return {
        "serper": "Google Shopping",
        "mercado_livre": "Mercado Livre",
        "demo": "Demo",
    }.get(value, value)


def opportunity_label(value: str | None) -> str:
    return {
        "excellent": "🟢 Excelente",
        "good": "🔵 Boa",
        "fair": "🟡 Regular",
        "weak": "🔴 Fraca",
    }.get(value or "", value or "—")


def score_meta(score: float) -> tuple[str, str]:
    if score >= 75:
        return "Excelente oportunidade", "dm-excellent"
    if score >= 60:
        return "Boa oportunidade", "dm-good"
    if score >= 50:
        return "Oportunidade regular", "dm-fair"
    return "Pouco atrativa", "dm-weak"


def recommendation_meta(value: str | None) -> tuple[str, str]:
    mapping = {
        "buy": ("COMPRAR", "dm-excellent"),
        "consider": ("CONSIDERAR COMPRA", "dm-good"),
        "wait": ("AGUARDAR", "dm-fair"),
        "avoid": ("EVITAR AGORA", "dm-weak"),
    }
    return mapping.get(
        value or "",
        (str(value or "—").upper(), "dm-fair"),
    )


if "last_search" not in st.session_state:
    st.session_state.last_search = None

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

if "watch_product_id" not in st.session_state:
    st.session_state.watch_product_id = "TENIS-001"

if "alert_product" not in st.session_state:
    st.session_state.alert_product = "TENIS-001"

if "advisor_product_id" not in st.session_state:
    st.session_state.advisor_product_id = "TENIS-001"


logo_col, hero_col = st.columns([1.55, 4])

with logo_col:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=440)

with hero_col:
    st.markdown(
        """
        <div class="dm-hero">
            <div class="dm-chip">Price Intelligence Copilot</div>
            <h1>Compre melhor. No momento certo.</h1>
            <p>
                Encontre ofertas reais, compare preços, acompanhe histórico e
                transforme sinais de mercado em decisões de compra mais inteligentes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

health = api_get("/health", silent=True)
api_online = bool(health)

tab_discover, tab_watch, tab_alerts, tab_advisor, tab_status = st.tabs(
    [
        "🔎 Descobrir",
        "📈 Monitorados",
        "🔔 Alertas",
        "🧠 Advisor",
        "⚙️ Status",
    ]
)


with tab_discover:
    st.markdown(
        """
        <div class="dm-section">
            <div class="dm-section-title">Encontre a melhor oportunidade</div>
            <div class="dm-muted">
                Busque produtos reais e deixe o Deal Score priorizar as ofertas mais interessantes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("search_form"):
        r1 = st.columns([2.4, 1, 1])

        with r1[0]:
            query = st.text_input(
                "Produto",
                placeholder="Ex.: tênis de corrida, smartwatch, halteres...",
            )

        with r1[1]:
            max_price = st.number_input(
                "Preço máximo",
                min_value=0.0,
                value=500.0,
                step=50.0,
            )

        with r1[2]:
            limit = st.selectbox(
                "Resultados",
                [6, 8, 10, 12, 16, 20],
                index=2,
            )

        r2 = st.columns([1.2, 1.2, 1.6])

        with r2[0]:
            source = st.selectbox(
                "Fonte",
                ["serper", "demo", "mercado_livre"],
                format_func=provider_name,
            )

        with r2[1]:
            sort_by = st.selectbox(
                "Ordenar por",
                [
                    "Melhor oportunidade",
                    "Menor preço",
                    "Melhor avaliação",
                ],
            )

        with r2[2]:
            search_clicked = st.form_submit_button(
                "Buscar ofertas",
                type="primary",
                use_container_width=True,
            )

    if search_clicked and query.strip():
        params = {
            "q": query.strip(),
            "source": source,
            "limit": int(limit),
        }

        if max_price > 0:
            params["max_price"] = max_price

        with st.spinner("Buscando, comparando e analisando ofertas..."):
            response = api_get("/products/search", params=params)

        if isinstance(response, dict):
            st.session_state.last_search = response

    response = st.session_state.last_search

    if isinstance(response, dict):
        products = response.get("products", [])

        if products:
            if sort_by == "Menor preço":
                products = sorted(
                    products,
                    key=lambda item: float(item.get("price") or 0),
                )
            elif sort_by == "Melhor avaliação":
                products = sorted(
                    products,
                    key=lambda item: (
                        -float(item.get("rating") or 0),
                        -int(item.get("rating_count") or 0),
                    ),
                )
            else:
                products = sorted(
                    products,
                    key=lambda item: -float(item.get("deal_score") or 0),
                )

            prices = [
                float(item["price"])
                for item in products
                if item.get("price") is not None
            ]
            scores = [
                float(item.get("deal_score") or 0)
                for item in products
            ]

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Ofertas", len(products))
            k2.metric("Menor preço", brl(min(prices) if prices else None))
            k3.metric(
                "Preço médio",
                brl(sum(prices) / len(prices) if prices else None),
            )
            k4.metric(
                "Melhor Deal Score",
                f"{max(scores):.1f}/100" if scores else "—",
            )

            st.markdown("### Ranking DealMind")

            for start in range(0, len(products), 2):
                cards = st.columns(2)

                for offset, card in enumerate(cards):
                    idx = start + offset
                    if idx >= len(products):
                        continue

                    product = products[idx]
                    score = float(product.get("deal_score") or 0)
                    label, css_class = score_meta(score)
                    current_price = float(product.get("price") or 0)
                    historical_average = product.get("historical_average")

                    with card:
                        with st.container(border=True):
                            media_col, data_col = st.columns([1, 1.8])

                            with media_col:
                                if product.get("thumbnail"):
                                    st.image(
                                        product["thumbnail"],
                                        use_container_width=True,
                                    )
                                else:
                                    st.markdown("## 🛍️")

                            with data_col:
                                st.markdown(
                                    f'<div class="dm-product-title">{product.get("name", "Produto")}</div>',
                                    unsafe_allow_html=True,
                                )
                                st.markdown(
                                    f'<div class="dm-store">{product.get("store", "Loja não informada")}</div>',
                                    unsafe_allow_html=True,
                                )
                                st.markdown(
                                    f'<div class="dm-price">{brl(current_price)}</div>',
                                    unsafe_allow_html=True,
                                )

                                rating = product.get("rating")
                                rating_count = product.get("rating_count")

                                if rating is not None:
                                    rating_text = f"⭐ {float(rating):.1f}"
                                    if rating_count:
                                        rating_text += (
                                            f" · {int(rating_count)} avaliações"
                                        )
                                    st.caption(rating_text)
                                else:
                                    st.caption("Sem avaliações disponíveis")

                            score_col, label_col = st.columns([1, 1.45])

                            with score_col:
                                st.metric(
                                    "Deal Score",
                                    f"{score:.1f}/100",
                                )

                            with label_col:
                                st.markdown(
                                    f'<span class="dm-score {css_class}">{label}</span>',
                                    unsafe_allow_html=True,
                                )

                            if historical_average is not None:
                                hist = float(historical_average)
                                pct = (
                                    ((current_price - hist) / hist) * 100
                                    if hist
                                    else 0
                                )

                                if pct < -0.5:
                                    st.success(
                                        f"{abs(pct):.1f}% abaixo da média histórica ({brl(hist)})."
                                    )
                                elif pct > 0.5:
                                    st.warning(
                                        f"{pct:.1f}% acima da média histórica ({brl(hist)})."
                                    )
                                else:
                                    st.caption(
                                        f"Preço alinhado à média histórica: {brl(hist)}."
                                    )
                            else:
                                st.caption(
                                    "Histórico sendo construído pelo DealMind."
                                )

                            action1, action2 = st.columns(2)

                            with action1:
                                if product.get("url"):
                                    st.link_button(
                                        "Ver oferta",
                                        product["url"],
                                        use_container_width=True,
                                    )

                            with action2:
                                if st.button(
                                    "Monitorar preço",
                                    key=f"monitor_{product.get('id')}_{idx}",
                                    use_container_width=True,
                                ):
                                    st.session_state.selected_product = product
                                    selected_id = str(product.get("id"))
                                    st.session_state.watch_product_id = selected_id
                                    st.session_state.alert_product = selected_id
                                    st.session_state.advisor_product_id = selected_id

                                    snapshot_payload = {
                                        "product_id": str(product.get("id")),
                                        "title": product.get(
                                            "name",
                                            "Produto monitorado",
                                        ),
                                        "price": float(
                                            product.get("price") or 0
                                        ),
                                        "original_price": (
                                            float(product["original_price"])
                                            if product.get("original_price") is not None
                                            else None
                                        ),
                                        "url": product.get("url"),
                                        "category_id": (
                                            product.get("category_id")
                                            or "shopping"
                                        ),
                                    }

                                    snapshot = api_post(
                                        "/monitoring/snapshots",
                                        snapshot_payload,
                                    )

                                    if snapshot:
                                        st.success(
                                            "Produto adicionado aos monitorados "
                                            "com sucesso."
                                        )

            selected = st.session_state.selected_product

            if selected:
                st.divider()
                st.markdown("### 🔔 Criar alerta para a oferta selecionada")

                with st.container(border=True):
                    a1, a2, a3 = st.columns([2, 1, 1.2])

                    with a1:
                        st.write(f"**{selected.get('name', 'Produto')}**")
                        st.caption(
                            f"{selected.get('store', 'Loja')} · "
                            f"preço atual {brl(selected.get('price'))}"
                        )

                    with a2:
                        default_target = max(
                            0.01,
                            round(
                                float(selected.get("price") or 0) * 0.92,
                                2,
                            ),
                        )
                        quick_target = st.number_input(
                            "Quero pagar até",
                            min_value=0.01,
                            value=default_target,
                            step=10.0,
                            key="quick_target",
                        )

                    with a3:
                        quick_contact = st.text_input(
                            "Contato",
                            placeholder="e-mail ou identificador",
                            key="quick_contact",
                        )

                    if st.button(
                        "Ativar alerta",
                        type="primary",
                        use_container_width=True,
                    ):
                        alert = api_post(
                            "/alerts",
                            {
                                "product_id": str(selected.get("id")),
                                "target_price": quick_target,
                                "contact": quick_contact or None,
                            },
                        )

                        if alert:
                            st.success(
                                f"Alerta criado para {brl(quick_target)}."
                            )
        else:
            st.info("Nenhuma oferta encontrada com os filtros informados.")


with tab_watch:
    st.markdown(
        """
        <div class="dm-section">
            <div class="dm-section-title">Histórico e inteligência de preço</div>
            <div class="dm-muted">
                Consulte um produto acompanhado e veja sua evolução ao longo do tempo.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    product_id = st.text_input(
        "Product ID",
        key="watch_product_id",
    )

    if product_id:
        analysis = api_get(
            f"/monitoring/{product_id}",
            silent=True,
        )
        history_data = api_get(
            f"/monitoring/{product_id}/history",
            silent=True,
        )

        if isinstance(analysis, dict) and analysis.get("product_id"):
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Preço atual", brl(analysis.get("current_price")))
            m2.metric("Preço médio", brl(analysis.get("average_price")))
            m3.metric("Melhor preço", brl(analysis.get("minimum_price")))
            m4.metric(
                "Deal Score",
                f"{float(analysis.get('deal_score', 0)):.1f}/100",
            )

            chart_col, insight_col = st.columns([2.1, 1])

            with chart_col:
                st.markdown("### Evolução do preço")

                if (
                    isinstance(history_data, dict)
                    and history_data.get("history")
                ):
                    df = pd.DataFrame(history_data["history"])
                    df["captured_at"] = pd.to_datetime(
                        df["captured_at"],
                        errors="coerce",
                    )
                    df = (
                        df.dropna(subset=["captured_at"])
                        .sort_values("captured_at")
                    )

                    if not df.empty:
                        st.line_chart(
                            df.set_index("captured_at")[["price"]],
                            use_container_width=True,
                        )

                        table = df[
                            ["captured_at", "price", "original_price"]
                        ].copy()

                        table["captured_at"] = table[
                            "captured_at"
                        ].dt.strftime("%d/%m/%Y %H:%M")

                        table["price"] = table["price"].apply(brl)
                        table["original_price"] = table[
                            "original_price"
                        ].apply(brl)

                        table.columns = [
                            "Capturado em",
                            "Preço",
                            "Preço original",
                        ]

                        st.dataframe(
                            table,
                            use_container_width=True,
                            hide_index=True,
                        )
                else:
                    st.info("Ainda não há histórico suficiente.")

            with insight_col:
                st.markdown("### Leitura rápida")
                st.metric(
                    "Oportunidade",
                    opportunity_label(analysis.get("opportunity")),
                )

                variation = float(
                    analysis.get(
                        "variation_vs_average_percent",
                        0,
                    )
                    or 0
                )

                if variation < 0:
                    st.success(
                        f"{abs(variation):.2f}% abaixo da média."
                    )
                elif variation > 0:
                    st.warning(
                        f"{variation:.2f}% acima da média."
                    )
                else:
                    st.info("Preço alinhado à média.")

                st.write(
                    f"**Observações:** {analysis.get('observations', 0)}"
                )
                st.write(
                    f"**Preço máximo:** {brl(analysis.get('maximum_price'))}"
                )

                if analysis.get("url"):
                    st.link_button(
                        "Abrir produto",
                        analysis["url"],
                        use_container_width=True,
                    )

        else:
            st.info(
                "Este produto ainda não possui análise consolidada. "
                "As buscas reais já alimentam o histórico automaticamente."
            )

    with st.expander("Registrar observação manual"):
        with st.form("manual_snapshot_form"):
            c1, c2 = st.columns(2)

            with c1:
                manual_product_id = st.text_input(
                    "Product ID",
                    value=product_id or "TENIS-001",
                )
                manual_title = st.text_input(
                    "Nome do produto",
                    value="Produto monitorado",
                )
                manual_price = st.number_input(
                    "Preço atual",
                    min_value=0.01,
                    value=299.90,
                    step=10.0,
                )

            with c2:
                manual_original_price = st.number_input(
                    "Preço original",
                    min_value=0.01,
                    value=449.90,
                    step=10.0,
                )
                manual_url = st.text_input(
                    "URL do produto",
                    value="https://example.com",
                )
                manual_category = st.text_input(
                    "Categoria",
                    value="shopping",
                )

            manual_submit = st.form_submit_button(
                "Registrar preço",
                type="primary",
            )

        if manual_submit:
            snapshot = api_post(
                "/monitoring/snapshots",
                {
                    "product_id": manual_product_id,
                    "title": manual_title,
                    "price": manual_price,
                    "original_price": manual_original_price,
                    "url": manual_url,
                    "category_id": manual_category or None,
                },
            )

            if snapshot:
                st.success("Preço registrado com sucesso.")


with tab_alerts:
    st.markdown(
        """
        <div class="dm-section">
            <div class="dm-section-title">Alertas de preço</div>
            <div class="dm-muted">
                Defina quanto você quer pagar e acompanhe os gatilhos ativos.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("alert_form"):
        a1, a2, a3 = st.columns([1.5, 1, 1.4])

        with a1:
            alert_product = st.text_input(
                "Product ID",
                key="alert_product",
            )

        with a2:
            target_price = st.number_input(
                "Preço-alvo",
                min_value=0.01,
                value=320.00,
                step=10.0,
            )

        with a3:
            contact = st.text_input(
                "Contato",
                placeholder="e-mail ou identificador",
            )

        submit_alert = st.form_submit_button(
            "Criar alerta",
            type="primary",
            use_container_width=True,
        )

    if submit_alert:
        alert = api_post(
            "/alerts",
            {
                "product_id": alert_product,
                "target_price": target_price,
                "contact": contact or None,
            },
        )

        if alert:
            st.success(
                f"Alerta #{alert['id']} criado para "
                f"{brl(alert['target_price'])}."
            )

    alerts = api_get("/alerts", silent=True)

    if isinstance(alerts, list) and alerts:
        df_alerts = pd.DataFrame(alerts)

        active_count = (
            int(df_alerts["active"].sum())
            if "active" in df_alerts
            else 0
        )

        m1, m2 = st.columns(2)
        m1.metric("Alertas cadastrados", len(df_alerts))
        m2.metric("Alertas ativos", active_count)

        if "target_price" in df_alerts:
            df_alerts["target_price"] = df_alerts[
                "target_price"
            ].apply(brl)

        if "active" in df_alerts:
            df_alerts["Status"] = df_alerts["active"].apply(
                lambda value: "🟢 Ativo" if value else "✅ Disparado"
            )

        st.dataframe(
            df_alerts.rename(
                columns={
                    "id": "ID",
                    "product_id": "Produto",
                    "target_price": "Preço-alvo",
                    "contact": "Contato",
                    "created_at": "Criado em",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhum alerta cadastrado até o momento.")


with tab_advisor:
    st.markdown(
        """
        <div class="dm-section">
            <div class="dm-section-title">DealMind AI Advisor</div>
            <div class="dm-muted">
                Transforme histórico, Deal Score e comportamento de preço em uma recomendação objetiva.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    advisor_product_id = st.text_input(
        "Produto para análise",
        key="advisor_product_id",
    )

    if advisor_product_id:
        advisor = api_get(
            f"/advisor/{advisor_product_id}",
            silent=True,
        )

        if isinstance(advisor, dict) and advisor.get("available", True):
            recommendation = advisor.get("recommendation")
            recommendation_label, recommendation_class = (
                recommendation_meta(recommendation)
            )

            with st.container(border=True):
                c1, c2, c3 = st.columns([1.3, 1, 1])

                with c1:
                    st.markdown("### Recomendação")
                    st.markdown(
                        f'<span class="dm-score {recommendation_class}">'
                        f'{recommendation_label}</span>',
                        unsafe_allow_html=True,
                    )

                with c2:
                    st.metric(
                        "Confiança",
                        str(advisor.get("confidence", "—")).title(),
                    )

                with c3:
                    metrics = advisor.get("metrics", {})
                    deal_score = (
                        metrics.get("deal_score")
                        if isinstance(metrics, dict)
                        else None
                    )
                    st.metric(
                        "Deal Score",
                        f"{float(deal_score):.1f}/100"
                        if deal_score is not None
                        else "—",
                    )

                if advisor.get("summary"):
                    st.info(advisor["summary"])

                reasons = advisor.get("reasons", [])
                if reasons:
                    st.markdown("#### Por que o DealMind pensa assim?")
                    for reason in reasons:
                        st.write(f"• {reason}")

                metrics = advisor.get("metrics", {})
                if isinstance(metrics, dict) and metrics:
                    x1, x2, x3 = st.columns(3)
                    x1.metric(
                        "Preço atual",
                        brl(metrics.get("current_price")),
                    )
                    x2.metric(
                        "Média histórica",
                        brl(metrics.get("average_price")),
                    )
                    x3.metric(
                        "Melhor preço",
                        brl(metrics.get("minimum_price")),
                    )

                if advisor.get("disclaimer"):
                    st.caption(advisor["disclaimer"])
        else:
            st.info(
                "Ainda não há informação suficiente para gerar uma "
                "recomendação para este produto."
            )


with tab_status:
    st.markdown(
        """
        <div class="dm-section">
            <div class="dm-section-title">Status da plataforma</div>
            <div class="dm-muted">
                Dados técnicos ficam separados da experiência principal.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    s1, s2 = st.columns(2)
    s1.metric("API", "Online" if api_online else "Offline")
    s2.metric("Backend", "Render")

    providers = api_get("/providers", silent=True)

    if isinstance(providers, dict) and providers.get("providers"):
        provider_df = pd.DataFrame(providers["providers"]).copy()

        if "name" in provider_df:
            provider_df["name"] = provider_df["name"].apply(provider_name)

        st.markdown("### Providers")
        st.dataframe(
            provider_df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown(
        """
        <div class="dm-tech-note">
            Busca principal: Google Shopping via Serper ·
            Mercado Livre: integração autenticada ·
            Histórico e OAuth: PostgreSQL ·
            Backend: FastAPI no Render
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="dm-footer">
        DealMind AI · Price Intelligence Copilot · MVP
    </div>
    """,
    unsafe_allow_html=True,
)