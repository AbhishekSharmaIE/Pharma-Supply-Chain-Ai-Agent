from datetime import date
from typing import List, Literal

from pydantic import BaseModel


class Order(BaseModel):
    order_id: str
    product_name: str
    quantity: int
    customer_tier: Literal["platinum", "gold", "standard"]
    urgency_flag: bool
    stock_available: int
    expiry_date: date
    customer_location: str
    warehouse_location: str
    order_date: date


class OrderBatch(BaseModel):
    batch_id: str
    orders: List[Order]
