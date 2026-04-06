import csv
import io
import logging
from datetime import date, timedelta
from typing import List

from pydantic import ValidationError

from models.order import Order

logger = logging.getLogger(__name__)

ORDER_HEADERS = {
    "order_id",
    "product_name",
    "quantity",
    "customer_tier",
    "urgency_flag",
    "stock_available",
    "expiry_date",
    "customer_location",
    "warehouse_location",
    "order_date",
}

LEGACY_HEADERS = {
    "ID",
    "Stage",
    "Activity",
    "Description",
    "Cost (GHS)",
    "Revenue (GHS)",
    "Time (Days)",
    "Region",
}


def parse_csv(file_bytes: bytes) -> List[Order]:
    try:
        decoded = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise ValueError("CSV is missing header row.")

    header_set = set(reader.fieldnames)
    use_legacy_mapping = LEGACY_HEADERS.issubset(header_set) and not ORDER_HEADERS.issubset(
        header_set
    )

    orders: List[Order] = []
    for index, row in enumerate(reader, start=2):
        try:
            payload = _map_legacy_row(row, index) if use_legacy_mapping else row
            order = Order.model_validate(payload)
            orders.append(order)
        except ValidationError as exc:
            logger.warning("Skipping invalid CSV row %s: %s", index, exc)

    return orders


def _parse_money(value: str | None) -> int:
    if not value:
        return 0
    cleaned = value.replace(",", "").strip()
    if not cleaned:
        return 0
    try:
        return int(float(cleaned))
    except ValueError:
        return 0


def _parse_time_days(value: str | None) -> int:
    if not value:
        return 0
    cleaned = value.strip().lower()
    if cleaned == "ongoing":
        return 365
    try:
        return int(cleaned)
    except ValueError:
        return 0


def _map_legacy_row(row: dict, row_index: int) -> dict:
    stage = (row.get("Stage") or "").strip()
    region = (row.get("Region") or "National").strip()
    activity = (row.get("Activity") or "").strip()
    item_id = (row.get("ID") or "").strip()

    if not item_id:
        item_id = str(row_index)
    if not activity:
        activity = "Unspecified Activity"

    cost = _parse_money(row.get("Cost (GHS)"))
    revenue = _parse_money(row.get("Revenue (GHS)"))
    duration_days = _parse_time_days(row.get("Time (Days)"))

    quantity = max(10, min(5000, cost // 10000 if cost else (duration_days or 30)))
    stock_available = max(0, quantity + (revenue // 20000) - 20)

    if stage in {"Distribution", "Post-Market"}:
        customer_tier = "platinum"
    elif stage == "Sales":
        customer_tier = "gold"
    else:
        customer_tier = "standard"

    urgency_flag = stage in {"Distribution", "Post-Market"} or duration_days <= 30
    expiry_days = max(7, min(365, duration_days if duration_days else 120))
    expiry_date = date.today() + timedelta(days=expiry_days)
    order_date = date.today()

    warehouse_location = (
        "Greater Accra" if region in {"National", "International", "West Africa"} else region
    )

    return {
        "order_id": f"LEGACY-{item_id}",
        "product_name": activity,
        "quantity": quantity,
        "customer_tier": customer_tier,
        "urgency_flag": urgency_flag,
        "stock_available": stock_available,
        "expiry_date": expiry_date.isoformat(),
        "customer_location": region,
        "warehouse_location": warehouse_location,
        "order_date": order_date.isoformat(),
    }
