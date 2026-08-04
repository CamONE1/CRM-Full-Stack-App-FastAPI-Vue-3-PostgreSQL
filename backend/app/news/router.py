from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.news import schemas, service
from app.common.rbac import require_roles
from app.employees.models import Employee

router = APIRouter(
	prefix="/news",
	tags=["News"],
)

# create_news
@router.post(
	'',
	response_model=schemas.News,
	status_code=status.HTTP_201_CREATED,
  summary="Create news",
  description="Creates a news item and returns it with generated ID and timestamp.",
)
def create_news(
	news: schemas.NewsCreate,
	db: Session = Depends(get_db),
	payload: dict = Depends(require_roles("hr", "admin")),
):
	author = db.query(Employee).filter(Employee.user_id == int(payload["sub"])).first()
	if author is None:
		raise HTTPException(
			status_code=400,
			detail="Current user has no linked employee profile — cannot author news",
		)
	return service.create_news(db=db, news=news, author_id=author.id)

# get_news
@router.get(
	'',
	response_model=list[schemas.News],
  summary="Get news list",
  description="Returns a list of news items (with pagination).",
)
def get_news(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
	return service.get_news(db=db, offset=offset, limit=limit)