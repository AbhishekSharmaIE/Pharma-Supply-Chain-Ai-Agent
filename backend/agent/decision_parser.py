import json
from datetime import datetime, timezone
from typing import Any

from models.response import AgentDecision, PriorityLevel


class DecisionParseError(Exception):
    def __init__(self, message: str, raw_output: str) -> None:
        super().__init__(message)
        self.raw_output = raw_output


class DecisionParser:
    def parse(self, raw_output: str, order_id: str, rule_flags: dict[str, bool]) -> AgentDecision:
        cleaned = self._strip_code_fences(raw_output)
        data = self._parse_json(cleaned, raw_output)

        priority_raw = data.get("priority_level")
        confidence_raw = data.get("confidence_score")

        if priority_raw not in {level.value for level in PriorityLevel}:
            raise DecisionParseError(
                f"Invalid priority_level: {priority_raw}",
                raw_output=raw_output,
            )

        if not isinstance(confidence_raw, (float, int)):
            raise DecisionParseError(
                "confidence_score must be a number.",
                raw_output=raw_output,
            )
        confidence_score = float(confidence_raw)
        if not (0.0 <= confidence_score <= 1.0):
            raise DecisionParseError(
                f"confidence_score out of bounds: {confidence_score}",
                raw_output=raw_output,
            )

        try:
            return AgentDecision(
                order_id=order_id,
                priority_level=PriorityLevel(priority_raw),
                confidence_score=confidence_score,
                reasoning=str(data["reasoning"]),
                rule_flags=rule_flags,
                requires_human_review=bool(data["requires_human_review"]),
                review_reason=data.get("review_reason"),
                processed_at=datetime.now(timezone.utc),
            )
        except KeyError as exc:
            raise DecisionParseError(
                f"Missing required field: {exc}",
                raw_output=raw_output,
            ) from exc
        except Exception as exc:  # noqa: BLE001
            raise DecisionParseError(
                f"Failed to construct AgentDecision: {exc}",
                raw_output=raw_output,
            ) from exc

    @staticmethod
    def _strip_code_fences(raw_output: str) -> str:
        stripped = raw_output.strip()
        if stripped.startswith("```") and stripped.endswith("```"):
            lines = stripped.splitlines()
            if len(lines) >= 2:
                return "\n".join(lines[1:-1]).strip()
        return stripped

    @staticmethod
    def _parse_json(cleaned: str, raw_output: str) -> dict[str, Any]:
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise DecisionParseError(
                f"Malformed JSON output: {exc}",
                raw_output=raw_output,
            ) from exc

        if not isinstance(parsed, dict):
            raise DecisionParseError(
                "LLM output JSON must be an object.",
                raw_output=raw_output,
            )
        return parsed
