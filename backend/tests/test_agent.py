from datetime import date, datetime, timedelta, timezone

import pytest

from agent.confidence import ConfidenceEvaluator
from agent.decision_parser import DecisionParseError, DecisionParser
from agent.prompt_builder import PromptBuilder
from agent.rule_engine import RuleEngine
from models.order import Order
from models.response import AgentDecision, PriorityLevel
from routes.orders import _process_order


def make_order(**overrides):
    data = {
        "order_id": "ORD-TEST-001",
        "product_name": "Amoxicillin 500mg",
        "quantity": 100,
        "customer_tier": "gold",
        "urgency_flag": False,
        "stock_available": 200,
        "expiry_date": date.today() + timedelta(days=60),
        "customer_location": "Dublin",
        "warehouse_location": "Cork",
        "order_date": date.today(),
    }
    data.update(overrides)
    return Order(**data)


def test_rule_engine_urgency():
    order = make_order(urgency_flag=True)
    flags = RuleEngine().evaluate(order)
    assert flags["urgency"] is True


def test_rule_engine_expiry():
    order = make_order(expiry_date=date.today() + timedelta(days=10))
    flags = RuleEngine().evaluate(order)
    assert flags["expiry_risk"] is True


def test_rule_engine_no_flags():
    order = make_order()
    flags = RuleEngine().evaluate(order)
    assert all(value is False for value in flags.values())


def test_prompt_builder_output():
    order = make_order(quantity=250, customer_tier="platinum")
    flags = RuleEngine().evaluate(order)
    system_prompt, user_prompt = PromptBuilder().build_prompt(order, flags)
    assert "pharmaceutical supply chain prioritization agent" in system_prompt
    assert order.product_name in user_prompt
    assert str(order.quantity) in user_prompt
    assert order.customer_tier in user_prompt
    assert "urgency:" in user_prompt
    assert "stock_risk:" in user_prompt
    assert "priority_customer:" in user_prompt
    assert "expiry_risk:" in user_prompt
    assert "local_delivery:" in user_prompt


def test_confidence_low_score():
    decision = AgentDecision(
        order_id="ORD-1",
        priority_level=PriorityLevel.HIGH,
        confidence_score=0.6,
        reasoning="Low certainty",
        rule_flags={},
        requires_human_review=False,
        review_reason=None,
        processed_at=datetime.now(timezone.utc),
    )
    updated = ConfidenceEvaluator().evaluate(decision, {})
    assert updated.requires_human_review is True


def test_confidence_conflict():
    decision = AgentDecision(
        order_id="ORD-2",
        priority_level=PriorityLevel.HIGH,
        confidence_score=0.9,
        reasoning="Conflict",
        rule_flags={},
        requires_human_review=False,
        review_reason=None,
        processed_at=datetime.now(timezone.utc),
    )
    updated = ConfidenceEvaluator().evaluate(
        decision,
        {"urgency": True, "stock_risk": True, "priority_customer": False, "expiry_risk": False, "local_delivery": False},
    )
    assert updated.requires_human_review is True
    assert "urgent but stock unavailable" in (updated.review_reason or "")


def test_decision_parser_valid():
    raw = """
    {
      "priority_level": "CRITICAL",
      "confidence_score": 0.93,
      "reasoning": "Urgent and stock constrained.",
      "requires_human_review": false,
      "review_reason": null
    }
    """
    decision = DecisionParser().parse(raw, "ORD-3", {"urgency": True})
    assert decision.order_id == "ORD-3"
    assert decision.priority_level == PriorityLevel.CRITICAL


def test_decision_parser_malformed():
    raw = "not-json"
    with pytest.raises(DecisionParseError):
        DecisionParser().parse(raw, "ORD-4", {})


@pytest.mark.asyncio
async def test_full_pipeline_mock(monkeypatch):
    async def fake_complete(self, system_prompt: str, user_prompt: str) -> str:
        del self, system_prompt, user_prompt
        return """
        {
          "priority_level": "CRITICAL",
          "confidence_score": 0.91,
          "reasoning": "Urgent and highly time-sensitive.",
          "requires_human_review": false,
          "review_reason": null
        }
        """

    monkeypatch.setattr("agent.llm_client.MockLLMClient.complete", fake_complete)
    order = make_order(urgency_flag=True)
    decision = await _process_order(order)
    assert decision.priority_level == PriorityLevel.CRITICAL
