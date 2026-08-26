import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sesc_auth_sdk.enums.scope import Scope
from sesc_auth_sdk.schemas.user import User

from src.orders.order_schemas import (
    OrderDepartmentUpdate,
    OrderFilter,
    OrderListResponse,
    OrderRead,
    OrderStatusUpdate,
    OrderWorkerUpdate,
)
from src.orders.order_service import get_order_service, OrderService
from src.utils.auth.dependencies import Auth

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", status_code=201, summary="Создать новый заказ")
async def create_order(
    department_id: uuid.UUID = Form(..., description="ID департамента"),
    title: str = Form(..., description="Заголовок заказа"),
    description: str = Form(..., description="Описание проблемы"),
    photos: list[UploadFile] = File(default=[], description="Фотографии"),
    service: OrderService = Depends(get_order_service),
    user: User = Depends(Auth([Scope.technical_support_orders_create]).return_user),
) -> OrderRead:
    """
    Создаёт новый заказ в техподдержке.
    
    - **department_id**: ID департамента, в который попадает заказ
    - **title**: Краткий заголовок (до 255 символов)
    - **description**: Подробное описание (до 511 символов)
    - **photos**: Список файлов-изображений (опционально)
    
    Автор заказа (from_user_id) определяется автоматически из токена авторизации.
    Статус устанавливается в "not started".
    """
    return await service.create_order(
        department_id=department_id,
        title=title,
        description=description,
        photos=photos,
        user=user,
    )


@router.get("", summary="Получить список заказов")
async def get_orders(
    filters: OrderFilter = Depends(),
    service: OrderService = Depends(get_order_service),
    user: User = Depends(Auth([Scope.technical_support_orders_get]).return_user),
) -> OrderListResponse:
    """
    Возвращает пагинированный список заказов с фильтрацией.
    
    **Фильтры:**
    - **category**: `all` (все), `my` (мои созданные), `todo` (назначенные мне)
    - **department_id**: Фильтр по департаменту (только для category=all)
    - **status**: Фильтр по статусу (not started / in progress / done)
    - **page**: Номер страницы (начиная с 1)
    - **length**: Размер страницы
    
    В ответе возвращается `total` — общее количество заказов для пагинации.
    """
    return await service.get_orders(filters, user)


@router.get("/{order_id}", summary="Получить заказ по ID")
async def get_order(
    order_id: uuid.UUID,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(Auth([Scope.technical_support_orders_get])),
) -> OrderRead:
    """
    Возвращает полную информацию о заказе включая фото (ключи S3).
    """
    return await service.get_order(order_id)


@router.get("/{order_id}/photos/{photo_key:path}/url", summary="Получить presigned URL для скачивания фото")
async def get_photo_url(
    order_id: uuid.UUID,
    photo_key: str,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(Auth([Scope.technical_support_orders_get])),
) -> dict[str, str]:
    """
    Генерирует временную ссылку (presigned URL) для скачивания фото из S3.

    Ссылка действительна 1 час (3600 секунд).
    """
    url = await service.get_order_photo_url(order_id, photo_key)
    return {"url": url}


@router.delete("/{order_id}/photos/{photo_key:path}", summary="Удалить фото из заказа", status_code=204)
async def delete_photo(
    order_id: uuid.UUID,
    photo_key: str,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(Auth([Scope.technical_support_orders_set_status])),  # reuse existing scope
) -> None:
    """
    Удаляет фото из заказа и из S3-хранилища.

    Требует права на изменение заказа (scope set_status).
    """
    await service.delete_order_photo(order_id, photo_key)


@router.put("/{order_id}/status", summary="Обновить статус заказа")
async def update_status(
    order_id: uuid.UUID,
    data: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(Auth([Scope.technical_support_orders_set_status])),
) -> OrderRead:
    """
    Обновляет статус заказа.
    
    При установке статуса "done" автоматически проставляется finished_at.
    """
    return await service.update_status(order_id, data.status)


@router.put("/{order_id}/worker", summary="Назначить исполнителя заказу")
async def update_worker(
    order_id: uuid.UUID,
    data: OrderWorkerUpdate,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(Auth([Scope.technical_support_orders_set_worker])),
) -> OrderRead:
    """
    Назначает исполнителя (worker) заказу.
    
    worker_id — UUID пользователя из экосистемы.
    """
    return await service.update_worker(order_id, data.worker_id)


@router.put("/{order_id}/department", summary="Сменить департамент заказа")
async def update_department(
    order_id: uuid.UUID,
    data: OrderDepartmentUpdate,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(Auth([Scope.technical_support_orders_set_department])),
) -> OrderRead:
    """
    Переводит заказ в другой департамент.
    """
    return await service.update_department(order_id, data.department_id)
