import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("DEALMIND_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="DealMind AI", page_icon="📈", layout="wide")


def api_get(path: str, params: dict | None = None):
    try:
        response = requests.get(f"{API_URL}{path}", params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Erro ao consultar a API: {exc}")
        return None


def api_post(path: str, payload: dict):
    try:
        response = requests.post(f"{API_URL}{path}", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        st.error(f"Erro ao enviar dados para a API: {exc}")
        return None


def brl(value):
    if value is None:
        return "-"
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def opportunity_label(value):
    labels = {
        "excellent": "🟢 Excelente",
        "good": "🔵 Boa",
        "fair": "🟡 Regular",
        "weak": "🔴 Fraca",
    }
    return labels.get(value or "", value or "-")


st.image(
    "assets/dealmind-logo-horizontal.png",
    width=420,
)

st.caption(
    "Price Intelligence Copilot — monitoramento, histórico, alertas e recomendações de preço"
)

tab_dashboard, tab_monitor, tab_alerts, tab_search, tab_advisor = st.tabs(
    [
        "📊 Dashboard",
        "➕ Monitorar preço",
        "🔔 Alertas",
        "🔎 Busca / Providers",
        "🧠 AI Advisor",
    ]
)

with tab_dashboard:
    st.subheader("Dashboard de Price Intelligence")
    product_id = st.text_input("Produto monitorado", value="TENIS-001")

    analysis = api_get(f"/monitoring/{product_id}") if product_id else None
    history_data = api_get(f"/monitoring/{product_id}/history") if product_id else None

    if isinstance(analysis, dict) and analysis.get("product_id"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Preço atual", brl(analysis.get("current_price")))
        c2.metric("Preço médio", brl(analysis.get("average_price")))
        c3.metric("Melhor preço", brl(analysis.get("minimum_price")))
        c4.metric("Deal Score", f"{analysis.get('deal_score', 0):.1f} / 100")

        st.divider()
        left, right = st.columns([2, 1])

        with left:
            st.markdown("### Evolução do preço")
            if isinstance(history_data, dict) and history_data.get("history"):
                df = pd.DataFrame(history_data["history"])
                df["captured_at"] = pd.to_datetime(df["captured_at"], errors="coerce")
                df = df.dropna(subset=["captured_at"]).sort_values("captured_at")
                chart_df = df.set_index("captured_at")[["price"]]
                st.line_chart(chart_df, use_container_width=True)

                table = df[["captured_at", "price", "original_price"]].copy()
                table["captured_at"] = table["captured_at"].dt.strftime("%d/%m/%Y %H:%M")
                table["price"] = table["price"].apply(brl)
                table["original_price"] = table["original_price"].apply(brl)
                table.columns = ["Capturado em", "Preço", "Preço original"]
                st.dataframe(table, use_container_width=True, hide_index=True)

        with right:
            st.markdown("### Oportunidade")
            st.metric("Classificação", opportunity_label(analysis.get("opportunity")))
            variation = float(analysis.get("variation_vs_average_percent", 0))
            if variation < 0:
                st.success(f"O preço atual está {abs(variation):.2f}% abaixo da média.")
            elif variation > 0:
                st.warning(f"O preço atual está {variation:.2f}% acima da média.")
            else:
                st.info("O preço atual está igual à média observada.")

            st.write(f"**Observações:** {analysis.get('observations', 0)}")
            st.write(f"**Preço máximo:** {brl(analysis.get('maximum_price'))}")
            if analysis.get("url"):
                st.link_button("Abrir produto", analysis["url"], use_container_width=True)

with tab_monitor:
    st.subheader("Registrar nova observação de preço")

    with st.form("snapshot_form"):
        c1, c2 = st.columns(2)
        with c1:
            snapshot_product_id = st.text_input("Product ID", value="TENIS-001")
            snapshot_title = st.text_input("Nome do produto", value="Tênis de Corrida Demo")
            snapshot_price = st.number_input("Preço atual", min_value=0.01, value=299.90, step=10.0)
        with c2:
            snapshot_original_price = st.number_input("Preço original", min_value=0.01, value=449.90, step=10.0)
            snapshot_url = st.text_input("URL do produto", value="https://example.com/tenis-001")
            snapshot_category = st.text_input("Categoria", value="running")

        submitted = st.form_submit_button("Registrar preço", type="primary")

    if submitted:
        result = api_post(
            "/monitoring/snapshots",
            {
                "product_id": snapshot_product_id,
                "title": snapshot_title,
                "price": snapshot_price,
                "original_price": snapshot_original_price,
                "url": snapshot_url,
                "category_id": snapshot_category or None,
            },
        )
        if result:
            st.success("Preço registrado com sucesso.")
            analysis = result.get("analysis", {})
            triggered = result.get("triggered_alerts", [])
            c1, c2, c3 = st.columns(3)
            c1.metric("Deal Score", f"{analysis.get('deal_score', 0):.1f}/100")
            c2.metric("Preço médio", brl(analysis.get("average_price")))
            c3.metric("Observações", analysis.get("observations", 0))
            if triggered:
                st.error("🚨 Alerta de preço disparado!")
                for alert in triggered:
                    st.write(
                        f"Meta: **{brl(alert['target_price'])}** → "
                        f"preço atual: **{brl(alert['current_price'])}**"
                    )
            else:
                st.info("Nenhum alerta foi disparado nesta captura.")

with tab_alerts:
    st.subheader("Alertas de preço")

    with st.form("alert_form"):
        alert_product = st.text_input("Product ID", value="TENIS-001", key="alert_product")
        target_price = st.number_input("Preço-alvo", min_value=0.01, value=320.00, step=10.0)
        contact = st.text_input("Contato", value="teste@dealmind.ai")
        submit_alert = st.form_submit_button("Criar alerta", type="primary")

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
            st.success(f"Alerta #{alert['id']} criado para {brl(alert['target_price'])}.")

    st.divider()
    alerts = api_get("/alerts")
    if isinstance(alerts, list) and alerts:
        df_alerts = pd.DataFrame(alerts)
        df_alerts["target_price"] = df_alerts["target_price"].apply(brl)
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

with tab_search:
    st.subheader("🔎 Busca Inteligente de Ofertas")

    st.caption(
        "Pesquise produtos reais, compare preços e use o Deal Score "
        "para identificar as oportunidades mais interessantes."
    )

    providers = api_get("/providers")

    if isinstance(providers, dict) and providers.get("providers"):
        provider_df = pd.DataFrame(providers["providers"])

        st.markdown("### Providers disponíveis")

        st.dataframe(
            provider_df,
            use_container_width=True,
            hide_index=True,
        )

    st.info(
        "A busca principal utiliza o provider Serper / Google Shopping. "
        "O Mercado Livre permanece integrado para recursos autenticados."
    )

    with st.form("search_form"):
        c1, c2 = st.columns([2, 1])

        with c1:
            q = st.text_input(
                "O que você está procurando?",
                placeholder="Ex.: tênis de corrida",
            )

        with c2:
            max_price = st.number_input(
                "Preço máximo",
                min_value=0.0,
                value=500.0,
                step=50.0,
            )

        c3, c4 = st.columns(2)

        with c3:
            source = st.selectbox(
                "Provider",
                ["serper", "demo", "mercado_livre"],
                index=0,
            )

        with c4:
            limit = st.slider(
                "Quantidade de resultados",
                min_value=1,
                max_value=20,
                value=10,
            )

        do_search = st.form_submit_button(
            "🔎 Buscar ofertas",
            type="primary",
            use_container_width=True,
        )

    if do_search and q:
        params = {
            "q": q,
            "source": source,
            "limit": limit,
        }

        if max_price > 0:
            params["max_price"] = max_price

        with st.spinner("Buscando e analisando ofertas..."):
            result = api_get(
                "/products/search",
                params=params,
            )

        if isinstance(result, dict):
            products = result.get("products", [])

            if products:
                st.success(
                    f"{len(products)} ofertas encontradas para **{q}**."
                )

                st.markdown("### 🧠 Ranking DealMind")

                for index, product in enumerate(products, start=1):
                    score = float(product.get("deal_score", 0))
                    rating = product.get("rating")
                    rating_count = product.get("rating_count")
                    historical_average = product.get("historical_average")

                    if score >= 75:
                        score_label = "🟢 Excelente oportunidade"
                    elif score >= 60:
                        score_label = "🔵 Boa oportunidade"
                    elif score >= 50:
                        score_label = "🟡 Oportunidade regular"
                    else:
                        score_label = "🔴 Pouco atrativa"

                    with st.container(border=True):
                        image_col, info_col, score_col = st.columns(
                            [1, 3, 1.2]
                        )

                        with image_col:
                            thumbnail = product.get("thumbnail")

                            if thumbnail:
                                st.image(
                                    thumbnail,
                                    use_container_width=True,
                                )
                            else:
                                st.write("🛍️")

                        with info_col:
                            st.markdown(
                                f"### {index}. {product.get('name', 'Produto')}"
                            )

                            st.write(
                                f"**Loja:** {product.get('store', '-')}"
                            )

                            st.markdown(
                                f"## {brl(product.get('price'))}"
                            )

                            if rating is not None:
                                rating_text = f"⭐ {float(rating):.1f}"

                                if rating_count:
                                    rating_text += (
                                        f" · {int(rating_count)} avaliações"
                                    )

                                st.write(rating_text)

                            if historical_average is not None:
                                st.write(
                                    "**Média histórica:** "
                                    f"{brl(historical_average)}"
                                )
                            else:
                                st.caption(
                                    "Histórico sendo construído pelo DealMind."
                                )

                            product_url = product.get("url")

                            if product_url:
                                st.link_button(
                                    "🛒 Ver oferta",
                                    product_url,
                                )

                        with score_col:
                            st.metric(
                                "Deal Score",
                                f"{score:.1f}/100",
                            )

                            st.write(score_label)

                            discount = float(
                                product.get(
                                    "discount_percent",
                                    0,
                                )
                                or 0
                            )

                            if discount > 0:
                                st.success(
                                    f"{discount:.1f}% de desconto"
                                )

                st.divider()

                st.caption(
                    "O Deal Score considera competitividade de preço, "
                    "avaliações, volume de reviews, descontos disponíveis "
                    "e histórico observado pelo DealMind."
                )

            else:
                st.info(
                    "Nenhuma oferta encontrada com os filtros informados."
                )

with tab_advisor:
    st.subheader("🧠 DealMind AI Advisor")
    st.caption(
        "Recomendação de compra baseada no histórico de preços, Deal Score "
        "e comportamento observado do produto."
    )

    advisor_product_id = st.text_input(
        "Produto para análise",
        value="TENIS-001",
        key="advisor_product_id",
    )

    if advisor_product_id:
        advisor = api_get(f"/advisor/{advisor_product_id}")

        if isinstance(advisor, dict) and advisor.get("available"):
            recommendation = advisor.get("recommendation_label", "-")
            confidence = advisor.get("confidence", "-")
            summary = advisor.get("summary", "")
            reasons = advisor.get("reasons", [])
            metrics = advisor.get("metrics", {})

            st.divider()

            col1, col2, col3 = st.columns(3)

            with col1:
                if recommendation == "COMPRAR":
                    st.success(f"### 🟢 {recommendation}")
                elif recommendation == "CONSIDERAR COMPRA":
                    st.info(f"### 🔵 {recommendation}")
                elif recommendation == "ACOMPANHAR":
                    st.warning(f"### 🟡 {recommendation}")
                else:
                    st.error(f"### 🔴 {recommendation}")

            with col2:
                confidence_labels = {
                    "high": "Alta",
                    "medium": "Média",
                    "low": "Baixa",
                }
                st.metric(
                    "Confiança da análise",
                    confidence_labels.get(confidence, confidence),
                )

            with col3:
                st.metric(
                    "Deal Score",
                    f"{metrics.get('deal_score', 0):.1f} / 100",
                )

            st.markdown("### Resumo da recomendação")
            st.info(summary)

            st.markdown("### Por que o DealMind chegou a essa conclusão?")

            for reason in reasons:
                st.write(f"✓ {reason}")

            st.divider()

            st.markdown("### Métricas utilizadas")

            m1, m2, m3, m4 = st.columns(4)

            m1.metric(
                "Preço atual",
                brl(metrics.get("current_price")),
            )
            m2.metric(
                "Preço médio",
                brl(metrics.get("average_price")),
            )
            m3.metric(
                "Menor preço",
                brl(metrics.get("minimum_price")),
            )
            m4.metric(
                "Observações",
                metrics.get("observations", 0),
            )

            variation = float(
                metrics.get("variation_vs_average_percent", 0)
            )

            if variation < 0:
                st.success(
                    f"O preço atual está {abs(variation):.2f}% abaixo da média observada."
                )
            elif variation > 0:
                st.warning(
                    f"O preço atual está {variation:.2f}% acima da média observada."
                )
            else:
                st.info("O preço atual está igual à média observada.")

            st.caption(
                "A recomendação é baseada exclusivamente no histórico de preços "
                "disponível no DealMind AI. Quanto maior o histórico, maior pode "
                "ser a confiança da análise."
            )                
