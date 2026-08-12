from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.employees.models import Employee
from app.news.models import News
from app.offers.models import Offer
from app.offers.schemas import OfferStatus

RECENT_LIMIT = 5
OFFER_STATUSES: tuple[OfferStatus, ...] = ("draft", "sent", "accepted", "declined", "expired")
NO_DEPARTMENT_LABEL = "Без отдела"


def _resolve_due_expiries(db: Session) -> None:
	"""Bulk-flips any 'sent' offer past its expires_at to 'expired'. Offers/service.py only
	resolves expiry lazily on individual reads, so a stale 'sent' offer nobody has opened
	since expiring would otherwise show up as 'sent' in the aggregate funnel below."""
	now = datetime.now(timezone.utc)
	updated = (
		db.query(Offer)
		.filter(Offer.status == "sent", Offer.expires_at < now)
		.update({"status": "expired"}, synchronize_session=False)
	)
	if updated:
		db.commit()


def _offers_stats(db: Session) -> dict:
	rows = (
		db.query(Offer.status, func.count())
		.filter(Offer.is_archived.is_(False))
		.group_by(Offer.status)
		.all()
	)
	by_status: dict[str, int] = dict.fromkeys(OFFER_STATUSES, 0)
	by_status.update(dict(rows))
	return {"total": sum(by_status.values()), "by_status": by_status}


def _employees_stats(db: Session) -> dict:
	rows = db.query(Employee.department, func.count()).group_by(Employee.department).all()
	by_department: dict[str, int] = {}
	for department, count in rows:
		by_department[department or NO_DEPARTMENT_LABEL] = count

	total = sum(by_department.values())
	active = db.query(func.count(Employee.id)).filter(Employee.is_active.is_(True)).scalar()
	return {"total": total, "active": active, "inactive": total - active, "by_department": by_department}


def _recent_offers(db: Session) -> list[Offer]:
	return (
		db.query(Offer)
		.filter(Offer.is_archived.is_(False))
		.order_by(Offer.created_at.desc())
		.limit(RECENT_LIMIT)
		.all()
	)


def _recent_news(db: Session) -> list[News]:
	return db.query(News).order_by(News.created_at.desc()).limit(RECENT_LIMIT).all()


def get_dashboard_stats(db: Session) -> dict:
	_resolve_due_expiries(db)
	return {
		"offers": _offers_stats(db),
		"employees": _employees_stats(db),
		"recent_offers": _recent_offers(db),
		"recent_news": _recent_news(db),
	}
