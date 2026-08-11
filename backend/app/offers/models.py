import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
	from app.employees.models import Employee


class Offer(Base):
	__tablename__ = "offers"

	id: Mapped[int] = mapped_column(primary_key=True)

	candidate_name: Mapped[str] = mapped_column(String(255), nullable=False)
	candidate_email: Mapped[str] = mapped_column(String(255), nullable=False)
	position: Mapped[str] = mapped_column(String(150), nullable=False)
	salary_note: Mapped[str | None] = mapped_column(Text, nullable=True)

	# draft / sent / accepted / declined / expired — plain string, validated
	# via Pydantic Literal at the schema layer (see schemas.py). Chosen over a
	# native Postgres ENUM so adding a status later doesn't need an
	# ALTER TYPE ... ADD VALUE migration.
	status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="draft")

	created_by_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), nullable=False)

	# Generated only on the draft -> sent transition; null while draft.
	public_token: Mapped[uuid.UUID | None] = mapped_column(Uuid, unique=True, nullable=True, index=True)

	expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
	responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

	# Archive is a visibility flag, independent of status — not part of the
	# lifecycle state machine.
	is_archived: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
	archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

	created_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True),
		server_default=func.now(),
		nullable=False,
	)

	created_by: Mapped["Employee"] = relationship("Employee")
