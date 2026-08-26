import datetime
import uuid

import pytest
from sesc_auth_sdk.enums.scope import Scope
from sqlalchemy import func, select

from src.enums import Status
from src.orders.order_model import Order

pytestmark = pytest.mark.integration

CREATE_SCOPE = Scope.technical_support_orders_create
GET_SCOPE = Scope.technical_support_orders_get
SET_STATUS_SCOPE = Scope.technical_support_orders_set_status
SET_WORKER_SCOPE = Scope.technical_support_orders_set_worker
SET_DEPARTMENT_SCOPE = Scope.technical_support_orders_set_department


class TestCreateOrder:
    async def test_create_order_success(self, client, auth_client, make_user, db_session, create_order_data):
        user = make_user()
        client = auth_client(user=user, scopes=[CREATE_SCOPE])
        data = create_order_data()

        response = client.post(
            "/orders",
            data=data,
            files=[("photos", ("wifi.jpg", b"fake-image-bytes", "image/jpeg"))],
        )

        assert response.status_code == 201, response.text
        body = response.json()

        assert body["department_id"] == data["department_id"]
        assert body["title"] == data["title"]
        assert body["description"] == data["description"]
        assert body["status"] == Status.NOT_STARTED.value
        assert body["from_user_id"] == str(user.id)
        assert body["finished_at"] is None
        assert len(body["photos"]) == 1
        assert body["photos"][0].startswith(f"orders/{body['id']}/")

        orders_count = await db_session.scalar(select(func.count()).select_from(Order))
        assert orders_count == 1

    async def test_create_order_with_multiple_photos(self, client, auth_client, create_order_data):
        client = auth_client(scopes=[CREATE_SCOPE])

        response = client.post(
            "/orders",
            data=create_order_data(),
            files=[
                ("photos", ("wifi.jpg", b"fake-image-bytes", "image/jpeg")),
                ("photos", ("router.jpg", b"fake-image-bytes", "image/jpeg")),
            ],
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert len(body["photos"]) == 2
        assert len(set(body["photos"])) == 2

    async def test_create_order_accepts_no_photo(self, client, auth_client, create_order_data):
        client = auth_client(scopes=[CREATE_SCOPE])

        response = client.post("/orders", data=create_order_data())

        assert response.status_code == 201
        body = response.json()
        assert body["photos"] == []

    async def test_create_order_requires_scope(self, client, auth_client, create_order_data):
        client = auth_client(scopes=[])

        response = client.post(
            "/orders",
            data=create_order_data(),
            files=[("photos", ("wifi.jpg", b"fake-image-bytes", "image/jpeg"))],
        )

        assert response.status_code == 403

    async def test_create_order_unauthorized(self, client, create_order_data):
        response = client.post(
            "/orders",
            data=create_order_data(),
            files=[("photos", ("wifi.jpg", b"fake-image-bytes", "image/jpeg"))],
        )

        assert response.status_code == 401

    async def test_create_order_rejects_non_image(self, client, auth_client, create_order_data):
        client = auth_client(scopes=[CREATE_SCOPE])

        response = client.post(
            "/orders",
            data=create_order_data(),
            files=[("photos", ("doc.txt", b"hello", "text/plain"))],
        )

        assert response.status_code == 400

    async def test_create_order_validation_error(self, client, auth_client, create_order_data):
        client = auth_client(scopes=[CREATE_SCOPE])
        data = create_order_data()
        del data["title"]

        response = client.post(
            "/orders",
            data=data,
            files=[("photos", ("wifi.jpg", b"fake-image-bytes", "image/jpeg"))],
        )

        assert response.status_code == 422


class TestGetOrders:
    async def test_get_orders_returns_all(self, client, auth_client, make_user, create_order_factory):
        user = make_user()
        await create_order_factory(from_user_id=user.id)
        other = await create_order_factory()
        client = auth_client(user=user, scopes=[GET_SCOPE])

        response = client.get("/orders")

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["page"] == 1
        assert body["length"] == 10
        assert "total" in body
        assert body["total"] == 2
        assert len(body["items"]) == 2
        assert {item["from_user_id"] for item in body["items"]} == {str(user.id), str(other.from_user_id)}

    async def test_get_orders_my(self, client, auth_client, make_user, create_order_factory):
        user = make_user()
        my_order = await create_order_factory(from_user_id=user.id)
        await create_order_factory()
        client = auth_client(user=user, scopes=[GET_SCOPE])

        response = client.get("/orders", params={"category": "my"})

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert [item["id"] for item in body["items"]] == [str(my_order.id)]

    async def test_get_orders_todo(self, client, auth_client, make_user, create_order_factory):
        user = make_user()
        assigned = await create_order_factory(worker_id=user.id)
        await create_order_factory()
        client = auth_client(user=user, scopes=[GET_SCOPE])

        response = client.get("/orders", params={"category": "todo"})

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert [item["id"] for item in body["items"]] == [str(assigned.id)]

    async def test_get_orders_filter_by_department(self, client, auth_client, make_user, create_order_factory):
        user = make_user()
        department_id = uuid.uuid4()
        matching = await create_order_factory(from_user_id=user.id, department_id=department_id)
        await create_order_factory(from_user_id=user.id)
        client = auth_client(user=user, scopes=[GET_SCOPE])

        response = client.get("/orders", params={"department_id": str(department_id)})

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert [item["id"] for item in body["items"]] == [str(matching.id)]

    async def test_get_orders_filter_by_status(self, client, auth_client, make_user, create_order_factory):
        user = make_user()
        in_progress = await create_order_factory(from_user_id=user.id, status=Status.IN_PROGRESS)
        await create_order_factory(from_user_id=user.id)
        client = auth_client(user=user, scopes=[GET_SCOPE])

        response = client.get("/orders", params={"status": Status.IN_PROGRESS.value})

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert [item["id"] for item in body["items"]] == [str(in_progress.id)]

    async def test_get_orders_pagination(self, client, auth_client, make_user, create_order_factory):
        user = make_user()
        orders = [await create_order_factory(from_user_id=user.id) for _ in range(3)]
        client = auth_client(user=user, scopes=[GET_SCOPE])

        response = client.get("/orders", params={"page": 2, "length": 2})

        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 2
        assert body["length"] == 2
        assert body["total"] == 3
        assert len(body["items"]) == 1
        assert body["items"][0]["id"] in {str(o.id) for o in orders}

    async def test_get_orders_unauthorized(self, client):
        response = client.get("/orders")
        assert response.status_code == 401


class TestGetOrder:
    async def test_get_order_success(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        client = auth_client(scopes=[GET_SCOPE])

        response = client.get(f"/orders/{order.id}")

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == str(order.id)
        assert body["title"] == order.title
        assert body["status"] == Status.NOT_STARTED.value

    async def test_get_order_not_found(self, client, auth_client):
        client = auth_client(scopes=[GET_SCOPE])

        response = client.get(f"/orders/{uuid.uuid4()}")

        assert response.status_code == 404

    async def test_get_order_requires_scope(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        client = auth_client(scopes=[])

        response = client.get(f"/orders/{order.id}")

        assert response.status_code == 403

    async def test_get_order_unauthorized(self, client, create_order_factory):
        order = await create_order_factory()

        response = client.get(f"/orders/{order.id}")

        assert response.status_code == 401


class TestOrderPhotos:
    async def test_get_photo_presigned_url(self, client, auth_client, create_order_factory):
        order = await create_order_factory(photos=["orders/test/photo1.jpg"])
        client = auth_client(scopes=[GET_SCOPE])

        # URL-encode the photo key for the path
        photo_key = "orders%2Ftest%2Fphoto1.jpg"
        response = client.get(f"/orders/{order.id}/photos/{photo_key}/url")

        assert response.status_code == 200, response.text
        body = response.json()
        assert "url" in body
        assert body["url"].startswith("https://s3.test/orders/test/photo1.jpg")

    async def test_get_photo_presigned_url_not_found(self, client, auth_client, create_order_factory):
        order = await create_order_factory(photos=[])
        client = auth_client(scopes=[GET_SCOPE])

        response = client.get(f"/orders/{order.id}/photos/orders%2Ftest%2Fmissing.jpg/url")

        assert response.status_code == 404

    async def test_delete_photo(self, client, auth_client, create_order_factory):
        order = await create_order_factory(photos=["orders/test/photo1.jpg", "orders/test/photo2.jpg"])
        # Client needs both scopes: SET_STATUS for DELETE, GET for verification
        test_client = auth_client(scopes=[SET_STATUS_SCOPE, GET_SCOPE])

        photo_key = "orders%2Ftest%2Fphoto1.jpg"
        response = test_client.delete(f"/orders/{order.id}/photos/{photo_key}")

        assert response.status_code == 204
        
        # Verify photo removed
        response = test_client.get(f"/orders/{order.id}")
        assert response.status_code == 200
        body = response.json()
        assert "orders/test/photo1.jpg" not in body["photos"]
        assert "orders/test/photo2.jpg" in body["photos"]

    async def test_delete_photo_not_found(self, client, auth_client, create_order_factory):
        order = await create_order_factory(photos=[])
        client = auth_client(scopes=[SET_STATUS_SCOPE])

        response = client.delete(f"/orders/{order.id}/photos/orders%2Ftest%2Fmissing.jpg")

        assert response.status_code == 404

    async def test_delete_photo_requires_scope(self, client, auth_client, create_order_factory):
        order = await create_order_factory(photos=["orders/test/photo1.jpg"])
        client = auth_client(scopes=[])

        photo_key = "orders%2Ftest%2Fphoto1.jpg"
        response = client.delete(f"/orders/{order.id}/photos/{photo_key}")

        assert response.status_code == 403


class TestUpdateOrderStatus:
    async def test_update_order_status(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        client = auth_client(scopes=[SET_STATUS_SCOPE])

        response = client.put(
            f"/orders/{order.id}/status",
            json={"status": Status.IN_PROGRESS.value},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == str(order.id)
        assert body["status"] == Status.IN_PROGRESS.value
        assert body["finished_at"] is None

    async def test_update_order_status_done_sets_finished_at(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        client = auth_client(scopes=[SET_STATUS_SCOPE])

        response = client.put(
            f"/orders/{order.id}/status",
            json={"status": Status.DONE.value},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["status"] == Status.DONE.value
        assert body["finished_at"] is not None

    async def test_update_order_status_not_found(self, client, auth_client):
        client = auth_client(scopes=[SET_STATUS_SCOPE])

        response = client.put(
            f"/orders/{uuid.uuid4()}/status",
            json={"status": Status.DONE.value},
        )

        assert response.status_code == 404

    async def test_update_order_status_requires_scope(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        client = auth_client(scopes=[])

        response = client.put(
            f"/orders/{order.id}/status",
            json={"status": Status.DONE.value},
        )

        assert response.status_code == 403

    async def test_update_order_status_unauthorized(self, client, create_order_factory):
        order = await create_order_factory()

        response = client.put(
            f"/orders/{order.id}/status",
            json={"status": Status.DONE.value},
        )

        assert response.status_code == 401


class TestUpdateOrderWorker:
    async def test_update_order_worker(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        worker_id = uuid.uuid4()
        client = auth_client(scopes=[SET_WORKER_SCOPE])

        response = client.put(
            f"/orders/{order.id}/worker",
            json={"worker_id": str(worker_id)},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == str(order.id)
        assert body["worker_id"] == str(worker_id)

    async def test_update_order_worker_not_found(self, client, auth_client):
        client = auth_client(scopes=[SET_WORKER_SCOPE])

        response = client.put(
            f"/orders/{uuid.uuid4()}/worker",
            json={"worker_id": str(uuid.uuid4())},
        )

        assert response.status_code == 404


class TestUpdateOrderDepartment:
    async def test_update_order_department(self, client, auth_client, create_order_factory):
        order = await create_order_factory()
        new_department_id = uuid.uuid4()
        client = auth_client(scopes=[SET_DEPARTMENT_SCOPE])

        response = client.put(
            f"/orders/{order.id}/department",
            json={"department_id": str(new_department_id)},
        )

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["id"] == str(order.id)
        assert body["department_id"] == str(new_department_id)

    async def test_update_order_department_not_found(self, client, auth_client):
        client = auth_client(scopes=[SET_DEPARTMENT_SCOPE])

        response = client.put(
            f"/orders/{uuid.uuid4()}/department",
            json={"department_id": str(uuid.uuid4())},
        )

        assert response.status_code == 404