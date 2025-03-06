# from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
# from sqlalchemy.sql import func
# from ..database import Base
# import bcrypt

# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)
#     initial_balance = Column(Float, default=10000.0)
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
#     def set_password(self, password):
#         """Hash password and store it."""
#         salt = bcrypt.gensalt()
#         self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
#     def verify_password(self, password):
#         """Verify password against stored hash."""
#         return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))

# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, LargeBinary
from sqlalchemy.sql import func
from ..database import Base
import bcrypt

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    initial_balance = Column(Float, default=10000.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    profile_picture = Column(LargeBinary, nullable=True)
    profile_picture_type = Column(String, nullable=True)
    
    def set_password(self, password):
        """Hash password and store it."""
        salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password):
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))