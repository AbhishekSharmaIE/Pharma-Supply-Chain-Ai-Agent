from datetime import date

from models.order import Order


class RuleEngine:
    def evaluate(self, order: Order) -> dict[str, bool]:
        return {
            "urgency": order.urgency_flag is True,
            "stock_risk": order.stock_available < order.quantity,
            "priority_customer": order.customer_tier == "platinum",
            "expiry_risk": (order.expiry_date - date.today()).days <= 30,
            "local_delivery": order.customer_location == order.warehouse_location,
        }

    def get_rule_summary(self, flags: dict[str, bool]) -> str:
        bullets: list[str] = []
        bullets.append(
            "- ✅ Urgent order flagged by customer"
            if flags.get("urgency")
            else "- ⬜ Order not marked urgent"
        )
        bullets.append(
            "- ⚠️ Stock available is less than requested quantity"
            if flags.get("stock_risk")
            else "- ✅ Stock available is sufficient for requested quantity"
        )
        bullets.append(
            "- ⭐ Customer is Platinum tier"
            if flags.get("priority_customer")
            else "- ⬜ Customer is not Platinum tier"
        )
        bullets.append(
            "- ✅ Product expires within 30 days"
            if flags.get("expiry_risk")
            else "- ✅ Product expiry is outside 30-day risk window"
        )
        bullets.append(
            "- 📍 Customer and warehouse are in the same region"
            if flags.get("local_delivery")
            else "- ⬜ Customer and warehouse are in different regions"
        )
        return "\n".join(bullets)
