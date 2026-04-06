import logging

from backend.models.response import AgentDecision, PriorityLevel

logger = logging.getLogger(__name__)


class ConfidenceEvaluator:
    def evaluate(self, decision: AgentDecision, rule_flags: dict[str, bool]) -> AgentDecision:
        updated = decision.model_copy(deep=True)
        review_reasons: list[str] = []

        if updated.confidence_score < 0.75:
            review_reasons.append(
                f"Low confidence score ({updated.confidence_score:.2f})"
            )

        if rule_flags.get("urgency") and rule_flags.get("stock_risk"):
            review_reasons.append(
                "Conflicting signals: urgent but stock unavailable"
            )

        if rule_flags.get("expiry_risk") and updated.priority_level == PriorityLevel.LOW:
            logger.warning(
                "Overriding LOW priority to MEDIUM because expiry_risk is true for order_id=%s",
                updated.order_id,
            )
            updated.priority_level = PriorityLevel.MEDIUM
            review_reasons.append("Expiry risk override applied: LOW -> MEDIUM")

        if review_reasons:
            updated.requires_human_review = True
            updated.review_reason = " | ".join(review_reasons)

        return updated
