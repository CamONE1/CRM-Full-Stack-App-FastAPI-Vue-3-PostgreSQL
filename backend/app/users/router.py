from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.users import schemas, service
from app.common.rbac import require_roles

router = APIRouter(
	prefix="/users",
	tags=["Users"],
	dependencies=[Depends(require_roles("admin"))],
)


@router.get(
	"",
	response_model=list[schemas.UserOut],
	summary="List users",
	description="Returns a list of users (with pagination). Admin only.",
)
def list_users(offset: int = 0, limit: int = 50, db: Session = Depends(get_db)):
	return service.get_users(db=db, offset=offset, limit=limit)


@router.patch(
	"/{user_id}",
	response_model=schemas.UserOut,
	summary="Update a user",
	description="Partially updates a user's role and/or active status. Admin only.",
)
def update_user(user_id: int, data: schemas.UserUpdate, db: Session = Depends(get_db)):
	user = service.get_user(db=db, user_id=user_id)
	if user is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
	return service.update_user(db=db, user=user, data=data)
