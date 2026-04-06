from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AgentDecision(BaseModel):
    order_id: str
    priority_level: PriorityLevel
    confidence_score: float
    reasoning: str
    rule_flags: Dict[str, bool]
    requires_human_review: bool
    review_reason: Optional[str]
    processed_at: datetime


class BatchResponse(BaseModel):
    batch_id: str
    total_orders: int
    decisions: List[AgentDecision]
    human_review_count: int
    processing_time_seconds: float
