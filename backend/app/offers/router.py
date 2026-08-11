from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.employees.models import Employee
from app.offers import schemas, service
from app.offers.models import Offer
from app.common.rbac import require_roles

HR_ADMIN = ("hr", "admin")

router = APIRouter(prefix="/offers", tags=["Offers"])
public_router = APIRouter(prefix="/public/offers", tags=["Public Offers"])


def _get_offer_or_404(db: Session, offer_id: int) -> Offer:
	offer = service.get_offer(db=db, offer_id=offer_id)
	if offer is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
	return offer


# Explicit paths (/positions) must be declared before the /{offer_id}
# catch-all, otherwise FastAPI would try to match them against it first.

@router.get(
	"/positions",
	response_model=list[str],
	dependencies=[Depends(require_roles(*HR_ADMIN))],
	summary="List distinct positions",
	description="Returns distinct offer positions, for filter dropdowns. HR/Admin only.",
)
def list_positions(db: Session = Depends(get_db)):
	return service.get_distinct_positions(db=db)


@router.get(
	"",
	response_model=schemas.OfferListOut,
	dependencies=[Depends(require_roles(*HR_ADMIN))],
	summary="List offers",
	description="Returns a paginated, filterable list of offers. Archived offers are hidden unless "
	"include_archived=true. HR/Admin only.",
)
def list_offers(
	search: str | None = None,
	status_filter: schemas.OfferStatus | None = Query(default=None, alias="status"),
	position: str | None = None,
	include_archived: bool = False,
	offset: int = 0,
	limit: int = 50,
	db: Session = Depends(get_db),
):
	items, total = service.get_offers(
		db=db,
		search=search,
		status=status_filter,
		position=position,
		include_archived=include_archived,
		offset=offset,
		limit=limit,
	)
	return schemas.OfferListOut(items=items, total=total)


@router.post(
	"",
	response_model=schemas.OfferOut,
	status_code=status.HTTP_201_CREATED,
	summary="Create a draft offer",
	description="Creates a new offer in draft status, authored by the current user's employee profile. "
	"HR/Admin only.",
)
def create_offer(
	data: schemas.OfferCreate,
	db: Session = Depends(get_db),
	payload: dict = Depends(require_roles(*HR_ADMIN)),
):
	author = db.query(Employee).filter(Employee.user_id == int(payload["sub"])).first()
	if author is None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Current user has no linked employee profile — cannot author offers",
		)
	return service.create_offer(db=db, data=data, created_by_id=author.id)


@router.get(
	"/{offer_id}",
	response_model=schemas.OfferOut,
	dependencies=[Depends(require_roles(*HR_ADMIN))],
	summary="Get offer by id",
	description="Returns a single offer. HR/Admin only.",
)
def get_offer(offer_id: int, db: Session = Depends(get_db)):
	return _get_offer_or_404(db, offer_id)


@router.patch(
	"/{offer_id}",
	response_model=schemas.OfferOut,
	dependencies=[Depends(require_roles(*HR_ADMIN))],
	summary="Update a draft offer",
	description="Partially updates a draft offer's fields. Only allowed while status is 'draft'. HR/Admin only.",
)
def update_offer(offer_id: int, data: schemas.OfferUpdate, db: Session = Depends(get_db)):
	offer = _get_offer_or_404(db, offer_id)
	try:
		return service.update_offer_draft(db=db, offer=offer, data=data)
	except service.InvalidTransition as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"Cannot edit offer: not a draft (current status: '{exc.current_status}')",
		)


@router.post(
	"/{offer_id}/send",
	response_model=schemas.OfferOut,
	dependencies=[Depends(require_roles(*HR_ADMIN))],
	summary="Send a draft offer",
	description="Transitions a draft offer to 'sent' and generates its public token. Requires expires_at "
	"to be set. HR/Admin only.",
)
def send_offer(offer_id: int, db: Session = Depends(get_db)):
	offer = _get_offer_or_404(db, offer_id)
	try:
		return service.send_offer(db=db, offer=offer)
	except service.InvalidTransition as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"Cannot send offer: not a draft (current status: '{exc.current_status}')",
		)
	except service.MissingExpiry:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			detail="Cannot send offer: expires_at must be set first",
		)


@router.post(
	"/{offer_id}/archive",
	response_model=schemas.OfferOut,
	dependencies=[Depends(require_roles(*HR_ADMIN))],
	summary="Archive an offer",
	description="Hides an offer from the default list view. Idempotent, works on any status. HR/Admin only.",
)
def archive_offer(offer_id: int, db: Session = Depends(get_db)):
	offer = _get_offer_or_404(db, offer_id)
	return service.archive_offer(db=db, offer=offer)


# --- Public endpoints: no auth, looked up by token, never by numeric id ---

@public_router.get(
	"/{token}",
	response_model=schemas.OfferPublicOut,
	summary="Get a public offer by token",
	description="Returns the candidate-facing view of an offer. No authentication.",
)
def get_public_offer(token: UUID, db: Session = Depends(get_db)):
	offer = service.get_offer_by_token(db=db, token=token)
	if offer is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
	return offer


@public_router.post(
	"/{token}/respond",
	response_model=schemas.OfferPublicOut,
	summary="Accept or decline a public offer",
	description="Candidate action on their offer. Idempotent: repeating the same action is a no-op; "
	"the opposite action after a terminal response is rejected. No authentication.",
)
def respond_to_public_offer(token: UUID, data: schemas.OfferRespond, db: Session = Depends(get_db)):
	offer = service.get_offer_by_token(db=db, token=token)
	if offer is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
	try:
		return service.respond_to_offer(db=db, offer=offer, action=data.action)
	except service.OfferExpired:
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Offer expired")
	except service.RespondConflict as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"Offer already '{exc.current_status}'",
		)
	except service.InvalidTransition as exc:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=f"Cannot respond: offer is '{exc.current_status}'",
		)
