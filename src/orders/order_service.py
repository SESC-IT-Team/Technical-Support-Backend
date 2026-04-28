from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.enums import Status
from src.orders.order_schemas import UpdateOrderStatusRequest, SetWorkerRequest, SetDepartmentRequest
from src.orders.order_repository import OrderRepository
from src.orders.order_schemas import OrderFilter, GetOrdersResponse, CreateOrderRequest
from utils.custom_auth.custom_auth import TechSupportUser


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repo = repository

    async def create_order(self, data: CreateOrderRequest, user: TechSupportUser):
        order_data = data.model_dump()
        order_data['status'] = Status.NOT_STARTED
        order_data['from_user_id'] = user.id
        return await self.repo.create_order(order_data)

    async def get_orders(self, filters: OrderFilter, user: TechSupportUser):
        orders = await self.repo.get_orders(
            user_id=user.id,
            page=filters.page,
            length=filters.length,
            category=filters.category,
            department_id=filters.department_id,
            status=filters.status,
            created_at_sort=filters.created_at_sort
        )
        return GetOrdersResponse(
            items=orders,
            page=filters.page,
            length=filters.length
        )

    async def update_order_status(self, data: UpdateOrderStatusRequest):
        return await self.repo.update_order_status(
            order_id=data.order_id,
            new_status=data.status
        )

    async def set_worker(self, data: SetWorkerRequest):
        return await self.repo.set_worker(
            order_id=data.order_id,
            worker_id=data.worker_id
        )

    async def set_department(self, data: SetDepartmentRequest):
        return await self.repo.set_department(
            order_id=data.order_id,
            department_id=data.department_id
        )

async def get_order_service(session: AsyncSession = Depends(get_db)):
    return OrderService(OrderRepository(session))