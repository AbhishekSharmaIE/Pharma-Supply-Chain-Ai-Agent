import asyncio
import logging
import time
import uuid
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from agent.confidence import ConfidenceEvaluator
from agent.decision_parser import DecisionParseError, DecisionParser
from agent.llm_client import LLMClientError, get_llm_client
from agent.prompt_builder import PromptBuilder
from agent.rule_engine import RuleEngine
from models.order import Order, OrderBatch
from models.response import AgentDecision, BatchResponse
from utils.csv_parser import parse_csv

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


rule_engine = RuleEngine()
prompt_builder = PromptBuilder()
decision_parser = DecisionParser()
confidence_evaluator = ConfidenceEvaluator()


async def _process_order(order: Order) -> AgentDecision:
    rule_flags = rule_engine.evaluate(order)
    system_prompt, user_prompt = prompt_builder.build_prompt(order, rule_flags)

    try:
        llm_client = get_llm_client()
        raw_output = await llm_client.complete(system_prompt, user_prompt)
    except LLMClientError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        decision = decision_parser.parse(raw_output, order.order_id, rule_flags)
    except DecisionParseError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Unable to parse LLM response for order {order.order_id}",
        ) from exc

    return confidence_evaluator.evaluate(decision, rule_flags)


async def _process_batch(batch_id: str, orders: List[Order]) -> BatchResponse:
    start = time.perf_counter()
    decisions = await asyncio.gather(*[_process_order(order) for order in orders])
    processing_time_seconds = time.perf_counter() - start
    human_review_count = sum(1 for decision in decisions if decision.requires_human_review)

    logger.info(
        "Processed batch_id=%s orders=%s human_review=%s in %.2fs",
        batch_id,
        len(orders),
        human_review_count,
        processing_time_seconds,
    )

    return BatchResponse(
        batch_id=batch_id,
        total_orders=len(orders),
        decisions=decisions,
        human_review_count=human_review_count,
        processing_time_seconds=processing_time_seconds,
    )


@router.post("/prioritize", response_model=BatchResponse)
async def prioritize_orders(batch: OrderBatch) -> BatchResponse:
    return await _process_batch(batch.batch_id, batch.orders)


@router.post("/upload-csv", response_model=BatchResponse)
async def upload_csv(file: UploadFile = File(...)) -> BatchResponse:
    try:
        file_bytes = await file.read()
        orders = parse_csv(file_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not orders:
        raise HTTPException(status_code=400, detail="No valid orders found in CSV.")

    batch_id = str(uuid.uuid4())
    return await _process_batch(batch_id, orders)
