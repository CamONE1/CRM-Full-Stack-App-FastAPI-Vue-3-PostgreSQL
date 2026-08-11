import uuid
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.offers import schemas
from app.offers.models import Offer


class InvalidTransition(Exception):
	def __init__(self, current_status: str):
		self.current_status = current_status
		super().__init__(f"Invalid transition from status '{current_status}'")


class MissingExpiry(Exception):
	pass


class OfferExpired(Exception):
	pass


class RespondConflict(Exception):
	def __init__(self, current_status: str):
		self.current_status = current_status
		super().__init__(f"Cannot respond: offer already '{current_status}'")


def _resolve_expiry(offer: Offer) -> bool:
	"""Flips a due 'sent' offer to 'expired' in place. Returns True if it changed."""
	if offer.status != "sent" or offer.expires_at is None:
		return False
	expires_at = offer.expires_at
	if expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)
	if expires_at < datetime.now(timezone.utc):
		offer.status = "expired"
		return True
	return False


def create_offer(db: Session, data: schemas.OfferCreate, created_by_id: int) -> Offer:
	offer = Offer(
		candidate_name=data.candidate_name,
		candidate_email=data.candidate_email,
		position=data.position,
		salary_note=data.salary_note,
		expires_at=data.expires_at,
		created_by_id=created_by_id,
	)
	db.add(offer)
	db.commit()
	db.refresh(offer)
	return offer


def get_offers(
	db: Session,
	search: str | None = None,
	status: str | None = None,
	position: str | None = None,
	include_archived: bool = False,
	offset: int = 0,
	limit: int = 50,
) -> tuple[list[Offer], int]:
	query = db.query(Offer)

	if not include_archived:
		query = query.filter(Offer.is_archived.is_(False))
	if search:
		like = f"%{search}%"
		query = query.filter(or_(Offer.candidate_name.ilike(like), Offer.candidate_email.ilike(like)))
	if status:
		query = query.filter(Offer.status == status)
	if position:
		query = query.filter(Offer.position == position)

	total = query.count()
	items = query.order_by(Offer.created_at.desc()).offset(offset).limit(limit).all()

	if any(_resolve_expiry(item) for item in items):
		db.commit()
	return items, total


def get_offer(db: Session, offer_id: int) -> Offer | None:
	offer = db.get(Offer, offer_id)
	if offer is not None and _resolve_expiry(offer):
		db.commit()
	return offer


def get_offer_by_token(db: Session, token: uuid.UUID) -> Offer | None:
	offer = db.query(Offer).filter(Offer.public_token == token).first()
	if offer is not None and _resolve_expiry(offer):
		db.commit()
	return offer


def get_distinct_positions(db: Session) -> list[str]:
	rows = db.query(Offer.position).distinct().order_by(Offer.position).all()
	return [row[0] for row in rows]


def update_offer_draft(db: Session, offer: Offer, data: schemas.OfferUpdate) -> Offer:
	if offer.status != "draft":
		raise InvalidTransition(offer.status)
	updates = data.model_dump(exclude_unset=True)
	for field, value in updates.items():
		setattr(offer, field, value)
	db.commit()
	db.refresh(offer)
	return offer


def send_offer(db: Session, offer: Offer) -> Offer:
	if offer.status != "draft":
		raise InvalidTransition(offer.status)
	if offer.expires_at is None:
		raise MissingExpiry()
	offer.status = "sent"
	offer.public_token = uuid.uuid4()
	db.commit()
	db.refresh(offer)
	return offer


def archive_offer(db: Session, offer: Offer) -> Offer:
	if not offer.is_archived:
		offer.is_archived = True
		offer.archived_at = datetime.now(timezone.utc)
		db.commit()
		db.refresh(offer)
	return offer


def respond_to_offer(db: Session, offer: Offer, action: str) -> Offer:
	if _resolve_expiry(offer):
		db.commit()

	if offer.status == "expired":
		raise OfferExpired()

	target_status = "accepted" if action == "accept" else "declined"

	if offer.status in ("accepted", "declined"):
		if offer.status == target_status:
			return offer  # idempotent repeat of the same action — no-op
		raise RespondConflict(offer.status)

	if offer.status != "sent":
		raise InvalidTransition(offer.status)

	offer.status = target_status
	offer.responded_at = datetime.now(timezone.utc)
	db.commit()
	db.refresh(offer)
	return offer
