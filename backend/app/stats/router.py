from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.common.rbac import require_roles
from app.core.db import get_db
from app.stats import schemas, service

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get(
	"",
	response_model=schemas.StatsOut,
	dependencies=[Depends(require_roles("hr", "admin"))],
	summary="Get dashboard stats",
	description="Aggregated offers funnel, employees breakdown, and recent items for the dashboard. "
	"HR/Admin only.",
)
def get_stats(db: Session = Depends(get_db)):
	return service.get_dashboard_stats(db=db)
