from sqlalchemy.orm import Session
from ..models.user import User

def create_user(db: Session, username: str, email: str, password: str):
    """Create a new user with default balance."""
    user = User(username=username, email=email)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def update_profile_picture(db: Session, user_id: int, picture_data: bytes, picture_type: str) -> User:
    """Update user's profile picture."""
    user = get_user_by_id(db, user_id)
    if user:
        user.profile_picture = picture_data
        user.profile_picture_type = picture_type
        db.commit()
        db.refresh(user)
    return user

def get_user_profile_picture(db: Session, user_id: int):
    """Retrieve user's profile picture."""
    user = get_user_by_id(db, user_id)
    if user and user.profile_picture:
        return user.profile_picture, user.profile_picture_type
    return None, None