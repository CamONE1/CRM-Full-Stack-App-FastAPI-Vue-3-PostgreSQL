from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

OfferStatus = Literal["draft", "sent", "accepted", "declined", "expired"]


class OfferOut(BaseModel):
	id: int
	candidate_name: str
	candidate_email: str
	position: str
	salary_note: str | None
	status: OfferStatus
	created_by_id: int
	public_token: UUID | None
	expires_at: datetime | None
	responded_at: datetime | None
	is_archived: bool
	archived_at: datetime | None
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class OfferListOut(BaseModel):
	items: list[OfferOut]
	total: int


class OfferCreate(BaseModel):
	candidate_name: str
	candidate_email: str
	position: str
	salary_note: str | None = None
	expires_at: datetime | None = None


class OfferUpdate(BaseModel):
	candidate_name: str | None = None
	candidate_email: str | None = None
	position: str | None = None
	salary_note: str | None = None
	expires_at: datetime | None = None


class OfferRespond(BaseModel):
	action: Literal["accept", "decline"]


class OfferPublicOut(BaseModel):
	candidate_name: str
	position: str
	salary_note: str | None
	status: OfferStatus
	expires_at: datetime | None
	responded_at: datetime | None

	model_config = ConfigDict(from_attributes=True)
