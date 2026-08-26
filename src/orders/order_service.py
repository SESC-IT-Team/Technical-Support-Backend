import uuid
from fastapi import Depends, HTTPException, UploadFile
from sesc_auth_sdk.schemas.user import User
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.utils.S3Storage import S3Storage
from src.database.session import get_db
from src.enums import Status
from src.orders.order_schemas import OrderFilter, OrderListResponse
from src.orders.order_repository import OrderRepository


class OrderService:
    def __init__(self, repository: OrderRepository, storage: S3Storage):
        self.repo = repository
        self.storage = storage

    async def create_order(
        self,
        *,
        department_id: uuid.UUID,
        title: str,
        description: str,
        photos: list[UploadFile],
        user: User,
    ):
        for photo in photos:
            if not photo.content_type or not photo.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Only images are allowed")

        order_id = uuid.uuid4()
        photo_keys = [await self.storage.upload_order_photo(order_id, photo) for photo in photos]

        return await self.repo.create({
            "id": order_id,
            "from_user_id": user.id,
            "department_id": department_id,
            "title": title,
            "description": description,
            "photos": photo_keys,
        })

    async def get_order(self, order_id: uuid.UUID):
        return await self.repo.get_by_id(order_id)

    async def get_orders(self, filters: OrderFilter, user: User):
        orders = await self.repo.get_many(
            user_id=user.id,
            filters=filters,
        )
        total = await self.repo.count(filters, user.id)
        return OrderListResponse(
            items=orders,
            page=filters.page,
            length=filters.length,
            total=total,
        )

    async def update_status(self, order_id: uuid.UUID, status: Status):
        return await self.repo.update_status(order_id, status)

    async def update_worker(self, order_id: uuid.UUID, worker_id: uuid.UUID):
        return await self.repo.update_worker(order_id, worker_id)

    async def update_department(self, order_id: uuid.UUID, department_id: uuid.UUID):
        return await self.repo.update_department(order_id, department_id)

    async def get_photo_presigned_url(self, photo_key: str) -> str:
        return await self.storage.get_presigned_url(photo_key)

    async def get_order_photo_url(self, order_id: uuid.UUID, photo_key: str) -> str:
        order = await self.repo.get_by_id(order_id)
        if photo_key not in order.photos:
            raise HTTPException(status_code=404, detail="Photo not found in this order")
        return await self.storage.get_presigned_url(photo_key)

    async def delete_order_photo(self, order_id: uuid.UUID, photo_key: str) -> None:
        order = await self.repo.get_by_id(order_id)
        if photo_key not in order.photos:
            raise HTTPException(status_code=404, detail="Photo not found in this order")

        await self.storage.delete_order_photo(photo_key)

        # Remove photo key from order
        updated_photos = [p for p in order.photos if p != photo_key]
        await self.repo.update_photos(order_id, updated_photos)


async def get_order_service(session: AsyncSession = Depends(get_db)):
    storage = S3Storage(
        endpoint_url=settings.s3_endpoint_url,
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        bucket_name=settings.s3_bucket_name,
        region_name=settings.s3_region_name,
    )
    return OrderService(OrderRepository(session), storage)