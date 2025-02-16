# from typing import Optional, Generator
# import reflex as rx
# from sqlalchemy.orm import Session
# from ..database import get_db
# from ..models.user import User
# from datetime import datetime, timedelta
# from jose import jwt, JWTError
# import os
# from dotenv import load_dotenv

# load_dotenv()

# SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# class AuthState(rx.State):
#     """Authentication state management."""
    
#     # Form fields
#     username: str = ""
#     email: str = ""
#     password: str = ""
#     confirm_password: str = ""
    
#     # UI state
#     active_tab: str = "login"
#     auth_token: Optional[str] = None
#     error_message: Optional[str] = None
#     is_logged: bool = False
    
#     def on_mount(self):
#         """Initialize state when component mounts."""
#         return self.check_auth()

#     # ... [mantener los métodos create_access_token, verify_token y set_form_field igual] ...

#     def login(self) -> rx.event.EventSpec:
#         """Handle login."""
#         if not self.email or not self.password:
#             self.error_message = "Please fill in all fields"
#             return rx.window_alert("Please fill in all fields")

#         try:
#             db = next(get_db())
#             user = db.query(User).filter(User.email == self.email).first()
            
#             if not user or not User.verify_password(self.password, user.hashed_password):
#                 self.error_message = "Invalid email or password"
#                 return rx.window_alert("Invalid email or password")

#             # Create JWT token
#             token = self.create_access_token({"sub": user.email})
            
#             # Set auth state
#             self.auth_token = token
#             self.is_logged = True
#             self.username = user.username
            
#             # Usar set_cookie en lugar de localStorage
#             return [
#                 self.set_cookie("auth_token", token),
#                 self.set_cookie("username", user.username),
#                 rx.redirect("/dashboard")
#             ]
            
#         except Exception as e:
#             self.error_message = f"An error occurred: {str(e)}"
#             return rx.window_alert(f"An error occurred: {str(e)}")

#     def register(self) -> rx.event.EventSpec:
#         """Handle registration."""
#         # [Mantener las validaciones iniciales igual]
#         try:
#             # [Mantener la lógica de creación de usuario igual]
            
#             # Create JWT token
#             token = self.create_access_token({"sub": user.email})
            
#             # Set auth state
#             self.auth_token = token
#             self.is_logged = True
            
#             # Usar set_cookie en lugar de localStorage
#             return [
#                 self.set_cookie("auth_token", token),
#                 self.set_cookie("username", user.username),
#                 rx.redirect("/dashboard")
#             ]
            
#         except Exception as e:
#             self.error_message = f"An error occurred: {str(e)}"
#             return rx.window_alert(f"An error occurred: {str(e)}")

#     def logout(self) -> rx.event.EventSpec:
#         """Handle logout."""
#         self.auth_token = None
#         self.is_logged = False
#         self.username = ""
#         self.email = ""
#         self.password = ""
#         self.confirm_password = ""
#         self.error_message = None
        
#         # Limpiar cookies en lugar de localStorage
#         return [
#             self.clear_cookie("auth_token"),
#             self.clear_cookie("username"),
#             rx.redirect("/login")
#         ]

#     def check_auth(self) -> rx.event.EventSpec:
#         """Check authentication status on page load."""
#         try:
#             # Usar cookies en lugar de localStorage
#             token = self.get_cookie("auth_token")
#             username = self.get_cookie("username")
            
#             if not token or not username:
#                 self.is_logged = False
#                 return False
                
#             email = self.verify_token(token)
#             if not email:
#                 self.is_logged = False
#                 self.clear_cookie("auth_token")
#                 self.clear_cookie("username")
#                 return False
                
#             # Verify user exists
#             db = next(get_db())
#             user = db.query(User).filter(User.email == email).first()
#             if not user:
#                 self.is_logged = False
#                 return False
                
#             self.auth_token = token
#             self.is_logged = True
#             self.username = username
#             return True
                
#         except Exception:
#             self.is_logged = False
#             return False

