# /state/auth_state.py
from typing import Optional
import reflex as rx
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User

class AuthState(rx.State):
    """The auth state."""
    
    # Form fields
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    
    # UI state
    active_tab: str = "login"
    auth_token: Optional[str] = None
    error_message: Optional[str] = None
    is_logged: bool = False  # Add this line
    
    def set_username(self, username: str):
        self.username = username
        
    def set_email(self, email: str):
        self.email = email
        
    def set_password(self, password: str):
        self.password = password
        
    def set_confirm_password(self, confirm_password: str):
        self.confirm_password = confirm_password
        
    def set_active_tab(self, tab: str) -> None:
        """Set the active tab."""
        self.active_tab = tab
        # Clear form fields and error message when switching tabs
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.error_message = None

    def login(self):
        """Handle login."""
        try:
            # Input validation
            if not self.email or not self.password:
                self.error_message = "Please fill in all fields"
                return

            # Get database session
            db = next(get_db())
            
            # Find user
            user = db.query(User).filter(User.email == self.email).first()
            
            if not user or not User.verify_password(self.password, user.hashed_password):
                self.error_message = "Invalid email or password"
                return

            # Set auth token in state
            self.auth_token = str(user.id)  # Simple token for now
            
            # Clear form and error
            self.password = ""
            self.error_message = None
            
            # Redirect to dashboard
            return rx.redirect("/dashboard")
            
        except Exception as e:
            self.error_message = f"An error occurred: {str(e)}"

    def register(self):
        """Handle registration."""
        try:
            # Input validation
            if not all([self.username, self.email, self.password, self.confirm_password]):
                self.error_message = "Please fill in all fields"
                return
                
            if self.password != self.confirm_password:
                self.error_message = "Passwords do not match"
                return
                
            # Get database session
            db = next(get_db())
            
            # Check if user exists
            if db.query(User).filter(User.email == self.email).first():
                self.error_message = "Email already registered"
                return
                
            if db.query(User).filter(User.username == self.username).first():
                self.error_message = "Username already taken"
                return
            
            # Create new user
            hashed_password = User.get_password_hash(self.password)
            user = User(
                username=self.username,
                email=self.email,
                hashed_password=hashed_password
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Set auth token
            self.auth_token = str(user.id)
            
            # Clear form and error
            self.username = ""
            self.email = ""
            self.password = ""
            self.confirm_password = ""
            self.error_message = None
            
            # Redirect to dashboard
            return rx.redirect("/dashboard")
            
        except Exception as e:
            self.error_message = f"An error occurred: {str(e)}"

    def logout(self):
        """Handle logout."""
        self.auth_token = None
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.error_message = None
        return rx.redirect("/login")

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.auth_token is not None

    def require_auth(self):
        """Redirect to login if not authenticated."""
        if not self.is_authenticated():
            return rx.redirect("/login")