import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("DEALMIND_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="DealMind AI", page_icon="🏃", layout="wide")
st.title("🏃 DealMind AI")
st.caption("Copilot de ofertas para corrida & fitness — MVP v0.2")

source_label = st.radio(
    "Fonte de dados",
    ["Demo local", "Mercado Livre API"],
    horizontal=True,
)
source = "demo" if source_label == "Demo local" else "mercado_livre"

with st.form("search_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input(
            "O que você procura?",
            placeholder="Ex.: tênis de corrida, relógio esportivo, fone para treino"
        )
    with col2:
        max_price = st.number_input(
            "Orçamento máximo (R$)", min_value=0.0, value=500.0, step=50.0
        )
    submitted = st.form_submit_button("Buscar ofertas", type="primary")

if submitted:
    if not query.strip():
        st.warning("Digite o produto que deseja procurar.")
    else:
        try:
            params = {"q": query, "source": source, "limit": 20}
            if max_price > 0:
                params["max_price"] = max_price

            response = requests.get(
                f"{API_URL}/products/search", params=params, timeout=20
            )

            if response.status_code == 503:
                st.warning(
                    "A integração com Mercado Livre ainda não está configurada. "
                    "Adicione MELI_ACCESS_TOKEN ao arquivo .env."
                )
            else:
                response.raise_for_status()
                data = response.json()
                products = data["products"]
                st.session_state["products"] = products
                if not products:
                    st.info("Nenhuma oferta encontrada para esses critérios.")
        except requests.RequestException as exc:
            st.error(f"Erro ao consultar a API do DealMind: {exc}")

products = st.session_state.get("products", [])

if products:
    st.subheader("Ofertas encontradas")
    rows = [{
        "Produto": item["name"],
        "Loja": item.get("store", "Mercado Livre"),
        "Preço": f"R$ {item['price']:,.2f}",
        "Desconto": f"{item.get('discount_percent', 0):.1f}%",
        "Deal Score": f"{item.get('deal_score', 0):.1f}/100",
    } for item in products]

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    best = products[0]
    st.success(
        f"Melhor oportunidade encontrada: **{best['name']}** "
        f"por **R$ {best['price']:,.2f}** — "
        f"Deal Score **{best.get('deal_score', 0)}/100**."
    )

    if best.get("url"):
        st.link_button("Ver oferta", best["url"])

    st.divider()
    st.subheader("🔔 Criar alerta de preço")

    product_options = {
        f"{item['name']} — R$ {item['price']:,.2f}": item for item in products
    }
    selected_label = st.selectbox("Produto", list(product_options.keys()))
    selected = product_options[selected_label]

    target_price = st.number_input(
        "Preço-alvo",
        min_value=1.0,
        value=max(1.0, round(selected["price"] * 0.9, 2)),
        step=10.0,
    )

    contact = st.text_input(
        "Telegram",
        placeholder="@seu_usuario — integração será ativada na v0.3"
    )

    if st.button("Criar alerta"):
        try:
            response = requests.post(
                f"{API_URL}/alerts",
                json={
                    "product_id": selected["id"],
                    "target_price": target_price,
                    "contact": contact or None,
                },
                timeout=10,
            )
            response.raise_for_status()
            alert = response.json()
            st.success(
                f"Alerta #{alert['id']} registrado para R$ {alert['target_price']:,.2f}."
            )
        except requests.RequestException:
            st.error("Não foi possível registrar o alerta.")
