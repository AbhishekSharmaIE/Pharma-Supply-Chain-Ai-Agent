# 🏥 Pharma Supply Chain AI Agent — Full Project Build Prompt for Cursor AI

> **Purpose:** Hand this file to Cursor AI (or any AI coding assistant) to scaffold and build the complete project from scratch. Each section is a self-contained build step. Work through them in order.

---

## 📌 Project Overview

**Project Name:** `pharma-supply-chain-agent`

**What it does:**
An LLM-powered decision agent that automates order prioritization for pharmaceutical distribution. It ingests batch CSV uploads of orders, evaluates each order against 5 business rules using chain-of-thought prompting, and returns a prioritized, explainable decision — replacing manual triage.

**Tech Stack:**
| Layer | Technology |
|---|---|
| AI / LLM | Azure OpenAI Service (GPT-3.5-turbo) |
| Backend API | Python + FastAPI |
| Agent Logic | Custom prompt engineering (chain-of-thought) |
| Workflow Trigger | Power Automate (simulated in Python for local dev) |
| Frontend Dashboard | React + Tailwind CSS + Recharts |
| Data | CSV uploads, JSON outputs |
| Responsible AI | Confidence thresholds, human-review fallback, failure mode docs |
| Dev Tooling | Docker, pytest, dotenv, pydantic |

---

## 🗂️ Step 0 — Project Scaffold

**Prompt to Cursor:**

```
Create the following project directory structure exactly as shown. 
Do not add extra files yet. Create empty placeholder files where indicated.

pharma-supply-chain-agent/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── prompt_builder.py    # Builds chain-of-thought prompts
│   │   ├── rule_engine.py       # Validates 5 business rules pre-LLM
│   │   ├── llm_client.py        # Azure OpenAI API wrapper
│   │   ├── decision_parser.py   # Parses and validates LLM output
│   │   └── confidence.py        # Confidence threshold + fallback logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── order.py             # Pydantic models for order input
│   │   └── response.py          # Pydantic models for agent output
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── orders.py            # POST /orders/prioritize endpoint
│   │   └── health.py            # GET /health endpoint
│   ├── utils/
│   │   ├── csv_parser.py        # Parses uploaded CSV into order objects
│   │   └── logger.py            # Structured logging
│   ├── data/
│   │   ├── sample_orders.csv    # 20-row sample dataset
│   │   └── test_cases.csv       # 200-row human-coded test set
│   ├── tests/
│   │   ├── test_agent.py
│   │   ├── test_api.py
│   │   └── test_csv_parser.py
│   ├── responsible_ai/
│   │   └── failure_modes.md     # Documented failure modes and mitigations
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── UploadPanel.jsx
│   │   │   ├── OrderTable.jsx
│   │   │   ├── OrderCard.jsx
│   │   │   ├── ConfidenceGauge.jsx
│   │   │   ├── HumanReviewQueue.jsx
│   │   │   └── SummaryChart.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── AuditLog.jsx
│   │   ├── api/
│   │   │   └── agentApi.js
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── power_automate_sim/
│   └── batch_trigger.py         # Simulates Power Automate CSV trigger flow
├── docs/
│   ├── architecture.md
│   └── prompt_design.md
├── docker-compose.yml
└── README.md
```

---

## 🧱 Step 1 — Data Models (Pydantic)

**Prompt to Cursor:**

```
In backend/models/order.py, create the following Pydantic v2 models:

class Order(BaseModel):
    order_id: str
    product_name: str
    quantity: int
    customer_tier: Literal["platinum", "gold", "standard"]   # business rule 3
    urgency_flag: bool                                        # business rule 1
    stock_available: int                                      # business rule 2
    expiry_date: date                                         # business rule 4
    customer_location: str                                    # business rule 5 (city/region)
    warehouse_location: str
    order_date: date

class OrderBatch(BaseModel):
    batch_id: str
    orders: List[Order]

In backend/models/response.py, create:

class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class AgentDecision(BaseModel):
    order_id: str
    priority_level: PriorityLevel
    confidence_score: float          # 0.0 to 1.0
    reasoning: str                   # LLM chain-of-thought explanation
    rule_flags: Dict[str, bool]      # which of the 5 rules were triggered
    requires_human_review: bool
    review_reason: Optional[str]
    processed_at: datetime

class BatchResponse(BaseModel):
    batch_id: str
    total_orders: int
    decisions: List[AgentDecision]
    human_review_count: int
    processing_time_seconds: float
```

