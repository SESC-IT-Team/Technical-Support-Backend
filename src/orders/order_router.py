import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter

from src.database.session import get_db
from src.orders.order_schemas import CreateOrderRequest, OrderItem
from src.enums import Status


router = APIRouter()

@router.post("/create_orders")
def create_order(data: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    return OrderItem(
        order_id= uuid.uuid4(),
        department_id = data.department_id,
        from_user_id = uuid.uuid4(),
        worker_id= uuid.uuid4(),
        title = data.title,
        description = data.description,
        status = Status.NOT_STARTED,
        created_at = datetime(2026,3,13,17,17,17),
        finished_at = None
    )

@router.post("/department")
def create_department(data: OrderItem, db: AsyncSession = Depends(get_db)):
    return create_department(
        id = uuid.uuid4(),
        department_id = data.department_id
    )

@router.post("/get_orders")
def get_orders(data: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    return get_orders(
        id=uuid.uuid4(),
        department_id=data.department_id,
        from_user_id=uuid.uuid4(),
        worker=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status=Status.NOT_STARTED,
        created_at=datetime(2026, 3, 13, 17, 17, 17),
        finished_at=None
    )

@router.post("/change_status")
def change_status(data: OrderItem, db: AsyncSession = Depends(get_db)):
    return change_status(
        id=uuid.uuid4(),
        status=Status.NOT_STARTED
    )

@router.post("/set_worker")
def set_worker(data: OrderItem, db: AsyncSession = Depends(get_db)):
    return set_worker(
        id=uuid.uuid4(),
        worker=uuid.uuid4(),
        status=Status.NOT_STARTED
    )