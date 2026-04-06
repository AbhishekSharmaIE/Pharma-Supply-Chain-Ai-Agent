import csv
import io
import logging
from typing import List

from pydantic import ValidationError

from models.order import Order

logger = logging.getLogger(__name__)


def parse_csv(file_bytes: bytes) -> List[Order]:
    try:
        decoded = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc

    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise ValueError("CSV is missing header row.")

    orders: List[Order] = []
    for index, row in enumerate(reader, start=2):
        try:
            order = Order.model_validate(row)
            orders.append(order)
        except ValidationError as exc:
            logger.warning("Skipping invalid CSV row %s: %s", index, exc)

    return orders