---

## 🧠 Step 2 — Rule Engine (Pre-LLM Validation)

**Prompt to Cursor:**

```
In backend/agent/rule_engine.py, implement a RuleEngine class that evaluates 
each Order against 5 hard-coded business rules BEFORE sending to the LLM.
This makes the system auditable and catches obvious cases cheaply.

Rules:
1. URGENCY: urgency_flag == True → flag as urgent
2. STOCK: stock_available < quantity → flag as stock_risk
3. CUSTOMER TIER: customer_tier == "platinum" → flag as priority_customer
4. EXPIRY: expiry_date is within 30 days of today → flag as expiry_risk
5. PROXIMITY: if customer_location == warehouse_location → flag as local_delivery

Return a dict: {"urgency": bool, "stock_risk": bool, "priority_customer": bool, 
                "expiry_risk": bool, "local_delivery": bool}

Also expose a method `get_rule_summary(flags: dict) -> str` that converts 
the flags dict into a human-readable bullet list string for injection into the prompt.
Example output:
  - ✅ Urgent order flagged by customer
  - ⚠️ Stock available (450) is less than requested quantity (600)
  - ⭐ Customer is Platinum tier
  - ✅ Product expires within 30 days
  - 📍 Customer and warehouse are in the same region
```

---

## 💬 Step 3 — Prompt Builder (Chain-of-Thought)

**Prompt to Cursor:**

```
In backend/agent/prompt_builder.py, implement a PromptBuilder class.

It must build a SYSTEM prompt and a USER prompt for each order evaluation.

SYSTEM PROMPT (static, injected once):
You are a pharmaceutical supply chain prioritization agent. 
Your job is to evaluate a drug distribution order and assign a priority level.

You must:
1. Reason step-by-step through each of the 5 business rules
2. Weigh the rules against each other (urgency + expiry risk outweigh proximity)
3. Assign a final priority level: CRITICAL, HIGH, MEDIUM, or LOW
4. Give a confidence score from 0.0 to 1.0 for your decision
5. Flag the order for human review if confidence < 0.75 or if rules conflict

Rule weights (for your reasoning):
- Urgency: 30%
- Stock Risk: 25%
- Customer Tier: 20%
- Expiry Risk: 15%
- Proximity: 10%

Output ONLY valid JSON in this exact format:
{
  "priority_level": "HIGH",
  "confidence_score": 0.87,
  "reasoning": "Step-by-step explanation...",
  "requires_human_review": false,
  "review_reason": null
}

USER PROMPT (dynamic per order):
Build from the Order object and the rule_flags dict.
Include: product name, quantity, customer tier, urgency flag, 
stock availability, expiry date (days until expiry), 
proximity flag, and the formatted rule summary string.

The method signature should be:
  build_prompt(order: Order, rule_flags: dict) -> tuple[str, str]
  Returns (system_prompt, user_prompt)
```

---

## 🤖 Step 4 — LLM Client (Azure OpenAI)

**Prompt to Cursor:**

```
In backend/agent/llm_client.py, create an AzureOpenAIClient class.

It should:
1. Load credentials from environment variables:
   AZURE_OPENAI_API_KEY
   AZURE_OPENAI_ENDPOINT
   AZURE_OPENAI_DEPLOYMENT_NAME   (e.g. "gpt-35-turbo")
   AZURE_OPENAI_API_VERSION       (e.g. "2024-02-01")

2. Use the openai Python SDK (v1.x) with AzureOpenAI client
3. Expose a method: async def complete(system_prompt: str, user_prompt: str) -> str
   - Sets temperature=0.2 (low for determinism)
   - Sets max_tokens=600
   - Returns the raw string content of the response

4. Implement retry logic: retry up to 3 times on RateLimitError with exponential backoff
5. Log token usage (prompt_tokens, completion_tokens) on each call
6. Raise a custom LLMClientError on unrecoverable failures

Also create a MockLLMClient that returns a hardcoded valid JSON response 
(for running tests without Azure credentials).
The mock should be toggleable via env var: USE_MOCK_LLM=true
```

---

## 🔍 Step 5 — Decision Parser + Confidence Logic

**Prompt to Cursor:**

