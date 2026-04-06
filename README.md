# Pharma Supply Chain AI Agent

## Build Progress

- [x] Step 0 - Project scaffold created
- [x] Step 1 - Data models (Pydantic)
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
- [ ] Step 12 - Docker + environment
- [ ] Step 13 - Final README polish

### Step 0 Notes

Created the full baseline project structure and placeholder files for backend,
frontend, automation simulator, docs, and container setup so implementation can
proceed incrementally.

### Step 1 Notes

Implemented core backend data contracts in Pydantic v2 style:
- `backend/models/order.py`: `Order` and `OrderBatch`
- `backend/models/response.py`: `PriorityLevel`, `AgentDecision`, `BatchResponse`

### Step 2 Notes

Implemented `backend/agent/rule_engine.py` with:
- `evaluate(order)` for the 5 pre-LLM business rules
- `get_rule_summary(flags)` to generate a readable bullet-list summary for prompt injection

### Step 3 Notes

Implemented `backend/agent/prompt_builder.py` with:
- Static system prompt encoding business objectives, weighted rules, and strict JSON output format
- Dynamic user prompt generation from `Order` + rule flags, including days-until-expiry and structured rule summary

### Step 4 Notes

Implemented `backend/agent/llm_client.py` with:
- `AzureOpenAIClient` using env-configured Azure OpenAI credentials
- `complete(...)` with `temperature=0.2`, `max_tokens=600`, token usage logging, and 3-attempt exponential backoff on rate limiting
- `LLMClientError` for unrecoverable failures
- `MockLLMClient` and `get_llm_client()` toggle via `USE_MOCK_LLM=true`

### Step 5 Notes

Implemented:
- `backend/agent/decision_parser.py` with markdown-fence stripping, safe JSON parsing, required-field validation, strict priority/confidence checks, and `DecisionParseError`
- `backend/agent/confidence.py` with deterministic human-review rules and expiry-risk override (`LOW` -> `MEDIUM`)

### Step 6 Notes

Implemented backend API wiring:
- `backend/main.py` with FastAPI app metadata, CORS for `http://localhost:5173`, and route registration
- `backend/routes/health.py` for `GET /health`
- `backend/routes/orders.py` for `POST /orders/prioritize` and `POST /orders/upload-csv` using async batch processing (`asyncio.gather`)
- Added CSV endpoint error handling (400 malformed/empty CSV, 503 LLM failures)

### Step 7 Notes

Completed data-ingestion baseline:
- `backend/utils/csv_parser.py` parses CSV bytes with `csv.DictReader`, validates via `Order`, and skips invalid rows with warning logs
- `backend/data/sample_orders.csv` populated with 20 realistic pharma orders across Irish locations for local testing and demo flows

### Step 8 Notes

Implemented frontend dashboard foundation in `frontend/`:
- Vite + React app setup (`package.json`, `vite.config.js`, `index.html`, `src/main.jsx`)
- API integration layer in `src/api/agentApi.js` for CSV upload and JSON batch prioritization
- Dashboard + Audit Log pages and all core components (`UploadPanel`, `OrderTable`, `OrderCard`, `ConfidenceGauge`, `HumanReviewQueue`, `SummaryChart`)
- Batch run persistence to localStorage for audit history and interactive order drill-down

### Step 9 Notes

Implemented `power_automate_sim/batch_trigger.py`:
- Watches `power_automate_sim/watch_folder/` for new CSV files using `watchdog` (5-second polling loop)
- Sends each detected CSV to `POST /orders/upload-csv`
- Prints a formatted batch summary (batch id, totals, priority breakdown, human-review order IDs)
- Moves processed files into `power_automate_sim/watch_folder/processed/`
- Supports `--demo` to auto-copy `backend/data/sample_orders.csv` into the watch folder

### Step 10 Notes

Completed `backend/responsible_ai/failure_modes.md` with structured coverage of:
- Hallucination risk and confidence-triggered fallbacks
- Conflict/edge-case deterministic escalation paths
- Model drift benchmarking expectations
- Customer-tier bias monitoring controls
- Data privacy risk and PII-scrubbing roadmap
- Explicit confidence threshold action policy table

### Step 11 Notes

Implemented backend test coverage:
- `backend/tests/conftest.py` sets `USE_MOCK_LLM=true` for test runs
- `backend/tests/test_agent.py` covers rule engine, prompt builder, confidence evaluator, decision parser, and full mock pipeline
- `backend/tests/test_api.py` covers `/health`, `/orders/prioritize`, and `/orders/upload-csv`
- `backend/tests/test_csv_parser.py` covers valid parsing and invalid-row skipping behavior