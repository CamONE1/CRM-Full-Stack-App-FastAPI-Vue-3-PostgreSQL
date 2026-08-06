from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.employees import schemas, service
from app.common.rbac import get_current_user_payload, require_roles

router = APIRouter(
	prefix="/employees",
	tags=["Employees"],
)


# Explicit paths (/me, /positions) must be declared before the /{employee_id}
# catch-all, otherwise FastAPI would try to match them against it first.

@router.get(
	"/me",
	response_model=schemas.EmployeeOut,
	summary="Get my employee profile",
	description="Returns the employee profile linked to the current user. Any authenticated role.",
)
def get_my_employee(db: Session = Depends(get_db), payload: dict = Depends(get_current_user_payload)):
	employee = service.get_employee_by_user_id(db=db, user_id=int(payload["sub"]))
	if employee is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employee profile linked to current user")
	return employee


@router.patch(
	"/me",
	response_model=schemas.EmployeeOut,
	summary="Update my employee profile",
	description="Partially updates the current user's own phone/telegram. Any authenticated role.",
)
def update_my_employee(
	data: schemas.EmployeeSelfUpdate,
	db: Session = Depends(get_db),
	payload: dict = Depends(get_current_user_payload),
):
	employee = service.get_employee_by_user_id(db=db, user_id=int(payload["sub"]))
	if employee is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No employee profile linked to current user")
	return service.update_employee_self(db=db, employee=employee, data=data)


@router.get(
	"/positions",
	response_model=list[str],
	dependencies=[Depends(require_roles("hr", "admin"))],
	summary="List distinct positions",
	description="Returns distinct, non-null employee positions, for filter dropdowns. HR/Admin only.",
)
def list_positions(db: Session = Depends(get_db)):
	return service.get_distinct_positions(db=db)


@router.get(
	"",
	response_model=schemas.EmployeeListOut,
	dependencies=[Depends(require_roles("hr", "admin"))],
	summary="List employees",
	description="Returns a paginated, filterable list of employees. HR/Admin only.",
)
def list_employees(
	search: str | None = None,
	position: str | None = None,
	is_active: bool | None = None,
	offset: int = 0,
	limit: int = 50,
	db: Session = Depends(get_db),
):
	items, total = service.get_employees(
		db=db, search=search, position=position, is_active=is_active, offset=offset, limit=limit
	)
	return schemas.EmployeeListOut(items=items, total=total)


@router.get(
	"/{employee_id}",
	response_model=schemas.EmployeeOut,
	dependencies=[Depends(require_roles("hr", "admin"))],
	summary="Get employee by id",
	description="Returns a single employee card. HR/Admin only.",
)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
	employee = service.get_employee(db=db, employee_id=employee_id)
	if employee is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
	return employee