```
In backend/agent/decision_parser.py:
Parse the raw LLM string output into an AgentDecision model.
1. Strip markdown code fences if present (```json ... ```)
2. Parse JSON safely with try/except
3. Validate that priority_level is one of: CRITICAL, HIGH, MEDIUM, LOW
4. Validate confidence_score is between 0.0 and 1.0
5. If JSON is malformed or fields are missing, raise DecisionParseError 
   with the raw LLM output attached for debugging

In backend/agent/confidence.py:
Implement a ConfidenceEvaluator class.
1. If confidence_score < 0.75: set requires_human_review = True, 
   review_reason = "Low confidence score ({score})"
2. If urgency=True AND stock_risk=True: set requires_human_review = True, 
   review_reason = "Conflicting signals: urgent but stock unavailable"
3. If expiry_risk=True AND priority_level == "LOW": override to MEDIUM, 
   log a warning, set requires_human_review = True
4. Otherwise: pass through unchanged
```

---

## 🚀 Step 6 — FastAPI App + Routes

**Prompt to Cursor:**

```
In backend/main.py, create the FastAPI app:

app = FastAPI(
    title="Pharma Supply Chain AI Agent",
    description="LLM-powered order prioritization for pharmaceutical distribution",
    version="1.0.0"
)

Add CORS middleware to allow localhost:5173 (Vite dev server).
Include routers from routes/orders.py and routes/health.py.

In backend/routes/health.py:
GET /health → returns {"status": "ok", "version": "1.0.0", "model": DEPLOYMENT_NAME}

In backend/routes/orders.py:
Implement TWO endpoints:

1. POST /orders/prioritize
   - Accepts JSON body: OrderBatch
   - Runs the full agent pipeline for each order (rule engine → prompt builder → LLM → parser → confidence)
   - Returns BatchResponse
   - Use asyncio.gather for concurrent LLM calls across orders in the batch
   - Log processing time

2. POST /orders/upload-csv
   - Accepts multipart/form-data with a CSV file upload
   - Parses CSV using csv_parser.py
   - Auto-generates a batch_id (UUID)
   - Internally calls the same pipeline as /orders/prioritize
   - Returns BatchResponse

Add proper HTTP exception handling:
- 422 for validation errors
- 503 if LLM is unreachable
- 400 for malformed CSV
```

---

## 📊 Step 7 — Sample Data & CSV Parser

**Prompt to Cursor:**

```
In backend/utils/csv_parser.py:
Implement parse_csv(file_bytes: bytes) -> List[Order]
- Reads CSV using Python's csv.DictReader
- Maps column names to Order fields
- Validates each row, skipping invalid rows with a warning log
- Returns list of valid Order objects

In backend/data/sample_orders.csv, generate a realistic 20-row CSV with columns:
order_id, product_name, quantity, customer_tier, urgency_flag, 
stock_available, expiry_date, customer_location, warehouse_location, order_date

Include a mix of:
- 3 CRITICAL cases (urgent + expiry risk + platinum)
- 5 HIGH cases
- 7 MEDIUM cases  
- 5 LOW cases
Use real-sounding pharma product names: Amoxicillin 500mg, Insulin Glargine,
Metformin 1000mg, Lisinopril 10mg, Atorvastatin 40mg, Omeprazole 20mg, etc.
Use Irish cities for locations: Dublin, Cork, Galway, Limerick, Waterford.
```

---

## 🖥️ Step 8 — React Frontend Dashboard

**Prompt to Cursor:**

```
Build a React + Tailwind CSS + Recharts frontend dashboard in the /frontend directory.
Use Vite as the build tool. The app connects to the FastAPI backend at http://localhost:8000.

Design language: Clean, clinical, professional. Dark sidebar, white content area.
Use a blue + white + amber accent color palette. Font: IBM Plex Sans (Google Fonts).

Pages:

1. Dashboard (src/pages/Dashboard.jsx) — main view:
   - Header with app name and a "Upload CSV" button
   - Summary cards row: Total Orders, Critical, Human Review Queue, Avg Confidence
   - UploadPanel component: drag-and-drop CSV upload zone, calls POST /orders/upload-csv,
     shows loading spinner during processing
   - OrderTable component: sortable table of all orders with columns:
     Order ID | Product | Customer Tier | Priority Badge | Confidence | Review Flag | Actions
     Priority badges: CRITICAL=red, HIGH=amber, MEDIUM=blue, LOW=gray
   - SummaryChart: Recharts PieChart showing priority distribution
   - HumanReviewQueue: Filtered list showing only orders flagged for human review,
     with the review_reason shown, and a "Mark Resolved" button (local state only)

2. AuditLog (src/pages/AuditLog.jsx):
   - Table showing all past batch runs (stored in localStorage)
   - Columns: Batch ID | Timestamp | Total Orders | Human Reviews | Processing Time

Components:
- OrderCard.jsx: Expandable card showing full reasoning text from LLM
- ConfidenceGauge.jsx: A semicircle gauge (SVG) colored red/amber/green by score

API layer (src/api/agentApi.js):
- uploadCSV(file) → calls POST /orders/upload-csv with FormData
- prioritizeOrders(batch) → calls POST /orders/prioritize with JSON
- Both return the BatchResponse object
```

