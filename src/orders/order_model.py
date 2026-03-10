import uuid
from datetime import datetime
from src.enums import Status

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID

from src.database.base import Base

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False) # should take users from SDK
    department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    worker: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    photos: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.NOT_STARTED, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime] = mapped_column(DateTime, default=None, nullable=True)