from __future__ import annotations

import os
import base64
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


        .dm-topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            background: rgba(255,255,255,.92);
            border: 1px solid var(--dm-border);
            border-radius: 22px;
            padding: 14px 18px;
            box-shadow: 0 10px 30px rgba(15, 23, 42, .05);
            margin-bottom: 1rem;
            backdrop-filter: blur(12px);
        }

        .dm-brand-wrap {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .dm-brand-title {
            color: #0f172a;
            font-size: 1.15rem;
            font-weight: 900;
            line-height: 1.05;
            margin-bottom: 3px;
        }

        .dm-brand-sub {
            color: #64748b;
            font-size: .82rem;
            font-weight: 600;
        }

        .dm-status-pill {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 7px 11px;
            border-radius: 999px;
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            color: #047857;
            font-size: .78rem;
            font-weight: 850;
            white-space: nowrap;
        }

        .dm-status-dot {
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: #10b981;
            box-shadow: 0 0 0 4px rgba(16,185,129,.12);
        }

        .dm-page-title {
            font-size: 2rem;
            line-height: 1.08;
            font-weight: 950;
            color: #0f172a;
            letter-spacing: -.035em;
            margin-bottom: 5px;
        }

        .dm-page-sub {
            color: #64748b;
            font-size: .96rem;
            margin-bottom: 1.2rem;
        }

        .dm-kpi-card {
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 18px 18px 16px 18px;
            min-height: 126px;
            box-shadow: 0 10px 28px rgba(15,23,42,.045);
        }

        .dm-kpi-icon {
            font-size: 1.18rem;
            margin-bottom: 12px;
        }

        .dm-kpi-label {
            color: #64748b;
            font-size: .78rem;
            font-weight: 750;
            margin-bottom: 5px;
        }

        .dm-kpi-value {
            color: #0f172a;
            font-size: 1.72rem;
            font-weight: 950;
            letter-spacing: -.035em;
            line-height: 1;
        }

        .dm-kpi-note {
            color: #94a3b8;
            font-size: .74rem;
            margin-top: 8px;
        }

        .dm-panel-title {
            color: #0f172a;
            font-size: 1.25rem;
            font-weight: 900;
            letter-spacing: -.02em;
            margin-bottom: .15rem;
        }

        .dm-panel-sub {
            color: #64748b;
            font-size: .86rem;
            margin-bottom: .8rem;
        }

        .dm-deal-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            padding: 17px;
            box-shadow: 0 8px 24px rgba(15,23,42,.04);
            min-height: 220px;
        }

        .dm-deal-rank {
            color: #94a3b8;
            font-size: .72rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: .055em;
            margin-bottom: 8px;
        }

        .dm-deal-name {
            color: #0f172a;
            font-size: .98rem;
            font-weight: 900;
            line-height: 1.27;
            min-height: 2.5em;
        }

        .dm-deal-price {
            color: #0f172a;
            font-size: 1.65rem;
            font-weight: 950;
            letter-spacing: -.035em;
            margin-top: 10px;
        }

        .dm-deal-meta {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-top: 10px;
        }

        .dm-mini-score {
            display: inline-block;
            border-radius: 999px;
            padding: 6px 9px;
            font-size: .74rem;
            font-weight: 900;
        }

        .dm-observation {
            color: #94a3b8;
            font-size: .74rem;
        }

        .dm-insight-card {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 58%, #312e81 100%);
            border-radius: 22px;
            padding: 22px;
            color: white;
            box-shadow: 0 14px 36px rgba(15,23,42,.12);
            min-height: 205px;
        }

        .dm-insight-label {
            color: #cbd5e1;
            font-size: .76rem;
            font-weight: 850;
            text-transform: uppercase;
            letter-spacing: .055em;
            margin-bottom: 10px;
        }

        .dm-insight-main {
            color: white;
            font-size: 1.28rem;
            line-height: 1.28;
            font-weight: 900;
            margin-bottom: 10px;
        }

        .dm-insight-text {
            color: #cbd5e1;
            font-size: .9rem;
            line-height: 1.52;
        }

        .dm-dist-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 22px;
            padding: 20px;
            min-height: 205px;
            box-shadow: 0 8px 24px rgba(15,23,42,.04);
        }

        .dm-dist-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #475569;
            font-size: .84rem;
            font-weight: 700;
            margin: 10px 0 5px 0;
        }

        .dm-bar-track {
            height: 8px;
            background: #eef2f7;
            border-radius: 999px;
            overflow: hidden;
        }

        .dm-bar-fill {
            height: 100%;
            border-radius: 999px;
            background: linear-gradient(90deg, #4f46e5, #06b6d4);
        }

        .dm-section-gap {
            height: .65rem;
        }

        @media (max-width: 900px) {
            .dm-topbar { align-items: flex-start; }
            .dm-page-title { font-size: 1.65rem; }
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
    if score >= 85:
        return "Excelente oportunidade", "dm-excellent"
    if score >= 70:
        return "Boa oportunidade", "dm-good"
    if score >= 55:
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


def portfolio_summary(products: list[dict]) -> dict:
    total_products = len(products)
    total_observations = sum(int(item.get("observations") or 0) for item in products)
    opportunities = [
        item for item in products
        if item.get("opportunity") in {"excellent", "good"}
    ]
    excellent = [item for item in products if item.get("opportunity") == "excellent"]
    scores = [float(item.get("deal_score") or 0) for item in products]
    return {
        "total_products": total_products,
        "total_observations": total_observations,
        "opportunities": len(opportunities),
        "excellent": len(excellent),
        "average_score": (sum(scores) / len(scores)) if scores else 0.0,
    }


def top_opportunities(products: list[dict], limit: int = 6) -> list[dict]:
    ranked = sorted(
        products,
        key=lambda item: (
            -float(item.get("deal_score") or 0),
            float(item.get("current_price") or item.get("best_price") or float("inf")),
        ),
    )
    return ranked[:limit]


if "last_search" not in st.session_state:
    st.session_state.last_search = None

if "selected_product" not in st.session_state:
    st.session_state.selected_product = None


health = api_get("/health", silent=True)
api_online = bool(health)

logo_html = ""
if os.path.exists(LOGO_PATH):
    try:
        with open(LOGO_PATH, "rb") as logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
        logo_html = (
            f'<img src="data:image/png;base64,{logo_b64}" '
            'style="height:54px;width:auto;object-fit:contain;" />'
        )
    except OSError:
        logo_html = ""

status_markup = (
    '<span class="dm-status-pill">'
    '<span class="dm-status-dot"></span>Sistema online</span>'
    if api_online
    else
    '<span class="dm-status-pill" '
    'style="background:#fff7ed;border-color:#fed7aa;color:#c2410c;">'
    '● Sistema indisponível</span>'
)

st.markdown(
    f"""
    <div class="dm-topbar">
        <div class="dm-brand-wrap">
            {logo_html}
            <div>
                <div class="dm-brand-title">DealMind AI</div>
                <div class="dm-brand-sub">
                    Smart Shopping Intelligence · Price Intelligence Copilot
                </div>
            </div>
        </div>
        <div>{status_markup}</div>
    </div>
    """,
    unsafe_allow_html=True,
)


tab_overview, tab_discover, tab_watch, tab_alerts, tab_advisor, tab_status = st.tabs(
    [
        "🏠 Visão Geral",
        "🔎 Descobrir",
        "📈 Minha Carteira",
        "🔔 Alertas",
        "🧠 AI Advisor",
        "⚙️ Status",
    ]
)


with tab_overview:
    st.markdown(
        """
        <div class="dm-page-title">Sua inteligência de compra, em um só lugar.</div>
        <div class="dm-page-sub">
            Priorize oportunidades, entenda os sinais da sua carteira e decida com mais contexto.
        </div>
        """,
        unsafe_allow_html=True,
    )

    overview_portfolio = api_get("/monitoring/products", silent=True)
    overview_products = (
        overview_portfolio.get("products", [])
        if isinstance(overview_portfolio, dict)
        else []
    )

    if overview_products:
        summary = portfolio_summary(overview_products)

        excellent_count = sum(
            1 for item in overview_products
            if float(item.get("deal_score") or 0) >= 85
        )
        good_count = sum(
            1 for item in overview_products
            if 70 <= float(item.get("deal_score") or 0) < 85
        )
        fair_count = sum(
            1 for item in overview_products
            if 55 <= float(item.get("deal_score") or 0) < 70
        )
        weak_count = sum(
            1 for item in overview_products
            if float(item.get("deal_score") or 0) < 55
        )

        k1, k2, k3, k4 = st.columns(4)

        with k1:
            st.markdown(
                f"""
                <div class="dm-kpi-card">
                    <div class="dm-kpi-icon">📦</div>
                    <div class="dm-kpi-label">PRODUTOS MONITORADOS</div>
                    <div class="dm-kpi-value">{summary["total_products"]}</div>
                    <div class="dm-kpi-note">Carteira ativa no DealMind</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k2:
            st.markdown(
                f"""
                <div class="dm-kpi-card">
                    <div class="dm-kpi-icon">📈</div>
                    <div class="dm-kpi-label">OBSERVAÇÕES DE PREÇO</div>
                    <div class="dm-kpi-value">{summary["total_observations"]}</div>
                    <div class="dm-kpi-note">Base histórica acumulada</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k3:
            st.markdown(
                f"""
                <div class="dm-kpi-card">
                    <div class="dm-kpi-icon">🎯</div>
                    <div class="dm-kpi-label">SINAIS FAVORÁVEIS</div>
                    <div class="dm-kpi-value">{summary["opportunities"]}</div>
                    <div class="dm-kpi-note">{excellent_count} excelente(s) · {good_count} boa(s)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with k4:
            st.markdown(
                f"""
                <div class="dm-kpi-card">
                    <div class="dm-kpi-icon">🧠</div>
                    <div class="dm-kpi-label">DEAL SCORE MÉDIO</div>
                    <div class="dm-kpi-value">{summary["average_score"]:.1f}<span style="font-size:.9rem;color:#94a3b8;">/100</span></div>
                    <div class="dm-kpi-note">Qualidade média da carteira</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="dm-section-gap"></div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="dm-panel-title">Melhores oportunidades agora</div>
            <div class="dm-panel-sub">
                Produtos priorizados automaticamente pelo Deal Score e pelo comportamento recente de preço.
            </div>
            """,
            unsafe_allow_html=True,
        )

        leaders = top_opportunities(overview_products, limit=6)

        for row_start in range(0, len(leaders), 3):
            cols = st.columns(3)

            for offset, col in enumerate(cols):
                idx = row_start + offset
                if idx >= len(leaders):
                    continue

                item = leaders[idx]
                score = float(item.get("deal_score") or 0)
                label, css_class = score_meta(score)

                price = item.get("current_price")
                if price is None:
                    price = item.get("best_price")

                current = float(price or 0)
                average = float(item.get("average_price") or 0)
                pct_vs_average = (
                    ((current - average) / average) * 100
                    if average > 0
                    else 0.0
                )

                observations = int(item.get("observations") or 0)
                observation_word = (
                    "observação"
                    if observations == 1
                    else "observações"
                )

                movement_text = (
                    f"{abs(pct_vs_average):.1f}% abaixo da média"
                    if pct_vs_average < -0.5
                    else
                    f"{pct_vs_average:.1f}% acima da média"
                    if pct_vs_average > 0.5
                    else
                    "Preço alinhado à média"
                )

                with col:
                    st.markdown(
                        f"""
                        <div class="dm-deal-card">
                            <div class="dm-deal-rank">TOP {idx + 1} · DEALMIND RANKING</div>
                            <div class="dm-deal-name">{item.get("title", "Produto monitorado")}</div>
                            <div class="dm-deal-price">{brl(current)}</div>
                            <div class="dm-deal-meta">
                                <span class="dm-mini-score {css_class}">{score:.1f}/100 · {label}</span>
                            </div>
                            <div style="margin-top:12px;color:#475569;font-size:.82rem;font-weight:700;">
                                {movement_text}
                            </div>
                            <div class="dm-observation" style="margin-top:7px;">
                                {observations} {observation_word} de preço
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if st.button(
                        "Ver análise completa",
                        key=f'overview_{item.get("external_id")}_{idx}',
                        use_container_width=True,
                    ):
                        st.session_state.watch_product_id = str(
                            item.get("external_id")
                        )
                        st.info(
                            "Produto selecionado. Abra Minha Carteira para ver "
                            "histórico, Deal Score e análise detalhada."
                        )

        st.markdown('<div class="dm-section-gap"></div>', unsafe_allow_html=True)

        intelligence_col, distribution_col = st.columns([1.08, 1])

        with intelligence_col:
            if excellent_count > 0:
                insight_main = (
                    f"{excellent_count} oportunidade"
                    f"{'s' if excellent_count != 1 else ''} "
                    "merecem atenção imediata."
                )
                insight_text = (
                    "O DealMind encontrou produtos na faixa de maior atratividade. "
                    "Priorize a revisão dos Top Deals antes de ampliar novas buscas."
                )
            elif summary["opportunities"] > 0:
                insight_main = (
                    f"{summary['opportunities']} produtos estão "
                    "em faixa favorável."
                )
                insight_text = (
                    "Há sinais positivos na carteira, mas vale abrir a análise "
                    "individual e comparar histórico, média e preço atual."
                )
            else:
                insight_main = "A carteira pede paciência neste momento."
                insight_text = (
                    "Nenhum produto apresenta sinal forte agora. Continue "
                    "monitorando para capturar quedas e novas oportunidades."
                )

            st.markdown(
                f"""
                <div class="dm-insight-card">
                    <div class="dm-insight-label">DEALMIND INSIGHTS</div>
                    <div class="dm-insight-main">{insight_main}</div>
                    <div class="dm-insight-text">{insight_text}</div>
                    <div style="margin-top:18px;color:#94a3b8;font-size:.78rem;">
                        Score médio da carteira: {summary["average_score"]:.1f}/100
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with distribution_col:
            total = max(len(overview_products), 1)

            excellent_pct = round((excellent_count / total) * 100)
            good_pct = round((good_count / total) * 100)
            fair_pct = round((fair_count / total) * 100)
            weak_pct = max(
                0,
                100 - excellent_pct - good_pct - fair_pct,
            )

            st.markdown(
                f"""
                <div class="dm-dist-card">
                    <div class="dm-panel-title" style="font-size:1.05rem;">Distribuição da carteira</div>
                    <div class="dm-panel-sub">Como os produtos estão classificados agora.</div>

                    <div class="dm-dist-row"><span>Excelente</span><span>{excellent_count}</span></div>
                    <div class="dm-bar-track"><div class="dm-bar-fill" style="width:{excellent_pct}%"></div></div>

                    <div class="dm-dist-row"><span>Boa</span><span>{good_count}</span></div>
                    <div class="dm-bar-track"><div class="dm-bar-fill" style="width:{good_pct}%"></div></div>

                    <div class="dm-dist-row"><span>Regular</span><span>{fair_count}</span></div>
                    <div class="dm-bar-track"><div class="dm-bar-fill" style="width:{fair_pct}%"></div></div>

                    <div class="dm-dist-row"><span>Fraca / aguardar</span><span>{weak_count}</span></div>
                    <div class="dm-bar-track"><div class="dm-bar-fill" style="width:{weak_pct}%"></div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info(
            "Sua visão geral será construída conforme você adicionar produtos "
            "à carteira. Use Descobrir para começar."
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
            <div class="dm-section-title">Produtos monitorados</div>
            <div class="dm-muted">
                Acompanhe sua carteira, filtre os produtos mais relevantes e abra a análise completa sem precisar digitar Product ID.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    portfolio = api_get("/monitoring/products", silent=True)
    monitored_products = (
        portfolio.get("products", [])
        if isinstance(portfolio, dict)
        else []
    )

    if monitored_products:
        total_products = len(monitored_products)
        total_observations = sum(
            int(item.get("observations") or 0)
            for item in monitored_products
        )
        opportunities_now = sum(
            1
            for item in monitored_products
            if item.get("opportunity") in {"excellent", "good"}
        )

        k1, k2, k3 = st.columns(3)
        k1.metric("Produtos monitorados", total_products)
        k2.metric("Observações acumuladas", total_observations)
        k3.metric("Oportunidades agora", opportunities_now)

        filters = st.columns([2.2, 1.3, 1.1])

        with filters[0]:
            portfolio_search = st.text_input(
                "Buscar produto",
                placeholder="Ex.: Nike, Mizuno, Olympikus...",
                key="portfolio_search",
            )

        with filters[1]:
            portfolio_sort = st.selectbox(
                "Ordenar por",
                [
                    "Mais recentes",
                    "Mais observações",
                    "Menor preço",
                    "Maior preço",
                    "Nome A–Z",
                ],
                key="portfolio_sort",
            )

        with filters[2]:
            min_observations = st.selectbox(
                "Mín. observações",
                [1, 2, 3, 5, 10],
                key="portfolio_min_observations",
            )

        search_term = portfolio_search.strip().lower()
        filtered_products = [
            item
            for item in monitored_products
            if int(item.get("observations") or 0) >= min_observations
            and (
                not search_term
                or search_term in str(item.get("title") or "").lower()
            )
        ]

        if portfolio_sort == "Mais observações":
            filtered_products.sort(
                key=lambda item: -int(item.get("observations") or 0)
            )
        elif portfolio_sort == "Menor preço":
            filtered_products.sort(
                key=lambda item: float(
                    item["best_price"]
                    if item.get("best_price") is not None
                    else float("inf")
                )
            )
        elif portfolio_sort == "Maior preço":
            filtered_products.sort(
                key=lambda item: -float(item.get("best_price") or 0)
            )
        elif portfolio_sort == "Nome A–Z":
            filtered_products.sort(
                key=lambda item: str(item.get("title") or "").lower()
            )
        else:
            filtered_products.sort(
                key=lambda item: str(item.get("last_captured_at") or ""),
                reverse=True,
            )

        page_size = 9
        total_filtered = len(filtered_products)
        total_pages = max(1, (total_filtered + page_size - 1) // page_size)

        if "portfolio_page" not in st.session_state:
            st.session_state.portfolio_page = 1

        if st.session_state.portfolio_page > total_pages:
            st.session_state.portfolio_page = total_pages

        page = st.session_state.portfolio_page
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_filtered)
        page_products = filtered_products[start_idx:end_idx]

        st.markdown("### Sua carteira")

        if total_filtered:
            st.caption(
                f"Exibindo {start_idx + 1}–{end_idx} de "
                f"{total_filtered} produtos filtrados."
            )

            for card_start in range(0, len(page_products), 3):
                cols = st.columns(3)

                for offset, col in enumerate(cols):
                    idx = card_start + offset
                    if idx >= len(page_products):
                        continue

                    item = page_products[idx]
                    external_id = str(item.get("external_id"))

                    with col:
                        with st.container(border=True):
                            st.markdown(
                                f'<div class="dm-product-title">'
                                f'{item.get("title", "Produto monitorado")}'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                            st.caption(f"ID · {external_id}")

                            c1, c2 = st.columns(2)
                            c1.metric(
                                "Preço atual",
                                brl(
                                    item.get("current_price")
                                    if item.get("current_price") is not None
                                    else item.get("best_price")
                                ),
                            )
                            c2.metric(
                                "Preço médio",
                                brl(item.get("average_price")),
                            )

                            deal_score = float(item.get("deal_score") or 0)
                            opportunity = item.get("opportunity") or "weak"

                            opportunity_labels = {
                                "excellent": "Excelente oportunidade",
                                "good": "Boa oportunidade",
                                "fair": "Oportunidade moderada",
                                "weak": "Aguardar",
                            }

                            opportunity_icons = {
                                "excellent": "🟢",
                                "good": "🔵",
                                "fair": "🟡",
                                "weak": "⚪",
                            }

                            st.markdown(
                                f"**Deal Score {deal_score:.1f}/100**  \n"
                                f"{opportunity_icons.get(opportunity, '⚪')} "
                                f"{opportunity_labels.get(opportunity, 'Aguardar')}"
                            )

                            observations = int(item.get("observations") or 0)
                            observation_label = (
                                "observação"
                                if observations == 1
                                else "observações"
                            )

                            st.caption(f"{observations} {observation_label}")

                            if st.button(
                                "Ver análise",
                                key=(
                                    f"portfolio_select_"
                                    f"{external_id}_"
                                    f"{start_idx + idx}"
                                ),
                                use_container_width=True,
                            ):
                                st.session_state.watch_product_id = external_id
                                st.rerun()

            nav1, nav2, nav3 = st.columns([1, 1.2, 1])

            with nav1:
                if st.button(
                    "← Anterior",
                    disabled=page <= 1,
                    use_container_width=True,
                ):
                    st.session_state.portfolio_page -= 1
                    st.rerun()

            with nav2:
                st.markdown(
                    f"<div style='text-align:center;padding-top:.55rem;"
                    f"color:#64748b;font-weight:700;'>"
                    f"Página {page} de {total_pages}</div>",
                    unsafe_allow_html=True,
                )

            with nav3:
                if st.button(
                    "Próxima →",
                    disabled=page >= total_pages,
                    use_container_width=True,
                ):
                    st.session_state.portfolio_page += 1
                    st.rerun()

            label_map = {
                str(item.get("external_id")): item.get(
                    "title",
                    str(item.get("external_id")),
                )
                for item in filtered_products
            }
            product_ids = list(label_map.keys())

            preferred_id = str(
                st.session_state.get("watch_product_id", product_ids[0])
            )
            if preferred_id not in product_ids:
                preferred_id = product_ids[0]

            selected_product_id = st.selectbox(
                "Escolha um produto",
                options=product_ids,
                index=product_ids.index(preferred_id),
                format_func=lambda product_id: label_map.get(
                    product_id,
                    product_id,
                ),
                key="monitored_product_selector_v5",
            )

            st.session_state.watch_product_id = selected_product_id

            analysis = api_get(
                f"/monitoring/{selected_product_id}",
                silent=True,
            )
            history_data = api_get(
                f"/monitoring/{selected_product_id}/history",
                silent=True,
            )

            if isinstance(analysis, dict) and analysis.get("product_id"):
                st.divider()
                st.markdown(
                    f"### {label_map.get(selected_product_id, 'Análise do produto')}"
                )

                m1, m2, m3, m4 = st.columns(4)
                m1.metric(
                    "Preço atual",
                    brl(analysis.get("current_price")),
                )
                m2.metric(
                    "Preço médio",
                    brl(analysis.get("average_price")),
                )
                m3.metric(
                    "Melhor preço",
                    brl(analysis.get("minimum_price")),
                )
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
                        opportunity_label(
                            analysis.get("opportunity")
                        ),
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
                        f"**Observações:** "
                        f"{analysis.get('observations', 0)}"
                    )
                    st.write(
                        f"**Preço máximo:** "
                        f"{brl(analysis.get('maximum_price'))}"
                    )

                    if analysis.get("url"):
                        st.link_button(
                            "Abrir produto",
                            analysis["url"],
                            use_container_width=True,
                        )
            else:
                st.info(
                    "Ainda não há análise consolidada para o produto selecionado."
                )

        else:
            st.info(
                "Nenhum produto corresponde aos filtros selecionados."
            )

    else:
        st.info(
            "Sua carteira ainda está vazia. Vá em Descobrir, "
            "encontre uma oferta e clique em “Monitorar preço”."
        )

    with st.expander("Registrar observação manual"):
        manual_default_id = (
            str(st.session_state.get("watch_product_id"))
            if st.session_state.get("watch_product_id")
            else "TENIS-001"
        )

        with st.form("manual_snapshot_form"):
            c1, c2 = st.columns(2)

            with c1:
                manual_product_id = st.text_input(
                    "Identificador do produto",
                    value=manual_default_id,
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

    selected_id = (
        str(st.session_state.selected_product.get("id"))
        if st.session_state.selected_product
        else "TENIS-001"
    )

    with st.form("alert_form"):
        a1, a2, a3 = st.columns([1.5, 1, 1.4])

        with a1:
            alert_product = st.text_input(
                "Identificador do produto",
                value=selected_id,
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

    advisor_default = (
        str(st.session_state.selected_product.get("id"))
        if st.session_state.selected_product
        else "TENIS-001"
    )

    advisor_product_id = st.text_input(
        "Escolha um produto para o Advisor",
        value=advisor_default,
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