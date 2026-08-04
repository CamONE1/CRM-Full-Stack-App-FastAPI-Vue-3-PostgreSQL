from sqlalchemy.orm import Session
from app.news import models, schemas


def create_news(db: Session, news: schemas.NewsCreate, author_id: int):
	db_news = models.News(**news.model_dump(), author_id=author_id)
	db.add(db_news)
	db.commit()
	db.refresh(db_news)
	return db_news

def get_news(db: Session, offset: int = 0, limit: int = 10):
	return db.query(models.News).offset(offset).limit(limit).all()