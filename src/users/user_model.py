import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID

from src.database.base import Base
from src.enums import Role

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subrole: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER, nullable=False)
    head_of_department_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"), default=None, nullable=True)