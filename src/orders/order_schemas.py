import uuid
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.enums import Status, OrdersQuery


class OrderFilter(BaseModel):
    page: int = Field(default=1, ge=1)
    length: int = Field(default=10, ge=1)
    category: OrdersQuery = OrdersQuery.ALL
    department_id: Optional[uuid.UUID] = None
    status: Optional[Status] = None


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    from_user_id: uuid.UUID
    department_id: uuid.UUID
    worker_id: Optional[uuid.UUID] = None
    title: str
    description: str
    photos: List[str]
    status: Status
    created_at: datetime
    finished_at: Optional[datetime] = None


class OrderListResponse(BaseModel):
    items: List[OrderRead]
    page: int
    length: int
    total: int


class OrderStatusUpdate(BaseModel):
    status: Status


class OrderWorkerUpdate(BaseModel):
    worker_id: uuid.UUID


class OrderDepartmentUpdate(BaseModel):
    department_id: uuid.UUID
