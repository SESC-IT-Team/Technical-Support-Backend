import uuid

from pydantic import BaseModel
from datetime import datetime


class CreateOrderRequest(BaseModel):
    department_id: uuid.UUID
    title: str
    description: str


class CreateOrderResponse(BaseModel):
    id: uuid.UUID
    department_id: uuid.UUID
    from_user_id: uuid.UUID
    worker: uuid.UUID
    title: str
    description: str
    #photos
    status: str
    created_at: datetime
    finished_at: datetime