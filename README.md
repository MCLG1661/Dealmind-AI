# <img width="250" height="250" alt="ChatGPT Image 28 de ago  de 2026, 11_51_38" src="https://github.com/user-attachments/assets/e1eaae9d-152b-481f-a4ee-0a9706e6032e" /> DealMind AI
DealMind AI

> Inteligência de preços para encontrar melhores oportunidades de compra.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-336791)
![Tests](https://img.shields.io/badge/tests-11%20passed-brightgreen)

**DealMind AI** é um MVP funcional de Price Intelligence desenvolvido para transformar dados de ofertas e histórico de preços em informações úteis para decisão de compra.

A aplicação combina busca de produtos, monitoramento de preços, histórico, Deal Score, alertas inteligentes e recomendações orientadas por dados em uma experiência integrada.

---

## 🚀 Visão do produto

Encontrar uma oferta não significa necessariamente encontrar um bom momento de compra.

O DealMind AI foi desenvolvido para responder perguntas como:

- O preço atual está realmente bom?
- Quanto esse produto costuma custar?
- O preço está abaixo ou acima da média?
- Vale comprar agora ou esperar?
- Quais produtos apresentam as melhores oportunidades?
- Quando o preço atingir meu objetivo, o sistema consegue identificar isso?

O objetivo é transformar dados de preço em **inteligência de compra**.

---

## ✨ Principais funcionalidades

### 🔎 Descoberta de produtos

Pesquisa de produtos através de providers integrados à aplicação.

A arquitetura suporta diferentes fontes de dados e mantém a lógica de busca desacoplada da camada de apresentação.

---

### 📊 Monitoramento de preços

O DealMind registra snapshots de ofertas contendo informações como:

- identificador do produto;
- título;
- preço atual;
- preço original;
- URL;
- categoria;
- data e hora da observação.

Essas observações formam uma série histórica utilizada pelas demais camadas de inteligência.

---

### 📈 Histórico e análise de preços

Para produtos monitorados, a aplicação consegue calcular e apresentar informações como:

- preço atual;
- menor preço observado;
- maior preço observado;
- preço médio;
- número de observações;
- variação em relação à média;
- comportamento recente do preço.

---

### 🎯 Deal Score

O **Deal Score** sintetiza diferentes sinais de preço em uma pontuação que ajuda a priorizar oportunidades.

A interface utiliza esse score para destacar produtos potencialmente mais interessantes dentro da carteira monitorada.

---

### 🔔 Smart Price Alerts

O usuário pode criar um alerta definindo:

- produto;
- preço-alvo;
- contato opcional.

Quando um alerta é criado, o DealMind verifica se já existe um preço conhecido para aquele produto.

Se:

```text
preço atual <= preço-alvo
```

o alerta pode ser imediatamente considerado atingido.

Caso contrário, permanece ativo aguardando uma nova condição favorável de preço.

Isso evita manter como ativo um alerta cujo objetivo já foi alcançado no momento da criação.

---

### 🧠 DealMind AI Advisor

O Advisor transforma histórico de preços e indicadores do produto em uma recomendação mais objetiva para decisão de compra.

A proposta é responder à pergunta:

> **Comprar agora ou esperar?**

A recomendação utiliza os sinais disponíveis no DealMind para contextualizar o preço atual e apoiar a decisão.

---

### 📊 Cockpit de inteligência

A visão geral apresenta indicadores consolidados da carteira, incluindo:

- produtos monitorados;
- observações de preço;
- sinais favoráveis;
- Deal Score médio;
- ranking das melhores oportunidades.

O objetivo é permitir que o usuário identifique rapidamente quais produtos merecem atenção.

---

## 🏗️ Arquitetura

```text
┌─────────────────────────────┐
│        Streamlit UI         │
│   Product Experience Layer  │
└──────────────┬──────────────┘
               │ HTTP
               ▼
┌─────────────────────────────┐
│         FastAPI API         │
│      Application Layer      │
└──────────────┬──────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌───────────────┐
│   Services   │  │  Repositories │
│              │  │               │
│ Monitoring   │  │ Alerts        │
│ Advisor      │  │ Offers        │
│ Providers    │  │ History       │
└──────┬───────┘  └───────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐  ┌───────────────┐
│  Providers   │  │   Database    │
│ Mercado Livre│  │ SQLite /      │
│ Demo / etc.  │  │ PostgreSQL    │
└──────────────┘  └───────────────┘
```

A aplicação foi organizada em camadas para separar responsabilidades entre:

- API;
- regras de negócio;
- persistência;
- integrações externas;
- providers;
- frontend.

---

## 🧱 Estrutura do projeto

```text
dealmind-ai/
│
├── app/
│   ├── api/
│   │   ├── main.py
│   │   ├── monitoring_routes.py
│   │   └── advisor_routes.py
│   │
│   ├── database/
│   │   └── db.py
│   │
│   ├── integrations/
│   │   └── mercado_livre.py
│   │
│   ├── models/
│   │
│   ├── providers/
│   │
│   ├── repositories/
│   │   ├── alert_repository.py
│   │   └── offer_repository.py
│   │
│   ├── services/
│   │   ├── monitoring_service.py
│   │   ├── provider_service.py
│   │   └── token_store.py
│   │
│   └── config.py
│
├── frontend/
│   └── streamlit_app.py
│
├── tests/
│
├── data/
│
├── .github/
│   └── workflows/
│
├── requirements.txt
├── pytest.ini
├── run_api.py
└── README.md
```

---

## 🔌 API

A aplicação utiliza **FastAPI** como backend.

### Health Check

```http
GET /health
```

Exemplo:

```json
{
  "status": "ok",
  "service": "dealmind-ai",
  "version": "0.3.0"
}
```

---

### Providers

```http
GET /providers
```

Lista os providers disponíveis para pesquisa de produtos.

---

### Busca de produtos

```http
GET /products/search
```

Principais parâmetros:

```text
q
max_price
source
limit
```

---

### Histórico de produto

```http
GET /products/{product_id}/history
```

Retorna o histórico conhecido de preços do produto.

---

### Alertas

Criar alerta:

```http
POST /alerts
```

Listar alertas:

```http
GET /alerts
```

---

### Monitoramento

```http
POST /monitoring/snapshots
GET /monitoring/products
GET /monitoring/{product_id}
GET /monitoring/{product_id}/history
```

---

### Advisor

```http
GET /advisor/{product_id}
```

Retorna a análise utilizada pelo DealMind AI Advisor.

---

### Autenticação Mercado Livre

```http
GET /auth/status
GET /auth/me
GET /auth/mercadolivre
GET /callback/mercadolivre
```

A integração utiliza OAuth para autenticação com o Mercado Livre.

---

## 🛠️ Stack tecnológica

### Backend

- Python
- FastAPI
- Pydantic
- Requests

### Frontend

- Streamlit
- Pandas

### Dados

- SQLite para desenvolvimento local
- PostgreSQL para ambiente de produção
- camada de repositories para persistência

### Integrações

- Mercado Livre
- arquitetura baseada em providers

### Qualidade e DevOps

- Pytest
- Git
- GitHub
- GitHub Actions
- Render
- Streamlit

---

## 💻 Executando localmente

### 1. Clonar o projeto

```bash
git clone https://github.com/MCLG1661/dealmind-ai.git
cd dealmind-ai
```

### 2. Criar ambiente virtual

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example`.

Nunca envie credenciais reais para o repositório.

---

## ⚙️ Executando o backend

```bash
python -m uvicorn run_api:app --reload
```

Backend local:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
http://127.0.0.1:8000/health
```

---

## 🖥️ Executando o frontend

Em outro terminal:

```bash
streamlit run frontend/streamlit_app.py
```

Interface local:

```text
http://localhost:8501
```

Para desenvolvimento local, o backend e o frontend devem permanecer executando simultaneamente em terminais separados.

---

## 🧪 Testes

Execute:

```bash
pytest -q
```

Estado validado do projeto:

```text
11 passed
```

A suíte cobre componentes críticos da aplicação e ajuda a evitar regressões durante a evolução do produto.

---

## 🌐 Deploy

O backend está preparado para execução em ambiente de produção através do Render.

A arquitetura permite separar:

```text
Frontend
   ↓
FastAPI
   ↓
Services
   ↓
Repositories
   ↓
PostgreSQL
```

O health check da API permite verificar rapidamente a disponibilidade do serviço.

---

## 🔐 Segurança

Credenciais e tokens não devem ser versionados.

Arquivos locais de ambiente devem permanecer ignorados pelo Git.

Exemplo:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

Tokens OAuth, secrets e strings de conexão devem ser configurados através de variáveis de ambiente.

---

## 🧠 Decisões de engenharia

O DealMind AI foi desenvolvido priorizando alguns princípios:

**Separação de responsabilidades**  
Frontend, API, services, repositories, providers e integrações possuem responsabilidades distintas.

**Provider abstraction**  
A aplicação não depende diretamente de uma única fonte de produtos.

**Persistência de histórico**  
As observações são armazenadas para permitir análise temporal em vez de depender apenas do preço instantâneo.

**Inteligência sobre dados históricos**  
O produto procura responder não apenas “quanto custa?”, mas principalmente “esse preço faz sentido agora?”.

**Alertas orientados ao estado atual**  
Um alerta pode ser avaliado já no momento de sua criação quando existe preço conhecido.

**Experiência orientada à decisão**  
Cockpit, Deal Score, alertas e Advisor procuram reduzir a quantidade de dados que o usuário precisa interpretar manualmente.

---

## 🗺️ Roadmap

O MVP atual estabelece a base para futuras evoluções como:

- notificações automáticas por canais externos;
- execução periódica de monitoramento;
- expansão de providers;
- maior profundidade do modelo de recomendação;
- autenticação de usuários;
- carteiras individualizadas;
- evolução do Deal Score;
- observabilidade e métricas de produção;
- testes adicionais de integração;
- evolução para uma arquitetura SaaS multiusuário.

---

## 🎯 Objetivo do projeto

O DealMind AI demonstra, em um único produto, competências relacionadas a:

- desenvolvimento backend com Python;
- APIs REST;
- integração com APIs externas;
- Data Analytics;
- persistência e modelagem de dados;
- regras de negócio;
- arquitetura em camadas;
- desenvolvimento de produto;
- UX orientada à decisão;
- Inteligência Artificial aplicada a negócios;
- deploy e operação de aplicações.

Mais do que um comparador de preços, o DealMind foi concebido como um **copiloto de inteligência de compra**.

---

## 👤 Autor

**Marcus Guedes**

Marketing • Gestão • Data Analytics • Inteligência Artificial aplicada a negócios

- GitHub: [MCLG1661](https://github.com/MCLG1661)
- LinkedIn: [Marcus Guedes](https://www.linkedin.com/in/marcusguedes/)

---

