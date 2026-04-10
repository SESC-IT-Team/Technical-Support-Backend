from enums import Status
from orders.order_schemas import UpdateOrderStatusRequest, SetWorkerRequest, SetDepartmentRequest
from src.orders.order_repository import OrderRepository
from src.orders.order_schemas import OrderFilter, GetOrdersResponse, CreateOrderRequest


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repo = repository

    async def create_order(self, data: CreateOrderRequest):
        order_data = data.model_dump()
        order_data['status'] = Status.NOT_STARTED
        return await self.repo.create_order(order_data)

    async def get_orders(self, filters: OrderFilter):
        orders = await self.repo.get_orders(
            user_id=filters.user_id,
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
def get_order_service():
    return OrderService(OrderRepository())