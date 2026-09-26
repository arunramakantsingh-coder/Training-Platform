import argparse

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote a platform administrator")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    email = args.email.strip().lower()
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, full_name=args.name.strip(), hashed_password=hash_password(args.password), is_platform_admin=True)
            db.add(user)
        else:
            user.full_name = args.name.strip()
            user.hashed_password = hash_password(args.password)
            user.is_platform_admin = True
            user.is_active = True
        db.commit()
        print(f"Platform admin ready: {email}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
