from fastapi import Depends
from sesc_auth_sdk.schemas.user import JwtUserSchema
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.orders.order_schemas import SetStatusRequest, SetWorkerRequest, SetDepartmentRequest
from src.orders.order_repository import OrderRepository
from src.orders.order_schemas import OrderFilter, GetOrdersResponse, CreateOrderRequest


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repo = repository

    async def create_order(self, data: CreateOrderRequest, user: JwtUserSchema):
        order_data = data.model_dump()
        order_data['from_user_id'] = user.id
        return await self.repo.create_order(order_data)

    async def get_orders(self, filters: OrderFilter, user: JwtUserSchema):
        orders = await self.repo.get_orders(
            user_id=user.id,
            filters=filters
        )
        return GetOrdersResponse(
            items=orders,
            page=filters.page,
            length=filters.length
        )

    async def set_status(self, data: SetStatusRequest):
        return await self.repo.set_status(
            update_data=data
        )

    async def set_worker(self, data: SetWorkerRequest):
        return await self.repo.set_worker(
            update_data=data
        )

    async def set_department(self, data: SetDepartmentRequest):
        return await self.repo.set_department(
            update_data=data
        )

async def get_order_service(session: AsyncSession = Depends(get_db)):
    return OrderService(OrderRepository(session))