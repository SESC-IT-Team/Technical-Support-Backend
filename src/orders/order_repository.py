import uuid
from datetime import datetime

from sqlalchemy import select, update, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from src.orders.order_schemas import OrderFilter, SetStatusRequest, SetWorkerRequest, SetDepartmentRequest
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

    async def get_orders(self, user_id: uuid.UUID, filters: OrderFilter):
        stmt = select(Order)

        match filters.category:
            case OrdersQuery.ALL:
                if filters.department_id:
                    stmt = stmt.where(Order.department_id == filters.department_id)
            case OrdersQuery.TODO:
                stmt = stmt.where(Order.worker_id == user_id)
            case OrdersQuery.MY:
                stmt = stmt.where(Order.from_user_id == user_id)

        if filters.status:
            stmt = stmt.where(Order.status == filters.status)

        if filters.created_at_sort:
            sorting = desc(Order.created_at) if filters.created_at_sort == SortOrder.DESC else asc(Order.created_at)
            stmt = stmt.order_by(sorting)

        stmt = stmt.offset((filters.page - 1) * filters.length).limit(filters.length)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def set_status(self, update_data: SetStatusRequest):
        stmt = update(Order).where(Order.id == update_data.order_id).values(status=update_data.new_status)
        if update_data.new_status == Status.DONE:
            stmt = stmt.values(finished_at=datetime.now())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def set_worker(self, update_data: SetWorkerRequest):
        stmt = update(Order).where(Order.id == update_data.order_id).values(worker_id=update_data.worker_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def set_department(self, update_data: SetDepartmentRequest):
        stmt = update(Order).where(Order.id == update_data.order_id).values(department_id=update_data.department_id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.scalar_one_or_none()