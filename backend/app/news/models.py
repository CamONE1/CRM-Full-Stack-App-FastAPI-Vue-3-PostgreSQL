from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
	from app.employees.models import Employee


class News(Base):
	__tablename__ ="news"

	id: Mapped[int] = mapped_column(primary_key=True)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	body: Mapped[str] = mapped_column(Text, nullable=False)
	author_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		nullable=False,
	)

	author: Mapped["Employee"] = relationship("Employee")