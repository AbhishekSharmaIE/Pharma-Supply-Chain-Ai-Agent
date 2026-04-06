from datetime import date

from models.order import Order


class PromptBuilder:
    SYSTEM_PROMPT = """You are a pharmaceutical supply chain prioritization agent.
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
}"""

    def build_prompt(self, order: Order, rule_flags: dict[str, bool]) -> tuple[str, str]:
        days_until_expiry = (order.expiry_date - date.today()).days
        rule_summary = self._format_rule_summary(rule_flags)

        user_prompt = f"""Evaluate this pharmaceutical order:

Order details:
- Order ID: {order.order_id}
- Product name: {order.product_name}
- Quantity requested: {order.quantity}
- Customer tier: {order.customer_tier}
- Urgency flag: {order.urgency_flag}
- Stock available: {order.stock_available}
- Expiry date: {order.expiry_date.isoformat()} ({days_until_expiry} days until expiry)
- Customer location: {order.customer_location}
- Warehouse location: {order.warehouse_location}
- Local delivery flag: {rule_flags.get("local_delivery", False)}

Rule summary:
{rule_summary}

Return only the JSON response with priority decision and confidence."""
        return self.SYSTEM_PROMPT, user_prompt

    @staticmethod
    def _format_rule_summary(rule_flags: dict[str, bool]) -> str:
        return "\n".join(
            [
                f"- urgency: {rule_flags.get('urgency', False)}",
                f"- stock_risk: {rule_flags.get('stock_risk', False)}",
                f"- priority_customer: {rule_flags.get('priority_customer', False)}",
                f"- expiry_risk: {rule_flags.get('expiry_risk', False)}",
                f"- local_delivery: {rule_flags.get('local_delivery', False)}",
            ]
        )
