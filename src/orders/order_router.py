from fastapi import Depends, APIRouter

from src.orders.order_schemas import CreateOrderRequest, SetDepartmentRequest, \
    OrderFilter, UpdateOrderStatusRequest, SetWorkerRequest
from src.orders.order_service import get_order_service, OrderService
from utils.custom_auth.custom_auth import TechSupportUser, TechSupportAuth

router = APIRouter()

@router.post("/create_order")
async def create_order(data: CreateOrderRequest, service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth)):
    return await service.create_order(data, user)

@router.post("/change_order_department")
async def change_department(data: SetDepartmentRequest, service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth)):
    return await service.set_department(data)

@router.post("/get_orders")
async def get_orders(filters: OrderFilter, service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth)):
    return await service.get_orders(filters, user)

@router.post("/change_order_status")
async def change_status(data: UpdateOrderStatusRequest, service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth)):
    return await service.update_order_status(data)

@router.post("/set_order_worker")
async def set_worker(data: SetWorkerRequest, service: OrderService = Depends(get_order_service), user: TechSupportUser = Depends(TechSupportAuth)):
    return await service.set_worker(data)