from app.core.db import SessionLocal
from app.users.models import User, UserRole
from app.auth.security import hash_password


def main():
	db = SessionLocal()

	email = "admin@crm.com"
	password = "admin12345"

	exists = db.query(User).filter(User.email == email).first()
	if exists:
		print("Admin already exists:", email)
		return

	admin = User(
		email=email,
		password_hash=hash_password(password),
		role=UserRole.admin,
		is_active=True,
	)
	db.add(admin)
	db.commit()

	print("Created admin:", email)
	print("Password:", password)


if __name__ == "__main__":
	main()
