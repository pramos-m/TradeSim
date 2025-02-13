# import reflex as rx
# from typing import Optional
# from ..models.user import User
# from ..database import SessionLocal
# from jose import jwt, JWTError
# from datetime import datetime, timedelta

# SECRET_KEY = "your-secret-key-here"  # En producción, usar variable de entorno
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# class AuthState(rx.State):
#     """Estado para la autenticación."""
    
#     # Variables de estado
#     username: str = ""
#     password: str = ""
#     email: str = ""
#     is_logged: bool = False
#     token: Optional[str] = None  # Ahora almacenamos el token en el estado
#     error_message: Optional[str] = None
    
#     def create_access_token(self, data: dict):
#         to_encode = data.copy()
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         to_encode.update({"exp": expire})
#         encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#         return encoded_jwt

#     def login(self):
#         """Procesa el inicio de sesión."""
#         try:
#             with SessionLocal() as db:
#                 user = db.query(User).filter(User.username == self.username).first()
#                 if not user or not User.verify_password(self.password, user.hashed_password):
#                     self.error_message = "Usuario o contraseña incorrectos"
#                     return

#                 # Crear token y almacenarlo en el estado
#                 token = self.create_access_token({"sub": user.username})
#                 self.is_logged = True
#                 self.token = token
#                 self.error_message = None
                
#                 # Guardar token en localStorage desde el frontend
#                 return [
#                     rx.set_local_storage("token", token),
#                     rx.redirect("/dashboard")
#                 ]
#         except Exception as e:
#             self.error_message = f"Error durante el login: {str(e)}"
#             return

#     def register(self):
#         """Registra un nuevo usuario."""
#         try:
#             with SessionLocal() as db:
#                 existing_user = db.query(User).filter(
#                     (User.username == self.username) | (User.email == self.email)
#                 ).first()
                
#                 if existing_user:
#                     self.error_message = "Usuario o email ya registrado"
#                     return

#                 new_user = User(
#                     username=self.username,
#                     email=self.email,
#                     hashed_password=User.get_password_hash(self.password)
#                 )
#                 db.add(new_user)
#                 db.commit()
                
#                 # Iniciar sesión automáticamente después del registro
#                 return self.login()
#         except Exception as e:
#             self.error_message = f"Error durante el registro: {str(e)}"
#             return

#     def logout(self):
#         """Cierra la sesión del usuario."""
#         self.is_logged = False
#         self.username = ""
#         self.password = ""
#         self.email = ""
#         self.token = None  # Limpiar el token
#         return [
#             rx.remove_local_storage("token"),
#             rx.redirect("/login")
#         ]

#     def check_auth(self, token_from_client: Optional[str] = None):
#         """Verifica si hay un token válido."""
#         try:
#             if not token_from_client:
#                 self.is_logged = False
#                 return

#             payload = jwt.decode(token_from_client, SECRET_KEY, algorithms=[ALGORITHM])
#             username = payload.get("sub")
#             if username is None:
#                 self.is_logged = False
#                 return
                
#             self.is_logged = True
#             self.username = username
#             self.token = token_from_client  # Guardar el token en el estado
#         except JWTError:
#             self.is_logged = False
#             return rx.remove_local_storage("token")

# state/auth_state.py
import reflex as rx
from typing import Optional
from ..database import SessionLocal
from ..models.user import User

class AuthState(rx.State):
    """Estado de autenticación."""
    username: str = ""
    password: str = ""
    email: str = ""
    is_logged: bool = False
    error_message: str = ""

    def check_auth(self):
        """Verificar si el usuario está autenticado."""
        # Aquí puedes implementar la lógica para verificar el token/sesión
        pass

    def login(self):
        """Manejar el inicio de sesión."""
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=self.username).first()
            if user and User.verify_password(self.password, user.hashed_password):
                self.is_logged = True
                self.error_message = ""
                return rx.redirect("/dashboard")
            else:
                self.error_message = "Invalid username or password"
                self.is_logged = False

    def logout(self):
        """Cerrar sesión."""
        self.is_logged = False
        self.username = ""
        self.password = ""
        self.error_message = ""
        return rx.redirect("/login")

    def register(self):
        """Registrar un nuevo usuario."""
        if not all([self.username, self.email, self.password]):
            self.error_message = "All fields are required"
            return

        with SessionLocal() as session:
            if session.query(User).filter_by(username=self.username).first():
                self.error_message = "Username already exists"
                return
            
            if session.query(User).filter_by(email=self.email).first():
                self.error_message = "Email already exists"
                return

            hashed_password = User.get_password_hash(self.password)
            new_user = User(
                username=self.username,
                email=self.email,
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(new_user)
            try:
                session.commit()
                self.is_logged = True
                self.error_message = ""
                return rx.redirect("/dashboard")
            except Exception as e:
                session.rollback()
                self.error_message = "Error creating user"