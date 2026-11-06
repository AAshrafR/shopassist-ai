# ShopAssist AI: Architecture & System Design

## 1. System Overview
**ShopAssist AI** is an enterprise-grade customer support chatbot combining **Retrieval-Augmented Generation (RAG)** with deterministic **Business Operations Tools** (order tracking and ticket creation) for e-commerce platforms.

```
                  +----------------------------------------+
                  |         Client Interface               |
                  |  (HTML5/CSS3/Vanilla JS / Vercel Host) |
                  +-------------------+--------------------+
                                      | HTTP POST /api/chat
                                      v
                  +----------------------------------------+
                  |           FastAPI Gateway              |
                  | (CORS, Request Logging Middleware)     |
                  +-------------------+--------------------+
                                      |
                                      v
                        +---------------------------+
                        |  Intent & Query Router    |
                        +-------------+-------------+
                                      |
             +------------------------+-------------------------+
             |                                                  |
             v (Transactional Queries)                          v (Informational Queries)
+-------------------------+                           +-------------------------+
|     Business Tools      |                           |     RAG Pipeline        |
|-------------------------|                           |-------------------------|
| • order_lookup(id)      |                           | • Query Embedding       |
| • create_ticket(...)    |                           | • Hybrid Vector Search  |
+------------+------------+                           |   (Cosine + Lexical)    |
             |                                        +------------+------------+
             v                                                     |
+-------------------------+                                        v
| Simulated Business Data |                           +-------------------------+
|  (orders.json / SQLite) |                           | Context Grounding Engine|
+-------------------------+                           | (Policy + FAQ Citations)|
                                                      +-------------------------+
                                                                   |
                                                                   v
                                                      +-------------------------+
                                                      |   MLflow Experiment     |
                                                      |  Tracking & Telemetry   |
                                                      +-------------------------+
```

## 2. Core Modules

### 2.1 Data Collection & Knowledge Base
- **Bitext Dataset**: 26,872 customer support instruction-response pairs categorized into 11 retail domains and 27 intents.
- **Store Policies**: Markdown policies governing returns, refunds, shipping schedules, payment methods, cancellations, and account privacy.
- **Knowledge Base Chunker**: Semantic text chunker splitting documents into structured overlapping chunks with source file, title, and category metadata.

### 2.2 Semantic Vector Index & Hybrid Retrieval
- **Dense Vector Embeddings**: Sublinear TF-IDF + TruncatedSVD (Latent Semantic Analysis) projecting queries and documents into normalized 128-dimensional dense semantic vectors.
- **Hybrid Retrieval**: Linear combination of dense cosine similarity and lexical token overlap:
  $$\text{Score} = \alpha \cdot \text{CosineSim}(q, d) + (1 - \alpha) \cdot \text{LexicalOverlap}(q, d)$$
- **Score Ranking & Metadata Filtering**: Top-k retrieval with document deduplication and thresholding.

### 2.3 Business Tools Integration
- **Order Status Lookup**: Real-time extraction of order IDs (`ORD-1001` through `ORD-1005`) and retrieval of order status, tracking numbers, shipping carriers, estimated delivery dates, and purchased items.
- **Support Ticket Creation**: Automated creation of structured support tickets with category classification, priority assignment, and unique ticket IDs (`TKT-1001`+).

### 2.4 Backend (FastAPI)
- Modular routers (`/api/chat`, `/api/orders`, `/api/tickets`, `/api/health`, `/api/policies`).
- Pydantic models for strict type checking and validation.
- CORS middleware enabling frontend hosting across disparate origins (e.g., Vercel).
- Request logging middleware capturing endpoint latency and status codes.

### 2.5 Frontend & Vercel Deployment
- Custom-developed e-commerce customer support interface built from scratch with responsive layout.
- Real-time response streaming and typing indicators.
- Verified source citations tags detailing source file, title, and relevance score.
- Quick test chips and live simulated order monitor.
- Vercel routing configuration (`vercel.json`).

### 2.6 Evaluation & MLOps
- Quantitative benchmark over 113 balanced domain test cases.
- Metrics: Precision@3 (94.44%), Recall@3 (97.22%), MRR (0.9583), Tool Execution Accuracy (100%), Mean Latency (10.15ms).
- MLflow experiment tracking logging runs, hyperparameters, metrics, and evaluation reports.

