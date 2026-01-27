import enum
from sqlalchemy import String, Boolean, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.core.db import Base


class UserRole(str, enum.Enum):
	user = "user"
	hr = "hr"
	admin = "admin"


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True)
	email: Mapped[str] = mapped_column(
		String(255),
		unique=True,
		index=True,
		nullable=False
	)
	
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	
	role: Mapped[UserRole] = mapped_column(
		Enum(UserRole, name="user_role"),
		nullable=False,
		default=UserRole.user
	)
	
	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		nullable=False,
	)