from app.db.session import SessionLocal
from app.models.user import User

def check_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\nUsers in database:")
        for user in users:
            print(f"\nEmail: {user.email}")
            print(f"Username: {user.username}")
            print(f"Is active: {user.is_active}")
            print(f"Role: {user.role}")
            print("---")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 