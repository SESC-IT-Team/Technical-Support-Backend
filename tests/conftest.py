import datetime
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sesc_auth_sdk.dependencies import LyceumAuth
from sesc_auth_sdk.enums.gender import Gender
from sesc_auth_sdk.enums.role import Role
from sesc_auth_sdk.enums.scope import Scope
from sesc_auth_sdk.schemas.token import AccessTokenPayload
from sesc_auth_sdk.schemas.user import User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# src.config читает .env и собирает настройки авторизации при импорте,
# поэтому недостающие переменные окружения задаём ДО импорта приложения.
os.environ.setdefault("AUTHENTIK_URL", "https://auth.test")
os.environ.setdefault("CLIENT_ID", "test-client")
os.environ.setdefault("CLIENT_SECRET", "test-secret")
os.environ.setdefault("APPLICATION_SLUG", "test-app")
os.environ.setdefault("LOGIN_REDIRECT_URI", "http://localhost:3000/callback")
os.environ.setdefault("ROUTER_PATH", "/auth")
os.environ.setdefault("ALLOWED_ISSUERS", '["https://auth.test"]')

from src.database.base import Base
from src.database.session import get_db
from src.main import app
from src.utils.S3Storage import S3Storage

# In-memory SQLite + StaticPool: одно соединение на все тесты.
# aiosqlite не привязан к event loop, поэтому работает и с TestClient,
# и с async-фикстурами одновременно.
engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# Ключ переопределения auth-зависимости: return_user из SDK ссылается на
# этот staticmethod-объект через Depends(), поэтому берём его из __dict__ класса.
VERIFY_AUTHORIZED = LyceumAuth.__dict__["verify_authorized"]


@pytest.fixture(autouse=True)
async def setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    app.dependency_overrides.clear()


@pytest.fixture()
async def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        await session.close()


@pytest.fixture()
def client():
    async def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            await db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_s3(monkeypatch):
    """Заглушка S3: тесты не должны ходить в реальный объектный стор."""

    async def fake_upload(self, order_id, file):
        return f"orders/{order_id}/{uuid.uuid4()}.jpg"

    async def fake_get_presigned_url(self, key, expires_in=3600):
        return f"https://s3.test/{key}?expires={expires_in}"

    async def fake_delete_order_photo(self, key):
        pass

    monkeypatch.setattr(S3Storage, "upload_order_photo", fake_upload)
    monkeypatch.setattr(S3Storage, "get_presigned_url", fake_get_presigned_url)
    monkeypatch.setattr(S3Storage, "delete_order_photo", fake_delete_order_photo)


def make_access_token_payload(user_id: uuid.UUID, scopes: list[Scope]) -> AccessTokenPayload:
    now = int(datetime.datetime.now().timestamp())
    return AccessTokenPayload(
        iss="https://auth.test",
        sub=user_id,
        iat=now,
        auth_time=now,
        exp=now + 3600,
        scope=scopes,
        acr="0",
        amr=["pwd"],
        jti=str(uuid.uuid4()),
        azp="test-client",
        uid=str(user_id),
    )


@pytest.fixture()
def make_user():
    """Фабрика пользователя (схема SDK) — без записи в БД."""

    def _make_user(**overrides) -> User:
        data = dict(
            id=uuid.uuid4(),
            last_name="Тестов",
            first_name="Тест",
            middle_name=None,
            full_name="Тестов Тест",
            gender=Gender.male,
            roles=[Role.student],
            birthday=datetime.date(2008, 1, 1),
            grade=11,
            letter="Е",
            class_name="11Е",
            graduation_year=2027,
            login="test_user",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )
        data.update(overrides)
        return User(**data)

    return _make_user


@pytest.fixture()
def auth_client(client, monkeypatch, make_user):
    """Возвращает TestClient, авторизованный под пользователем.

    Вызов: auth_client(user=None, scopes=None) -> TestClient.
    Верификация JWT заменяется заглушкой, проверка скоупов остаётся настоящей,
    а запрос /me к сервису пользователей подменяется на объект User.
    """

    def _auth(user: User | None = None, scopes: list[Scope] | None = None) -> TestClient:
        user = user or make_user()
        payload = make_access_token_payload(user.id, scopes or [])
        app.dependency_overrides[VERIFY_AUTHORIZED] = lambda: payload

        async def fake_get_current_user(cls, token: str) -> User:
            return user

        monkeypatch.setattr(LyceumAuth, "get_current_user", classmethod(fake_get_current_user))
        return client

    return _auth


@pytest.fixture()
def create_order_data():
    """Базовые form-поля заказа для POST /orders."""

    def _data(**overrides):
        data = {
            "department_id": str(uuid.uuid4()),
            "title": "вайфай не работает в общежитии",
            "description": "уже вторую неделю",
        }
        data.update(overrides)
        return data

    return _data


@pytest.fixture()
async def create_order_factory(db_session):
    """Фабрика заказа: создаёт Order прямо в тестовой БД."""

    async def _factory(**overrides):
        from src.enums import Status
        from src.orders.order_model import Order

        data = dict(
            id=uuid.uuid4(),
            from_user_id=uuid.uuid4(),
            department_id=uuid.uuid4(),
            worker_id=None,
            title="тестовый заказ",
            description="описание",
            photos=[],
            status=Status.NOT_STARTED,
            created_at=datetime.datetime.now(),
        )
        data.update(overrides)
        order = Order(**data)
        db_session.add(order)
        await db_session.commit()
        await db_session.refresh(order)
        return order

    return _factory
