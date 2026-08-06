from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
	from app.users.models import User


class Employee(Base):
	__tablename__ = "employees"

	id: Mapped[int] = mapped_column(primary_key=True)

	# 1:1 to users, nullable — сотрудник может не иметь логина в системе
	user_id: Mapped[int | None] = mapped_column(
		ForeignKey("users.id", ondelete="SET NULL"),
		unique=True,
		nullable=True,
	)

	full_name: Mapped[str] = mapped_column(String(255), nullable=False)
	email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
	phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
	telegram: Mapped[str | None] = mapped_column(String(100), nullable=True)
	department: Mapped[str | None] = mapped_column(String(100), nullable=True)
	position: Mapped[str | None] = mapped_column(String(150), nullable=True)
	hire_date: Mapped[date | None] = mapped_column(Date, nullable=True)

	is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		nullable=False,
	)

	user: Mapped["User | None"] = relationship("User")
