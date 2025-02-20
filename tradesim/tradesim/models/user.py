# models/user.py
from sqlalchemy import Column, String, Numeric, CheckConstraint, Boolean
from ..models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    profile_image = Column(String, nullable=True)
    account_balance = Column(Numeric(10, 2), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        CheckConstraint('account_balance >= 0', name='check_account_balance_positive'),
    )

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            # Convert plain_password to bytes if it's not already
            if isinstance(plain_password, str):
                plain_password = plain_password.encode('utf-8')
            
            # Convert hashed_password to bytes if it's not already
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
                
            return bcrypt.checkpw(plain_password, hashed_password)
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        if not password:
            raise ValueError("Password cannot be empty")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Convert password to bytes if it's not already
        if isinstance(password, str):
            password = password.encode('utf-8')
            
        # Generate salt and hash password
        salt = bcrypt.gensalt(12)
        hashed = bcrypt.hashpw(password, salt)
        
        # Return hash as string
        return hashed.decode('utf-8')

    def to_dict(self, include_sensitive: bool = False):
        """Convert user object to dictionary excluding sensitive data."""
        base_dict = {
            "id": self.id,
            "username": self.username,
            "profile_picture": self.profile_picture,
            "balance": self.balance,
            "initial_balance": self.initial_balance,
            "is_active": self.is_active,
            "created_at": self.created_at
        }
        
        if include_sensitive:
            base_dict["email"] = self.email
            
        return base_dict