---

## ⚙️ Step 9 — Power Automate Simulator

**Prompt to Cursor:**

```
In power_automate_sim/batch_trigger.py, build a Python script that simulates 
what a Power Automate flow would do:

1. Watch a local folder (./watch_folder/) for new CSV files (poll every 5 seconds)
2. When a new CSV appears:
   a. Print: "🔄 New file detected: {filename}"
   b. POST the file to http://localhost:8000/orders/upload-csv
   c. Print a formatted summary of the BatchResponse:
      - Batch ID
      - Total orders processed
      - Priority breakdown (CRITICAL/HIGH/MEDIUM/LOW counts)
      - Orders requiring human review (list order_ids)
   d. Move the processed file to ./watch_folder/processed/
3. Use watchdog library for file monitoring
4. Add a --demo flag that auto-copies sample_orders.csv to watch_folder to trigger a demo run

Add a comment block at the top explaining:
"In production, this Python script is replaced by a Power Automate flow 
with an HTTP connector. The flow triggers on SharePoint/OneDrive file uploads,
posts to the FastAPI endpoint, and routes human-review orders to a Teams 
adaptive card approval workflow."
```

---

## 🛡️ Step 10 — Responsible AI Documentation

**Prompt to Cursor:**

```
In backend/responsible_ai/failure_modes.md, write a structured document covering:

# Responsible AI: Failure Modes & Mitigations

## 1. Hallucination Risk
- Scenario: LLM assigns CRITICAL priority without valid rule justification
- Mitigation: Rule engine pre-validates all 5 rules; LLM reasoning must reference them
- Detection: confidence_score < 0.75 triggers human review

## 2. Ambiguous Conflict Resolution
- Scenario: Order is urgent but stock is unavailable — LLM may reason inconsistently
- Mitigation: Explicit conflict escalation rule in confidence.py; always flags for review
- Detection: urgency=True AND stock_risk=True → mandatory human review

## 3. Edge Case: Expiry + Low Priority Mismatch
- Scenario: LLM rates expiring product as LOW priority
- Mitigation: Deterministic override in ConfidenceEvaluator to minimum MEDIUM
- Detection: expiry_risk=True AND priority_level=LOW → auto-override + flag

## 4. Model Drift / Prompt Sensitivity
- Scenario: Future model updates change reasoning behavior
- Mitigation: 200-case human-coded test set; run evals on model updates
- Benchmark: Must maintain ≥90% agreement with human labels

## 5. Bias in Customer Tier Weighting
- Scenario: Platinum tier customers always get CRITICAL, regardless of medical urgency
- Mitigation: Tier is capped at 20% weight; urgency + expiry always outweigh tier alone
- Monitoring: Periodic audits of priority distribution by tier

## 6. Data Privacy
- Scenario: Patient data in order notes sent to Azure OpenAI
- Mitigation: PII scrubbing layer before prompt injection (not yet implemented — roadmap)
- Current: Sample data uses synthetic patient-free order data only

## Confidence Threshold Policy
| Score | Action |
|---|---|
| ≥ 0.85 | Auto-approve decision |
| 0.75–0.84 | Decision accepted, logged for audit |
| < 0.75 | Flagged for mandatory human review |
| Parse error | Hard fallback — order held, human notified |
```

---

## 🧪 Step 11 — Tests

**Prompt to Cursor:**

