# Pharma Supply Chain AI Agent

## Build Progress

- [x] Step 0 - Project scaffold created
- [x] Step 1 - Data models (Pydantic)
- [x] Step 2 - Rule engine
- [x] Step 3 - Prompt builder
- [x] Step 4 - LLM client
- [x] Step 5 - Decision parser + confidence logic
- [ ] Step 6 - FastAPI app + routes
- [ ] Step 7 - Sample data + CSV parser
- [ ] Step 8 - React frontend dashboard
- [ ] Step 9 - Power Automate simulator
- [ ] Step 10 - Responsible AI documentation
- [ ] Step 11 - Tests
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