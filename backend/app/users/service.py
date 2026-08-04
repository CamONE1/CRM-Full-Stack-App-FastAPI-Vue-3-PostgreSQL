from sqlalchemy.orm import Session

from app.users import schemas
from app.users.models import User


def get_users(db: Session, offset: int = 0, limit: int = 50):
	return db.query(User).offset(offset).limit(limit).all()


def get_user(db: Session, user_id: int) -> User | None:
	return db.get(User, user_id)


def update_user(db: Session, user: User, data: schemas.UserUpdate) -> User:
	updates = data.model_dump(exclude_unset=True)
	for field, value in updates.items():
		setattr(user, field, value)
	db.commit()
	db.refresh(user)
	return user
