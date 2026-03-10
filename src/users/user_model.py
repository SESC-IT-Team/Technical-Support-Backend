import uuid
from src.enums import Role

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum
from sqlalchemy.dialects.postgresql import UUID

from src.database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.USER, nullable=False)