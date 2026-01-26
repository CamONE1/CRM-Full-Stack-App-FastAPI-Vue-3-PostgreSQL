from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.news import schemas, service
from app.core.db import get_db

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
def create_news(news: schemas.NewsCreate, db: Session = Depends(get_db)):
	return service.create_news(db=db, news=news)

# get_news
@router.get(
	'',
	response_model=list[schemas.News],
  summary="Get news list",
  description="Returns a list of news items (with pagination).",
)
def get_news(offset: int = 0, limit: int = 10, db: Session = Depends(get_db)):
	return service.get_news(db=db, offset=offset, limit=limit)