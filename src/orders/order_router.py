import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter

from src.database.session import get_db
from src.orders.order_schemas import CreateOrderRequest, OrderItem, GetOrdersResponse
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
def change_department(data: OrderItem, db: AsyncSession = Depends(get_db)):
    return OrderItem(
        order_id=uuid.uuid4(),
        department_id=data.department_id,
        from_user_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status=Status.NOT_STARTED,
        created_at=datetime(2026, 3, 13, 17, 17, 17),
        finished_at=None
    )

@router.post("/get_orders")
def get_orders(data: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    order = OrderItem(
        order_id=uuid.uuid4(),
        department_id=data.department_id,
        from_user_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status=Status.NOT_STARTED,
        created_at=datetime(2026, 3, 13, 17, 17, 17),
        finished_at=None
    )
    return GetOrdersResponse(
        items = [order],
        page = 1,
        length = 1

    )

@router.post("/change_status")
def change_status(data: OrderItem, db: AsyncSession = Depends(get_db)):
    return OrderItem(
        order_id=uuid.uuid4(),
        department_id=data.department_id,
        from_user_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status=Status.NOT_STARTED,
        created_at=datetime(2026, 3, 13, 17, 17, 17),
        finished_at=None
    )

@router.post("/set_worker")
def set_worker(data: OrderItem, db: AsyncSession = Depends(get_db)):
    return OrderItem(
        order_id=uuid.uuid4(),
        department_id=data.department_id,
        from_user_id=uuid.uuid4(),
        worker_id=uuid.uuid4(),
        title=data.title,
        description=data.description,
        status=Status.NOT_STARTED,
        created_at=datetime(2026, 3, 13, 17, 17, 17),
        finished_at=None
    )