import reflex as rx
from typing import Optional, List, Any, Callable
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
import re
from dotenv import load_dotenv
from ..database import get_db
from ..models.user import User

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthState(rx.State):
    """Estado de autenticación."""
    
    # Form fields
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    
    # UI state
    active_tab: str = "login"
    error_message: str = ""
    is_authenticated: bool = False
    loading: bool = False
    
    def on_mount(self) -> None:
        """Initialize state when component mounts."""
        self.check_auth()

    def username_change(self, value: str) -> None:
        """Update username field."""
        self.username = value.strip()
        self.error_message = ""

    def email_change(self, value: str) -> None:
        """Update email field."""
        self.email = value.lower().strip()
        self.error_message = ""

    def password_change(self, value: str) -> None:
        """Update password field."""
        self.password = value.strip()
        self.error_message = ""

    def confirm_password_change(self, value: str) -> None:
        """Update confirm password field."""
        self.confirm_password = value.strip()
        self.error_message = ""

    def validate_email(self, email: str) -> bool:
        """Validar formato de email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validar fortaleza de contraseña."""
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        if not re.search(r'[A-Z]', password):
            return False, "La contraseña debe tener al menos una mayúscula"
        if not re.search(r'[a-z]', password):
            return False, "La contraseña debe tener al menos una minúscula"
        if not re.search(r'\d', password):
            return False, "La contraseña debe tener al menos un número"
        return True, ""

    def create_access_token(self, data: dict) -> str:
        """Crear token JWT con payload adicional de seguridad."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[str]:
        """Verificar token JWT con validaciones adicionales."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "access":
                return None
            return payload.get("sub")
        except JWTError:
            return None

    def check_auth(self) -> None:
        """Check authentication status."""
        try:
            token = self.get_cookie("auth_token")
            if not token:
                self.is_authenticated = False
                return

            email = self.verify_token(token)
            if not email:
                self.is_authenticated = False
                self.clear_auth_cookies()
                return

            db = next(get_db())
            user = db.query(User).filter(User.email == email).first()
            
            if user and user.is_active:
                self.is_authenticated = True
                self.username = self.get_cookie("username", "")
            else:
                self.is_authenticated = False
                self.clear_auth_cookies()
                
        except Exception as e:
            print(f"Error in check_auth: {str(e)}")
            self.is_authenticated = False
            self.clear_auth_cookies()

    def clear_auth_cookies(self) -> None:
        """Limpiar cookies de autenticación."""
        self.clear_cookie("auth_token")
        self.clear_cookie("username")

    def login(self) -> List[rx.event.Event]:
        """Manejar login."""
        self.loading = True
        self.error_message = ""
        
        if not self.email or not self.password:
            self.error_message = "Por favor, complete todos los campos"
            self.loading = False
            return [rx.window_alert("Por favor, complete todos los campos")]

        if not self.validate_email(self.email):
            self.error_message = "Formato de email inválido"
            self.loading = False
            return [rx.window_alert("Formato de email inválido")]

        try:
            db = next(get_db())
            user = db.query(User).filter(User.email == self.email).first()
            
            if not user or not User.verify_password(self.password, user.hashed_password):
                self.error_message = "Email o contraseña inválidos"
                self.loading = False
                return [rx.window_alert("Email o contraseña inválidos")]

            if not user.is_active:
                self.error_message = "Usuario inactivo"
                self.loading = False
                return [rx.window_alert("Usuario inactivo")]

            token = self.create_access_token({"sub": user.email})
            self.is_authenticated = True
            self.username = user.username
            self.loading = False
            
            return [
                self.set_cookie("auth_token", token),
                self.set_cookie("username", user.username),
                rx.redirect("/dashboard")
            ]
            
        except Exception as e:
            self.error_message = f"Error en el login: {str(e)}"
            self.loading = False
            return [rx.window_alert(f"Error en el login: {str(e)}")]

    def register(self) -> List[rx.event.Event]:
        """Manejar registro."""
        self.loading = True
        self.error_message = ""
        
        if not all([self.username, self.email, self.password, self.confirm_password]):
            self.error_message = "Por favor, complete todos los campos"
            self.loading = False
            return [rx.window_alert("Por favor, complete todos los campos")]

        # Validaciones
        if not self.validate_email(self.email):
            self.error_message = "Formato de email inválido"
            self.loading = False
            return [rx.window_alert("Formato de email inválido")]

        is_valid_password, password_error = self.validate_password(self.password)
        if not is_valid_password:
            self.error_message = password_error
            self.loading = False
            return [rx.window_alert(password_error)]

        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden"
            self.loading = False
            return [rx.window_alert("Las contraseñas no coinciden")]

        if len(self.username) < 3:
            self.error_message = "El nombre de usuario debe tener al menos 3 caracteres"
            self.loading = False
            return [rx.window_alert("El nombre de usuario debe tener al menos 3 caracteres")]

        try:
            db = next(get_db())
            
            # Verificar usuario existente
            if db.query(User).filter(User.email == self.email).first():
                self.error_message = "El email ya está registrado"
                self.loading = False
                return [rx.window_alert("El email ya está registrado")]
            
            if db.query(User).filter(User.username == self.username).first():
                self.error_message = "El nombre de usuario ya está en uso"
                self.loading = False
                return [rx.window_alert("El nombre de usuario ya está en uso")]

            # Crear nuevo usuario
            hashed_password = User.get_password_hash(self.password)
            new_user = User(
                username=self.username,
                email=self.email,
                hashed_password=hashed_password,
                balance=10000.0,
                initial_balance=10000.0,
                is_active=True
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # Crear token y login
            token = self.create_access_token({"sub": new_user.email})
            self.is_authenticated = True
            self.loading = False
            
            return [
                self.set_cookie("auth_token", token),
                self.set_cookie("username", new_user.username),
                rx.redirect("/dashboard")
            ]
            
        except Exception as e:
            self.error_message = f"Error en el registro: {str(e)}"
            self.loading = False
            return [rx.window_alert(f"Error en el registro: {str(e)}")]

    def logout(self) -> List[rx.event.Event]:
        """Manejar logout."""
        self.is_authenticated = False
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.error_message = ""
        self.clear_auth_cookies()
        
        return [rx.redirect("/login")]

    def switch_tab(self, tab: str) -> None:
        """Cambiar entre tabs de login/registro."""
        self.active_tab = tab
        self.error_message = ""
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""