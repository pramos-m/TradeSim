import reflex as rx
from typing import List
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from ..database import SessionLocal
from ..models.user import User
from ..controller.user import get_user_by_email, get_user_by_username, get_user_by_id, create_user

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthState(rx.State):
    """Estado de autenticación mejorado."""
    # Authentication state
    is_authenticated: bool = False
    auth_token: str = rx.Cookie(name="auth_token", max_age=1800)
    processed_token: bool = False
    loading: bool = False
    
    # UI state
    active_tab: str = "login"
    error_message: str = ""
    
    # User data
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    
    # Add this to track the last path processed
    last_path: str = ""
    
    def create_access_token(self, user_id: int) -> str:
        """Create JWT token for authentication."""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> int:
        """Verify JWT token and return user ID or -1 if invalid."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = int(payload.get("sub"))
            return user_id
        except (JWTError, ValueError):
            return -1
    
    @rx.var
    def is_on_auth_page(self) -> bool:
        """Check if user is on login or registration page."""
        current_page = self.router.page.path
        return current_page == "/login"
    
    @rx.event
    async def on_load(self):
        """Handle page load authentication check."""
        # Get current path
        current_path = self.router.page.path
        
        # If we're on the same path as last time and already processed, skip processing
        if current_path == self.last_path and self.processed_token:
            return
        
        # Update last path
        self.last_path = current_path
        self.processed_token = True
        
        # Check if we have a token
        if not self.auth_token:
            # No token, not authenticated
            self.is_authenticated = False
            
            # Only redirect if we're on a protected page
            if current_path == "/dashboard":
                return rx.redirect("/login")
            return
        
        # We have a token, verify it
        user_id = self.verify_token(self.auth_token)
        if user_id <= 0:
            # Invalid token
            self.is_authenticated = False
            self.auth_token = ""  # Clear invalid token
            
            # Only redirect if we're on a protected page
            if current_path == "/dashboard":
                return rx.redirect("/login")
            return
        
        # Valid token, fetch user data
        db = SessionLocal()
        try:
            user = get_user_by_id(db, user_id)
            if user:
                self.username = user.username
                self.email = user.email
                self.is_authenticated = True
                
                # Only redirect if we're on the login page and authenticated
                if current_path == "/login":
                    return rx.redirect("/dashboard")
            else:
                # User not found, clear auth
                self.is_authenticated = False
                self.auth_token = ""
                
                # Only redirect if we're on a protected page
                if current_path == "/dashboard":
                    return rx.redirect("/login")
        finally:
            db.close()

    @rx.event
    async def login(self):
        """Process login attempt."""
        self.error_message = ""
        self.loading = True
        
        if not self.email or not self.password:
            self.error_message = "Por favor complete todos los campos"
            self.loading = False
            return
        
        db = None
        try:
            db = SessionLocal()
            
            # Direct query without the controller
            user = db.query(User).filter(User.email == self.email).first()
            
            if not user or not user.verify_password(self.password):
                self.error_message = "Email o contraseña incorrectos"
                self.loading = False
                return
            
            # When login is successful:
            self.is_authenticated = True
            self.username = user.username
            token = self.create_access_token(user.id)
            self.auth_token = token
            
            # Update last path to prevent redirect loops
            self.last_path = "/dashboard" 
            self.processed_token = True
            
            self.loading = False
            return rx.redirect("/dashboard")
                
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            self.loading = False
        finally:
            if db:
                db.close()

    @rx.event
    async def register(self):
        """Process registration attempt."""
        self.error_message = ""
        self.loading = True
        
        # Validate fields
        if not self.username or not self.email or not self.password:
            self.error_message = "Por favor complete todos los campos"
            self.loading = False
            return
        
        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden"
            self.loading = False
            return
        
        db = None
        try:
            db = SessionLocal()
            
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == self.email) | (User.username == self.username)
            ).first()
            
            if existing_user:
                self.error_message = "Usuario o email ya están registrados"
                self.loading = False
                return
            
            # Create new user
            new_user = User(
                username=self.username,
                email=self.email
            )
            new_user.set_password(self.password)
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            # Create and store token
            token = self.create_access_token(new_user.id)
            self.auth_token = token
            self.is_authenticated = True
            
            # Update last path to prevent redirect loops
            self.last_path = "/dashboard"
            self.processed_token = True
            
            self.loading = False
            return rx.redirect("/dashboard")
                
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            self.loading = False
        finally:
            if db:
                db.close()

    @rx.event
    def logout(self):
        """Process logout."""
        # Reset all state
        self.is_authenticated = False
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        
        # Important: Set processed_token to True to prevent immediate recheck
        self.processed_token = True
        self.last_path = "/"
        
        # Set to empty string to clear cookie
        self.auth_token = ""
        
        # Then redirect
        return rx.redirect("/")
    
    def set_active_tab(self, tab: str) -> None:
        """Switch between login/register tabs."""
        self.active_tab = tab
        self.error_message = ""
    
    def set_username(self, username: str) -> None:
        """Set username field."""
        self.username = username
        
    def set_email(self, email: str) -> None:
        """Set email field."""
        self.email = email
        
    def set_password(self, password: str) -> None:
        """Set password field."""
        self.password = password
        
    def set_confirm_password(self, confirm_password: str) -> None:
        """Set confirm password field."""
        self.confirm_password = confirm_password