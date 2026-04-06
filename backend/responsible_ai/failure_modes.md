# Responsible AI: Failure Modes & Mitigations

## 1. Hallucination Risk
- Scenario: LLM assigns CRITICAL priority without valid rule justification
- Mitigation: Rule engine pre-validates all 5 rules; LLM reasoning must reference them
- Detection: confidence_score < 0.75 triggers human review

## 2. Ambiguous Conflict Resolution
- Scenario: Order is urgent but stock is unavailable - LLM may reason inconsistently
- Mitigation: Explicit conflict escalation rule in confidence.py; always flags for review
- Detection: urgency=True AND stock_risk=True -> mandatory human review

## 3. Edge Case: Expiry + Low Priority Mismatch
- Scenario: LLM rates expiring product as LOW priority
- Mitigation: Deterministic override in ConfidenceEvaluator to minimum MEDIUM
- Detection: expiry_risk=True AND priority_level=LOW -> auto-override + flag

## 4. Model Drift / Prompt Sensitivity
- Scenario: Future model updates change reasoning behavior
- Mitigation: 200-case human-coded test set; run evals on model updates
- Benchmark: Must maintain >=90% agreement with human labels

## 5. Bias in Customer Tier Weighting
- Scenario: Platinum tier customers always get CRITICAL, regardless of medical urgency
- Mitigation: Tier is capped at 20% weight; urgency + expiry always outweigh tier alone
- Monitoring: Periodic audits of priority distribution by tier

## 6. Data Privacy
- Scenario: Patient data in order notes sent to Azure OpenAI
- Mitigation: PII scrubbing layer before prompt injection (not yet implemented - roadmap)
- Current: Sample data uses synthetic patient-free order data only

## Confidence Threshold Policy

| Score | Action |
|---|---|
| >= 0.85 | Auto-approve decision |
| 0.75-0.84 | Decision accepted, logged for audit |
| < 0.75 | Flagged for mandatory human review |
| Parse error | Hard fallback - order held, human notified |
