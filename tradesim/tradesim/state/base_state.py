# /state/base_state.py
import reflex as rx
from typing import Optional
from ..models.user import User
from ..database import SessionLocal
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Constants for JWT
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class State(rx.State):
    """Base state that includes authentication and other functionality."""
    
    # Authentication state variables
    username: str = ""
    password: str = ""
    email: str = ""
    is_logged: bool = False
    error_message: Optional[str] = None
    
    # Original state variables
    count: int = 0
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def login(self):
        """Process login."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == self.username).first()
            
            # Verify credentials
            if not user or not User.verify_password(self.password, user.hashed_password):
                self.error_message = "Incorrect username or password"
                return
            
            # Create token and update state
            token = self.create_access_token({"sub": user.username})
            self.is_logged = True
            self.error_message = None
            
            # Save token and redirect
            rx.window_localStorage.set_item("token", token)
            return rx.redirect("/dashboard")
    
    def register(self):
        """Register a new user."""
        with SessionLocal() as db:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.username == self.username) | (User.email == self.email)
            ).first()
            
            if existing_user:
                self.error_message = "Username or email already registered"
                return
            
            # Create new user
            new_user = User(
                username=self.username,
                email=self.email,
                hashed_password=User.get_password_hash(self.password)
            )
            
            db.add(new_user)
            db.commit()
            
            # Log in automatically
            self.login()
    
    def logout(self):
        """Log out the user."""
        self.is_logged = False
        self.username = ""
        self.password = ""
        self.email = ""
        return rx.window_localStorage.remove_item("token")
    
    def check_auth(self):
        """Check if there is a valid token."""
        token = rx.window_localStorage.get_item("token")
        if not token:
            self.is_logged = False
            return
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                self.is_logged = False
                return
            
            self.is_logged = True
            self.username = username
        except JWTError:
            self.is_logged = False
            return rx.window_localStorage.remove_item("token")
    
    # Original counter methods
    def increment(self):
        """Increment the counter."""
        self.count += 1
    
    def decrement(self):
        """Decrement the counter."""
        self.count -= 1