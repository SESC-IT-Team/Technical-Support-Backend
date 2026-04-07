import uuid
from typing import Optional, List

from pydantic import BaseModel, Field
from datetime import datetime

from enums import Status, SortOrder, OrdersQuery


class OrderFilter(BaseModel):
    user_id: uuid.UUID
    page: int = Field(default=1, ge=1)
    length: int = Field(default=10, ge=1)
    category: OrdersQuery = OrdersQuery.ALL
    department_id: Optional[uuid.UUID] = None
    status: Optional[Status] = None
    created_at_sort: Optional[SortOrder] = None

class OrderItem(BaseModel):
    order_id: uuid.UUID
    department_id: uuid.UUID
    from_user_id: uuid.UUID
    worker_id: uuid.UUID
    title: str
    description: str
    #photos
    status: Status
    created_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GetOrdersResponse(BaseModel):
    items: List[OrderItem]
    page: int
    length: int

class CreateOrderRequest(BaseModel):
    department_id: uuid.UUID
    title: str
    description: str

class UpdateOrderStatusRequest(BaseModel):
    order_id: uuid.UUID
    status: Status

class SetWorkerRequest(BaseModel):
    order_id: uuid.UUID
    worker_id: uuid.UUID

class SetDepartmentRequest(BaseModel):
    order_id: uuid.UUID
    department_id: uuid.UUID