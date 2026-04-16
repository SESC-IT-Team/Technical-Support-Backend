from fastapi import Depends, APIRouter

from src.orders.order_schemas import CreateOrderRequest, SetDepartmentRequest, \
    OrderFilter, UpdateOrderStatusRequest, SetWorkerRequest
from src.orders.order_service import get_order_service, OrderService

router = APIRouter()

@router.post("/create_orders")
def create_order(data: CreateOrderRequest, service: OrderService = Depends(get_order_service)):
    return service.create_order(data)

@router.post("/department")
def change_department(data: SetDepartmentRequest, service: OrderService = Depends(get_order_service)):
    return service.set_department(data)

@router.post("/get_orders")
def get_orders(filters: OrderFilter, service: OrderService = Depends(get_order_service)):
    return service.get_orders(filters)

@router.post("/change_status")
def change_status(data: UpdateOrderStatusRequest, service: OrderService = Depends(get_order_service)):
    return service.update_order_status(data)

@router.post("/set_worker")
def set_worker(data: SetWorkerRequest, service: OrderService = Depends(get_order_service)):
    return service.set_worker(data)