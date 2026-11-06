# ShopAssist AI 🛍️

[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.162.0-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tests Passing](https://img.shields.io/badge/pytest-14%2F14%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![Precision@3](https://img.shields.io/badge/Precision%403-94.44%25-success.svg)](docs/evaluation_results.md)
[![MRR](https://img.shields.io/badge/MRR-0.9583-success.svg)](docs/evaluation_results.md)
[![Tool Accuracy](https://img.shields.io/badge/Tool%20Accuracy-100%25-brightgreen.svg)](docs/evaluation_results.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/AAshrafR/shopassist-ai/releases)

An enterprise-ready intelligent customer support concierge powered by **Hybrid Retrieval-Augmented Generation (RAG)** and deterministic **Business Operations Tools** for modern e-commerce platforms.

ShopAssist AI unifies semantic policy retrieval, grounded extractive answering, real-time order tracking, and automated support ticket generation into a high-performance, sub-15ms FastAPI service and responsive web UI.

---

## 🌟 Key Features

- **Hybrid Semantic & Lexical Retrieval (RAG)**: Blends 128-dimensional Latent Semantic Analysis (Dense LSA TF-IDF + TruncatedSVD) with lexical keyword matching ($\alpha = 0.75$) to achieve high-precision knowledge retrieval across 950+ knowledge chunks.
- **Zero-Hallucination Policy Grounding**: Answers policy queries (returns, cancellations, payment options, shipping times, privacy) strictly from official store policies with direct citations.
- **Deterministic Business Tools**:
  - 📦 **Order Status Lookup**: Automatically parses order IDs (`ORD-1001` through `ORD-1005`) and fetches live fulfillment status, tracking numbers, carriers, and item breakdowns.
  - 🎫 **Support Ticket Creation**: Automatically routes complex inquiries or defective item reports into structured support tickets (`TKT-1001`+) with automatic category and priority triage.
- **Ultra-Fast Latency**: Under **15 ms** average end-to-end response time locally without external cloud API dependencies.
- **MLOps & Telemetry Tracking**: Integrated **MLflow** tracking for retrieval hyperparameters and benchmark runs, coupled with structured request duration logging middleware.
- **Responsive Web Interface**: Modern, interactive chat UI with quick query chips, live simulated order panel, verified citation pills, and typing indicators. Ready for local hosting or Vercel edge deployment.
- **Comprehensive Test Suite**: 14 unit and integration tests covering REST APIs, RAG search, chunking, and tool dispatches.

---

## 🏗️ System Architecture

```
                      +----------------------------------------+
                      |         Web Client / Browser           |
                      |    (HTML5 / CSS3 / Vanilla JS / UI)    |
                      +-------------------+--------------------+
                                          | HTTP REST
                                          v
                      +----------------------------------------+
                      |           FastAPI Gateway              |
                      |  (CORS, Static Files, Middleware Log)  |
                      +-------------------+--------------------+
                                          |
                                          v
                            +---------------------------+
                            |   Intent & Query Router   |
                            +-------------+-------------+
                                          |
                 +------------------------+-------------------------+
                 | (Transactional Intent)                           | (Informational Intent)
                 v                                                  v
    +-------------------------+                        +-------------------------+
    |     Business Tools      |                        |     RAG Pipeline        |
    |-------------------------|                        |-------------------------|
    | • lookup_order_status() |                        | • Dense LSA Embeddings  |
    | • create_support_ticket |                        | • Hybrid Vector Search  |
    | • list_recent_tickets() |                        | • Policy Grounding      |
    +------------+------------+                        +------------+------------+
                 |                                                  |
                 v                                                  v
    +-------------------------+                        +-------------------------+
    | Simulated Business Data |                        | Grounded Answer with    |
    | (orders.json, tickets)  |                        | Document Citations      |
    +-------------------------+                        +-------------------------+
                                                                    |
                                                                    v
                                                       +-------------------------+
                                                       |    MLflow Experiment    |
                                                       |     Tracking Store      |
                                                       +-------------------------+
```

---

## 📊 Evaluation & Benchmark Results

Evaluated over **113 balanced benchmark test cases** across 11 retail domains and 27 intents:

| Evaluation Metric | Measured Value | Target Benchmark | Status |
|:---|:---:|:---:|:---:|
| **Precision@3** | **94.44%** | > 80% |  Passed |
| **Recall@3** | **97.22%** | > 85% |  Passed |
| **Mean Reciprocal Rank (MRR)** | **0.9583** | > 0.75 |  Passed |
| **Tool Execution Accuracy** | **100.00%** | > 95% |  Passed |
| **Mean Query Latency** | **13.44 ms** | < 200 ms |  Passed |
| **P50 Latency (Median)** | **13.24 ms** | < 100 ms |  Passed |
| **P90 Latency** | **14.04 ms** | < 150 ms |  Passed |
| **P99 Latency** | **29.18 ms** | < 250 ms |  Passed |

*Detailed evaluation methodology and discussion are available in [docs/evaluation_results.md](docs/evaluation_results.md).*

---

## 📁 Repository Structure

```
shopassist-ai/
├── backend/                  # FastAPI Application
│   ├── routers/
│   │   ├── chat.py           # /api/chat RAG & Tool endpoint
│   │   ├── health.py         # /api/health and /api/policies
│   │   ├── orders.py         # /api/orders CRUD endpoints
│   │   └── tickets.py        # /api/tickets endpoints
│   ├── schemas/
│   │   └── api_models.py     # Pydantic request/response models
│   └── main.py               # Application factory & static mounting
├── data/
│   ├── processed/            # Cleaned data, chunks, and vector index
│   │   ├── cleaned_customer_support.csv
│   │   ├── eval_dataset.json
│   │   ├── knowledge_base_chunks.json
│   │   └── vector_index.pkl
│   ├── raw/                  # Raw Bitext customer support dataset
│   │   └── bitext_customer_support.csv
│   └── simulated/            # Business operational JSON databases
│       ├── orders.json
│       └── tickets.json
├── docs/
│   ├── policies/             # Markdown store policies
│   │   ├── account_security_policy.md
│   │   ├── cancellation_policy.md
│   │   ├── payment_and_billing_policy.md
│   │   ├── return_and_refund_policy.md
│   │   └── shipping_and_delivery_policy.md
│   ├── architecture.md       # Technical architecture specification
│   ├── eda_report.md         # Exploratory data analysis report
│   └── evaluation_results.md # Quantitative benchmark report
├── frontend/                 # Client UI (HTML5 / Vanilla JS / CSS)
│   ├── app.js                # Frontend controller & markdown renderer
│   ├── index.html            # Main customer concierge view
│   ├── style.css             # Responsive styling & themes
│   └── vercel.json           # Vercel deployment configuration
├── notebooks/
│   └── 01_eda_and_data_preprocessing.ipynb # Interactive EDA walkthrough
├── scripts/
│   ├── build_index.py        # Rebuild vector search index
│   ├── run_eda.py            # Regenerate EDA report
│   ├── run_evaluation.py     # Run 113-case benchmark & log to MLflow
│   ├── start_server.sh       # Linux/macOS launcher
│   └── start_server.bat      # Windows launcher
├── src/
│   ├── data/                 # Cleaning & data management
│   │   ├── preprocessor.py   # Dataset cleaner & chunk builder
│   │   └── simulated_data.py # Mock order & ticket store
│   ├── evaluation/           # Metrics calculation
│   │   └── metrics.py        # Precision, Recall, MRR, Tool accuracy
│   ├── monitoring/           # Logging & MLflow
│   │   ├── logger.py         # Structured request logging middleware
│   │   └── mlflow_tracker.py # MLflow tracking integration
│   ├── rag/                  # Core RAG engine
│   │   ├── chunker.py        # Recursive semantic text chunker
│   │   ├── embeddings.py     # Dense LSA embedding model
│   │   ├── pipeline.py       # End-to-end RAG orchestrator & router
│   │   └── vector_store.py   # Hybrid vector search index
│   └── tools/                # Business tools
│       ├── order_tool.py     # Order tracking & parsing
│       └── ticket_tool.py    # Ticket creation & dispatch
├── tests/                    # Pytest test suite
│   ├── test_api.py           # FastAPI integration tests
│   ├── test_rag.py           # RAG retrieval unit tests
│   └── test_tools.py         # Order & ticket tool unit tests
├── .gitignore
├── LICENSE
├── requirements.txt
├── run.py                    # Universal runner script
└── README.md
```

---

## 🚀 Quickstart

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone Repository & Setup Environment

```bash
git clone https://github.com/AAshrafR/shopassist-ai.git
cd shopassist-ai

# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS:
source .venv/bin/activate

# Or activate on Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

You can start the server with any of the following:

```bash
# Universal entry point:
python run.py

# Or directly with Uvicorn:
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Or via launch scripts:
./scripts/start_server.sh     # Linux / macOS
.\scripts\start_server.bat    # Windows
```

Once running:
- **Web Interface**: Open [http://localhost:8000](http://localhost:8000) in your browser.
- **Interactive Swagger Docs**: Open [http://localhost:8000/docs](http://localhost:8000/docs).
- **ReDoc Documentation**: Open [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 🧪 Running the Test Suite

Run all unit and integration tests with `pytest`:

```bash
pytest -v
```

Output:
```
tests/test_api.py::test_health_endpoint PASSED                     [  7%]
tests/test_api.py::test_list_policies_endpoint PASSED              [ 14%]
tests/test_api.py::test_orders_endpoints PASSED                    [ 21%]
tests/test_api.py::test_tickets_endpoints PASSED                   [ 28%]
tests/test_api.py::test_chat_endpoint_rag PASSED                   [ 35%]
tests/test_api.py::test_chat_endpoint_tool PASSED                  [ 42%]
tests/test_rag.py::test_chunker_splitting PASSED                   [ 50%]
tests/test_rag.py::test_vector_store_indexing_and_search PASSED    [ 57%]
tests/test_rag.py::test_rag_pipeline_end_to_end PASSED            [ 64%]
tests/test_tools.py::test_extract_order_id PASSED                  [ 71%]
tests/test_tools.py::test_order_lookup_success PASSED              [ 78%]
tests/test_tools.py::test_order_lookup_not_found PASSED            [ 85%]
tests/test_tools.py::test_create_support_ticket PASSED             [ 92%]
tests/test_tools.py::test_list_recent_tickets PASSED               [100%]

======================== 14 passed in 1.87s =========================
```

---

## 🔄 Data Pipeline & Benchmark Reproducibility

To re-run the full pipeline from raw data to evaluation:

```bash
# 1. Clean raw Bitext dataset & extract policy chunks
python -m src.data.preprocessor

# 2. Build and persist the vector search index
python scripts/build_index.py

# 3. Generate exploratory data analysis report
python scripts/run_eda.py

# 4. Run the 113-case evaluation benchmark and log to MLflow
python scripts/run_evaluation.py
```

### Inspect MLflow Experiments

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```
Navigate to [http://localhost:5000](http://localhost:5000) to inspect benchmark runs, hyperparameter combinations, latency curves, and logged artifacts.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Sample Payload / Params |
|:---|:---|:---|:---|
| `POST` | `/api/chat` | Main RAG & Tool assistant endpoint | `{"message": "Where is my order ORD-1001?"}` |
| `GET` | `/api/orders` | List simulated customer orders | None |
| `GET` | `/api/orders/{order_id}` | Retrieve specific order by ID | e.g. `/api/orders/ORD-1001` |
| `GET` | `/api/tickets` | List recent customer support tickets | None |
| `POST` | `/api/tickets` | Create a new support ticket | `{"customer_name": "...", "subject": "..."}` |
| `GET` | `/api/policies` | List all indexed store policy files | None |
| `GET` | `/api/health` | System health, uptime & index count | None |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
