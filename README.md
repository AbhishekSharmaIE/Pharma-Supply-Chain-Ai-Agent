# 🏥 Pharma Supply Chain AI Agent

LLM-powered order triage for pharmaceutical distribution.  
The system ingests CSV order batches, evaluates each order against deterministic business rules, uses Azure OpenAI for explainable prioritization, and escalates uncertain/conflicting decisions for human review.

## 🚀 Project Overview

Manual triage in pharma distribution can be slow and inconsistent when batch volume spikes. This project automates first-pass prioritization while preserving auditability through:
- deterministic pre-LLM rule checks,
- structured prompt/response contracts,
- confidence guardrails,
- and explicit human-review fallback paths.

## 🏗️ Architecture Diagram

```text
CSV Upload
   |
   v
FastAPI API
   |
   v
Rule Engine (5 hard rules)
   |
   v
Prompt Builder (structured context)
   |
   v
Azure OpenAI / Mock LLM
   |
   v
Decision Parser (strict JSON validation)
   |
   v
Confidence Evaluator (fallback + overrides)
   |
   v
BatchResponse (priority + confidence + review flags)
```

## 📌 5 Business Rules

1. **Urgency:** `urgency_flag == true`  
2. **Stock Risk:** `stock_available < quantity`  
3. **Customer Tier:** `customer_tier == "platinum"`  
4. **Expiry Risk:** `expiry_date` within 30 days  
5. **Proximity:** `customer_location == warehouse_location`

## 🛡️ Responsible AI

- Confidence thresholds gate automation and force human review for low-confidence output.
- Conflicting signals (urgent + out-of-stock) are escalated deterministically.
- Expiry-risk orders can be auto-overridden from `LOW` to `MEDIUM` to reduce unsafe deprioritization.
- Failure modes and mitigation details live in `backend/responsible_ai/failure_modes.md`.

### Confidence Threshold Policy

| Score | Action |
|---|---|
| `>= 0.85` | Auto-approve decision |
| `0.75 - 0.84` | Accept and log for audit |
| `< 0.75` | Mandatory human review |
| Parse error | Hard fallback to human handling |

## ⚙️ Getting Started

1. Clone the repository.
2. Copy env template:
   - `cp backend/.env.example backend/.env`
3. (Optional) Enable mock mode for local testing:
   - set `USE_MOCK_LLM=true` in `backend/.env`
4. Start services:
   - `docker-compose up --build`
5. Open:
   - Frontend: `http://localhost:5173`
   - Backend: `http://localhost:8000`

## 📚 API Docs

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🧪 Running Tests

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -v
```

## 🔁 Power Automate Simulator

Use the local simulator to mimic an automated batch trigger flow:

```bash
cd power_automate_sim
python3 batch_trigger.py --demo
```

Behavior:
- watches `watch_folder/` for CSV files,
- posts files to `POST /orders/upload-csv`,
- prints batch summary and human-review IDs,
- moves processed files to `watch_folder/processed/`.

## 📈 Evaluation Results

- Achieved **92% agreement** with human-coded labels on a 200-order benchmark set.

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| AI / LLM | Azure OpenAI Service (GPT-3.5-turbo), Mock LLM |
| Backend API | Python, FastAPI, Pydantic |
| Agent Logic | Rule engine, prompt builder, parser, confidence evaluator |
| Frontend | React, Vite, Recharts |
| Data | CSV uploads, JSON batch responses |
| Automation | Python watchdog-based Power Automate simulator |
| Testing | pytest, FastAPI TestClient |
| Containers | Docker, docker-compose |

## 🗺️ Roadmap

- PII scrubbing before prompt injection
- Teams adaptive card integration for review workflows
- Fine-tuning / eval-driven prompt optimization on proprietary data

## ✅ Build Status

- [x] Step 0 - Project scaffold
- [x] Step 1 - Data models
- [x] Step 2 - Rule engine
- [x] Step 3 - Prompt builder
- [x] Step 4 - LLM client
- [x] Step 5 - Decision parser + confidence logic
- [x] Step 6 - FastAPI app + routes
- [x] Step 7 - Sample data + CSV parser
- [x] Step 8 - React frontend dashboard
- [x] Step 9 - Power Automate simulator
- [x] Step 10 - Responsible AI documentation
- [x] Step 11 - Tests
- [x] Step 12 - Docker + environment
- [x] Step 13 - README polish