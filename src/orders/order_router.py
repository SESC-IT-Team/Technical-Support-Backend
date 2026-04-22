import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, APIRouter

from src.database.session import get_db
from src.orders.order_schemas import CreateOrderRequest, OrderItem, GetOrdersResponse, SetDepartmentRequest, \
    OrderFilter, UpdateOrderStatusRequest, SetWorkerRequest
from src.enums import Status
from src.orders.order_service import get_order_service, OrderService
from utils.custom_auth.custom_auth import TechSupportAuth, TechSupportUser
from sesc_auth_sdk.enums.role import Role
router = APIRouter()

@router.post("/create_orders")
def create_order(data: CreateOrderRequest, db: AsyncSession = Depends(get_db), service: OrderService = Depends(get_order_service),user: TechSupportUser = Depends(TechSupportAuth(allowed_roles=[Role.teacher, Role.staff, Role.admin]))):
    return service.create_order(data)

@router.post("/department")
def change_department(data: SetDepartmentRequest, db: AsyncSession = Depends(get_db),service: OrderService = Depends(get_order_service),user: TechSupportUser = Depends(TechSupportAuth(allowed_roles=[Role.admin, Role.staff]))):
    return service.set_department(data)

@router.post("/get_orders")
def get_orders(filters: OrderFilter, db: AsyncSession = Depends(get_db),service: OrderService = Depends(get_order_service),user: TechSupportUser = Depends(TechSupportAuth())):
    return service.get_orders(filters)



@router.post("/change_status")
def change_status(data: UpdateOrderStatusRequest, db: AsyncSession = Depends(get_db),service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth())):
    return service.update_order_status(data)

@router.post("/set_worker")
def set_worker(data: SetWorkerRequest, db: AsyncSession = Depends(get_db),service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth([Role.staff]))):
    return service.set_worker(data)

