from fastapi import Depends, APIRouter
from sesc_auth_sdk.dependencies import LyceumAuth
from sesc_auth_sdk.enums.permission import Permissions
from sesc_auth_sdk.schemas.user import JwtUserSchema

from src.orders.order_schemas import CreateOrderRequest, SetDepartmentRequest, \
    OrderFilter, SetStatusRequest, SetWorkerRequest, OrderItem, GetOrdersResponse
from src.orders.order_service import get_order_service, OrderService

router = APIRouter()

@router.post("/create_order")
async def create_order(data: CreateOrderRequest = Depends(), service: OrderService = Depends(get_order_service),
                       user: JwtUserSchema = Depends(LyceumAuth(required_permissions=[Permissions.TechnicalSupport.Orders.create]))) -> OrderItem:
    return await service.create_order(data, user)

@router.post("/get_orders")
async def get_orders(filters: OrderFilter = Depends(), service: OrderService = Depends(get_order_service),
                     user: JwtUserSchema = Depends(LyceumAuth(required_permissions=[Permissions.TechnicalSupport.Orders.get]))) -> GetOrdersResponse:
    return await service.get_orders(filters, user)

@router.post("/set_order_department")
async def set_department(data: SetDepartmentRequest = Depends(), service: OrderService = Depends(get_order_service),
                         user: JwtUserSchema = Depends(LyceumAuth(required_permissions=[Permissions.TechnicalSupport.Orders.set_department]))) -> OrderItem:
    return await service.set_department(data)

@router.post("/set_order_status")
async def set_status(data: SetStatusRequest = Depends(), service: OrderService = Depends(get_order_service),
                     user: JwtUserSchema = Depends(LyceumAuth(required_permissions=[Permissions.TechnicalSupport.Orders.set_status]))) -> OrderItem:
    return await service.set_status(data)

@router.post("/set_order_worker")
async def set_worker(data: SetWorkerRequest = Depends(), service: OrderService = Depends(get_order_service),
                     user: JwtUserSchema = Depends(LyceumAuth(required_permissions=[Permissions.TechnicalSupport.Orders.set_worker]))) -> OrderItem:
    return await service.set_worker(data)