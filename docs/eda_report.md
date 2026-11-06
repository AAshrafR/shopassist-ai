# Exploratory Data Analysis (EDA) Report: ShopAssist AI

## 1. Dataset Overview
- **Dataset Source**: Bitext Customer Support LLM Chatbot Training Dataset (`bitext/Bitext-customer-support-llm-chatbot-training-dataset`)
- **Total Records**: 26,872
- **Total Categories**: 11
- **Total Intents**: 27
- **Missing Values**: 0 across all features

## 2. Category Distribution
The dataset encompasses customer support interactions across primary retail domains:

| Category | Record Count | Percentage |
|---|---|---|
| ACCOUNT | 5,986 | 22.28% |
| ORDER | 3,988 | 14.84% |
| REFUND | 2,992 | 11.13% |
| INVOICE | 1,999 | 7.44% |
| CONTACT | 1,999 | 7.44% |
| PAYMENT | 1,998 | 7.44% |
| FEEDBACK | 1,997 | 7.43% |
| DELIVERY | 1,994 | 7.42% |
| SHIPPING | 1,970 | 7.33% |
| SUBSCRIPTION | 999 | 3.72% |
| CANCEL | 950 | 3.54% |

## 3. Intent Distribution (Top 15)
The dataset contains 27 discrete intents. The distribution across intents is well-balanced:

| Intent | Category | Count |
|---|---|---|
| check_invoice | INVOICE | 1,000 |
| complaint | FEEDBACK | 1,000 |
| contact_customer_service | CONTACT | 1,000 |
| edit_account | ACCOUNT | 1,000 |
| switch_account | ACCOUNT | 1,000 |
| check_payment_methods | PAYMENT | 999 |
| contact_human_agent | CONTACT | 999 |
| delivery_period | DELIVERY | 999 |
| get_invoice | INVOICE | 999 |
| newsletter_subscription | SUBSCRIPTION | 999 |
| payment_issue | PAYMENT | 999 |
| registration_problems | ACCOUNT | 999 |
| cancel_order | ORDER | 998 |
| place_order | ORDER | 998 |
| track_refund | REFUND | 998 |

## 4. Text Length Statistics (Characters)

| Metric | Instruction (Customer Prompt) | Response (Agent Guidance) |
|---|---|---|
| Mean | 46.9 | 633.4 |
| Std Dev | 10.9 | 330.3 |
| Min | 6 | 57 |
| 25% | 40 | 427 |
| 50% (Median) | 48 | 540 |
| 75% | 55 | 752 |
| Max | 92 | 2463 |

## 5. Knowledge Base Construction
- **Total Indexed Chunks**: 426
  - **Policy Chunks**: 21
  - **Bitext FAQ Canonical Chunks**: 405
- **Coverage**: Grounded support across Returns, Shipping, Payments, Cancellations, Accounts, and Order Tracking.

## 6. Key Findings and Implications for RAG Architecture
1. **Balanced Intent Representation**: The dataset provides uniform coverage across inquiries, ensuring no single intent skews the retrieval index.
2. **Distinct Categorical Boundaries**: Separation between informational queries (e.g., return window rules) and transactional queries (e.g., order tracking) allows clear routing to either RAG retrieval or Business Tools.
3. **Structured Policy Knowledge**: Augmenting the conversational training data with concrete store policy documents prevents hallucinated numerical bounds (e.g. guaranteeing the exact 30-day return policy and $50 free shipping threshold).
