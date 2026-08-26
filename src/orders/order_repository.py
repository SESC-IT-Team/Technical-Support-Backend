import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException
from sqlalchemy import select, update, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.orders.order_schemas import OrderFilter
from src.enums import OrdersQuery, Status
from src.orders.order_model import Order


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict):
        order = Order(**data)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_by_id(self, order_id: uuid.UUID):
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def get_many(self, user_id: uuid.UUID, filters: OrderFilter):
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

        stmt = stmt.order_by(desc(Order.created_at))

        stmt = stmt.limit(filters.length).offset((filters.page - 1) * filters.length)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, filters: OrderFilter, user_id: uuid.UUID) -> int:
        stmt = select(func.count()).select_from(Order)

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

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_status(self, order_id: uuid.UUID, status: Status):
        stmt = update(Order).where(Order.id == order_id).values(status=status)
        if status == Status.DONE:
            stmt = stmt.values(finished_at=datetime.now())
        stmt = stmt.returning(Order)
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        await self.session.commit()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def update_worker(self, order_id: uuid.UUID, worker_id: uuid.UUID):
        stmt = update(Order).where(Order.id == order_id).values(worker_id=worker_id)
        stmt = stmt.returning(Order)
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        await self.session.commit()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def update_department(self, order_id: uuid.UUID, department_id: uuid.UUID):
        stmt = update(Order).where(Order.id == order_id).values(department_id=department_id)
        stmt = stmt.returning(Order)
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        await self.session.commit()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    async def update_photos(self, order_id: uuid.UUID, photos: List[str]):
        stmt = update(Order).where(Order.id == order_id).values(photos=photos)
        stmt = stmt.returning(Order)
        result = await self.session.execute(stmt)
        order = result.scalar_one_or_none()
        await self.session.commit()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
