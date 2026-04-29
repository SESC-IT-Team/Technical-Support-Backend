from fastapi import Depends, APIRouter
from sesc_auth_sdk.dependencies import LyceumAuth
from sesc_auth_sdk.schemas.user import JwtUserSchema

from src.orders.order_schemas import CreateOrderRequest, SetDepartmentRequest, \
    OrderFilter, SetStatusRequest, SetWorkerRequest
from src.orders.order_service import get_order_service, OrderService

router = APIRouter()

@router.post("/create_order")
async def create_order(data: CreateOrderRequest, service: OrderService = Depends(get_order_service),
                       user: JwtUserSchema = Depends(LyceumAuth)):
    return await service.create_order(data, user)

@router.post("/get_orders")
async def get_orders(filters: OrderFilter, service: OrderService = Depends(get_order_service),
                     user: JwtUserSchema = Depends(LyceumAuth)):
    return await service.get_orders(filters, user)

@router.post("/set_order_department")
async def set_department(data: SetDepartmentRequest, service: OrderService = Depends(get_order_service),
                         user: JwtUserSchema = Depends(LyceumAuth)):
    return await service.set_department(data)

@router.post("/set_order_status")
async def set_status(data: SetStatusRequest, service: OrderService = Depends(get_order_service),
                     user: JwtUserSchema = Depends(LyceumAuth)):
    return await service.set_status(data)

@router.post("/set_order_worker")
async def set_worker(data: SetWorkerRequest, service: OrderService = Depends(get_order_service),
                     user: JwtUserSchema = Depends(LyceumAuth)):
    return await service.set_worker(data)