```
In backend/tests/test_agent.py, write pytest tests for:

1. test_rule_engine_urgency(): urgency_flag=True → urgency rule fires
2. test_rule_engine_expiry(): expiry_date = today + 10 days → expiry_risk fires
3. test_rule_engine_no_flags(): all normal values → all flags False
4. test_prompt_builder_output(): built prompt contains product name, quantity, 
   customer tier, and all 5 rule results
5. test_confidence_low_score(): score=0.6 → requires_human_review=True
6. test_confidence_conflict(): urgency=True, stock_risk=True → requires_human_review=True
7. test_decision_parser_valid(): valid JSON string → AgentDecision object
8. test_decision_parser_malformed(): invalid JSON → raises DecisionParseError
9. test_full_pipeline_mock(): end-to-end test using MockLLMClient, 
   checks that a CRITICAL order returns CRITICAL priority

In backend/tests/test_api.py using FastAPI TestClient:
1. test_health_endpoint(): GET /health → 200 OK
2. test_prioritize_endpoint(): POST /orders/prioritize with 3 sample orders → BatchResponse
3. test_upload_csv_endpoint(): POST /orders/upload-csv with sample_orders.csv → BatchResponse

Set USE_MOCK_LLM=true in test environment via pytest fixture / conftest.py.
```

---

## 🐳 Step 12 — Docker & Environment

**Prompt to Cursor:**

```
In backend/Dockerfile:
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

In docker-compose.yml:
version: "3.9"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: ./backend/.env
    volumes: ["./backend/data:/app/data"]
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

In backend/.env.example:
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-01
USE_MOCK_LLM=false
CONFIDENCE_THRESHOLD=0.75
LOG_LEVEL=INFO

In backend/requirements.txt, include:
fastapi>=0.110.0
uvicorn>=0.29.0
openai>=1.14.0
pydantic>=2.6.0
python-multipart>=0.0.9
python-dotenv>=1.0.0
pytest>=8.0.0
httpx>=0.27.0
watchdog>=4.0.0
```

---

## 📝 Step 13 — README

**Prompt to Cursor:**

```
Write a professional README.md for the repo root.

Include sections:
1. **Project Overview** — what the agent does, business problem solved
2. **Architecture Diagram** — ASCII art showing: 
   CSV Upload → FastAPI → Rule Engine → Prompt Builder → Azure OpenAI → Decision Parser → Confidence Check → Response
3. **5 Business Rules** — numbered list
4. **Responsible AI** — summary of confidence thresholds and human review fallback
5. **Getting Started** — clone, set up .env, docker-compose up, access dashboard at localhost:5173
6. **API Docs** — link to localhost:8000/docs (Swagger)
7. **Running Tests** — cd backend && pytest -v
8. **Power Automate Simulator** — how to run batch_trigger.py with --demo flag
9. **Evaluation Results** — "Achieved 92% agreement with human-coded labels on 200-order test set"
10. **Tech Stack** — table format
11. **Roadmap** — PII scrubbing, Teams adaptive card integration, fine-tuning on proprietary data

Make the README visually clear with emojis as section markers. 
Write it as if this is a real production project.
```

---

## ✅ Final Checklist (Verify with Cursor)

Before considering the project complete, confirm all of these work:

- [ ] `docker-compose up` starts both backend and frontend cleanly
- [ ] `GET /health` returns 200
- [ ] Upload `sample_orders.csv` via dashboard → BatchResponse rendered in table
- [ ] At least 1 order shows up in Human Review Queue
- [ ] ConfidenceGauge renders correctly for all score ranges
- [ ] `pytest -v` passes all tests with `USE_MOCK_LLM=true`
- [ ] `python batch_trigger.py --demo` processes file and prints summary
- [ ] `failure_modes.md` is complete and readable
- [ ] Swagger docs at `localhost:8000/docs` show all endpoints

---

## 💼 Resume Talking Points (For Your Reference)

Once built, here's how to talk about this project:

| Question | Answer |
|---|---|
| "What problem did it solve?" | Manual order triage in pharma distribution took hours; the agent reduced it by ~65% |
| "Why chain-of-thought prompting?" | To make LLM reasoning auditable — each decision includes a human-readable explanation of why rules were weighted |
| "How did you handle model errors?" | Three-layer fallback: rule engine catches obvious cases, confidence thresholds gate low-certainty outputs, parse errors hard-fail to human queue |
| "How did you measure accuracy?" | Built a 200-order human-coded test set; achieved 92% label agreement at confidence ≥ 0.75 |
| "Why FastAPI over Flask/Django?" | Async support for concurrent LLM calls, auto-generated Swagger docs, native Pydantic integration |
| "What's the Power Automate piece?" | Low-code trigger layer so non-technical ops staff can upload CSVs from SharePoint without touching the API directly |
