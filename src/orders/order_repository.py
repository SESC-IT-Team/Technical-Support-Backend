import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.enums import OrdersQuery, Status, SortOrder
from src.orders.order_model import Order


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, data: dict):
        order = Order(**data)
        self.session.add(order)
        await self.session.commit()
        return order

    async def get_orders(self, user_id: uuid.UUID, page: int, length: int, category: OrdersQuery,
                         department_id: Optional[uuid.UUID], status: Optional[Status], created_at_sort: Optional[SortOrder]):
        stmt = select(Order)

        match category:
            case OrdersQuery.ALL:
                if department_id:
                    stmt = stmt.where(Order.department_id == department_id)
            case OrdersQuery.TODO:
                stmt = stmt.where(Order.worker_id == user_id)
            case OrdersQuery.MY:
                stmt = stmt.where(Order.from_user_id == user_id)

        if status:
            stmt = stmt.where(Order.status == status)

        if created_at_sort:
            sorting = desc(Order.created_at) if created_at_sort == SortOrder.DESC else asc(Order.created_at)
            stmt = stmt.order_by(sorting)

        stmt = stmt.offset((page - 1) * length).limit(length)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_order_status(self, order_id: uuid.UUID, new_status: Status):
        stmt = update(Order).where(Order.id == order_id).values(status=new_status)
        if new_status == Status.DONE:
            stmt = stmt.values(finished_at=datetime.now())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def set_worker(self, order_id: uuid.UUID, worker_id: uuid.UUID):
        stmt = update(Order).where(Order.id == order_id).values(worker_id=worker_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def set_department(self, order_id: uuid.UUID, department_id: uuid.UUID):
        stmt = update(Order).where(Order.id == order_id).values(department_id=department_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()