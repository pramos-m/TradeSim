# tradesim/state/auth_state.py
import reflex as rx
from typing import List
from datetime import datetime, timedelta
from jose import jwt, JWTError
import os
from ..database import SessionLocal
from ..models.user import User
import logging
from decimal import Decimal

# Eliminar la línea: from ..state.auth_state import AuthState (YA NO ESTÁ AQUÍ)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class AuthState(rx.State):
    """Estado de autenticación - Corregido para login redirect"""
    # --- State Variables ---
    is_authenticated: bool = False
    auth_token: str = rx.Cookie(name="auth_token", max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    processed_token: bool = False
    loading: bool = False
    active_tab: str = "login"
    error_message: str = ""
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    account_balance: float = 0.0
    last_path: str = ""

    # --- Métodos de Token ---
    def create_access_token(self, user_id: int) -> str:
        # logger.info(f"Creando token para user_id: {user_id}") # Log reducido
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        data = {"sub": str(user_id), "exp": expire}
        try:
            encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creando token JWT: {e}")
            return ""

    def verify_token(self, token: str | None) -> int:
        if not token: return -1
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("sub"))
        except jwt.ExpiredSignatureError:
            # logger.warning("Verificando token: Token expirado.") # Log reducido
            return -1
        except (JWTError, ValueError, TypeError):
            # logger.error(f"Verificando token: Error de decodificación o formato: {e}") # Log reducido
            return -1

    # --- Variables Computadas ---
    @rx.var
    def is_on_auth_page(self) -> bool:
        current_page = self.router.page.path
        return current_page == "/login"

    # --- Event Handlers ---
    @rx.event
    async def on_load(self):
        """Maneja la carga inicial de página y la verificación de autenticación."""
        current_path = self.router.page.path
        if self.processed_token and self.last_path == current_path: return
        self.processed_token = True
        self.last_path = current_path
        if current_path == "/": return

        user_id = self.verify_token(self.auth_token)
        if user_id <= 0:
            if self.is_authenticated: logger.info("on_load: Desautenticando (token inválido/ausente).")
            self.is_authenticated = False; self.username = ""; self.email = ""; self.account_balance = 0.0
            if self.auth_token: self.auth_token = ""
            if current_path in ["/dashboard", "/profile"]: return rx.redirect("/login")
            return

        # Token VÁLIDO
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                needs_update = (
                    not self.is_authenticated or self.username != user.username or
                    abs(self.account_balance - float(user.account_balance if user.account_balance is not None else 0.0)) > 0.001
                )
                if needs_update:
                    self.username = user.username; self.email = user.email
                    self.account_balance = float(user.account_balance if user.account_balance is not None else 0.0)
                    self.is_authenticated = True
                    logger.info(f"on_load: Estado actualizado -> user: {self.username}, balance: {self.account_balance:.2f}, auth: {self.is_authenticated}")
                if current_path == "/login": return rx.redirect("/dashboard")
            else: # Token válido pero user no existe
                logger.warning(f"on_load: Usuario ID {user_id} no encontrado. Desautenticando.")
                self.is_authenticated = False; self.username = ""; self.email = ""; self.account_balance = 0.0; self.auth_token = ""
                if current_path in ["/dashboard", "/profile"]: return rx.redirect("/login")
        except Exception as e:
            logger.error(f"on_load: EXCEPCIÓN al buscar usuario ID {user_id}: {e}", exc_info=True)
            self.is_authenticated = False; self.account_balance = 0.0; self.auth_token = ""
            if current_path in ["/dashboard", "/profile"]: return rx.redirect("/login")
        finally:
            if db and db.is_active: db.close()

    @rx.event
    async def login(self):
        """Procesa el intento de inicio de sesión. SIN YIELD INICIAL, USA CALL_SCRIPT."""
        # logger.info(f"Intento de login para email: {self.email}") # Log reducido
        self.error_message = ""; self.loading = True

        if not self.email or not self.password:
            self.error_message = "Por favor complete todos los campos"; self.loading = False; return

        db = None
        try:
            db = SessionLocal()
            user = db.query(User).filter(User.email.ilike(self.email)).first()
            if not user or not user.verify_password(self.password):
                self.error_message = "Email o contraseña incorrectos"; self.loading = False; return

            # Login Exitoso
            logger.info(f"Login exitoso para usuario: {user.username} (ID: {user.id})")
            self.is_authenticated = True; self.username = user.username; self.email = user.email
            self.account_balance = float(user.account_balance) if user.account_balance is not None else 0.0
            # logger.info(f"Balance cargado: {self.account_balance:.2f}") # Log reducido

            token = self.create_access_token(user.id)
            if not token:
                logger.error("Login fallido: No se pudo crear el token."); self.error_message = "Error interno al generar token."; self.loading = False; return
            self.auth_token = token

            self.last_path = "/dashboard"; self.processed_token = True; self.loading = False
            logger.info("Login finalizado. Intentando redirect vía script a /dashboard...")
            return rx.call_script("window.location.href = '/dashboard';")

        except Exception as e:
            logger.error(f"Login fallido: Excepción inesperada: {e}", exc_info=True)
            self.error_message = f"Error inesperado durante el login."; self.loading = False
        finally:
            if db and db.is_active: db.close()

    @rx.event
    async def register(self):
        """Procesa el intento de registro. SIN YIELD INICIAL, USA CALL_SCRIPT."""
        # logger.info(f"Intento de registro para username: {self.username}, email: {self.email}") # Log reducido
        self.error_message = ""; self.loading = True

        if not self.username or not self.email or not self.password:
            self.error_message = "Por favor complete todos los campos"; self.loading = False; return
        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden"; self.loading = False; return

        db = None
        try:
            db = SessionLocal()
            existing_user = db.query(User).filter( (User.email.ilike(self.email)) | (User.username.ilike(self.username)) ).first()
            if existing_user:
                self.error_message = "Usuario o email ya están registrados"; self.loading = False; return

            logger.info("Creando nuevo usuario...")
            new_user = User(username=self.username.strip(), email=self.email.strip().lower())
            new_user.set_password(self.password)
            db.add(new_user); db.commit(); db.refresh(new_user)
            logger.info(f"Usuario creado: {new_user.username} (ID: {new_user.id}), Balance: {new_user.account_balance}")

            self.is_authenticated = True; self.username = new_user.username; self.email = new_user.email
            self.account_balance = float(new_user.account_balance) if new_user.account_balance is not None else 0.0

            token = self.create_access_token(new_user.id)
            if not token:
                 logger.error("Registro fallido post-creación: No se pudo crear el token.")
                 self.error_message = "Error interno al generar token post-registro."; self.loading = False; return
            self.auth_token = token

            self.last_path = "/dashboard"; self.processed_token = True; self.loading = False
            logger.info("Registro exitoso. Intentando redirect vía script a /dashboard...")
            return rx.call_script("window.location.href = '/dashboard';")

        except Exception as e:
            logger.error(f"Registro fallido: Excepción inesperada: {e}", exc_info=True)
            if db and db.is_active:
                 try: db.rollback(); # logger.info("Rollback BBDD ok.")
                 except Exception as rb_err: logger.error(f"Error en Rollback BBDD: {rb_err}")
            self.error_message = f"Error inesperado durante el registro."; self.loading = False
        finally:
            if db and db.is_active: db.close()

    @rx.event
    def logout(self):
        """Procesa el logout."""
        self.is_authenticated = False; self.username = ""; self.email = ""; self.password = ""
        self.confirm_password = ""; self.account_balance = 0.0; self.auth_token = ""
        self.processed_token = True; self.last_path = "/"
        return rx.call_script("window.location.href = '/';")

    # --- Setters Simples ---
    def set_active_tab(self, tab: str): self.active_tab = tab; self.error_message = ""
    def set_username(self, username: str): self.username = username
    def set_email(self, email: str): self.email = email
    def set_password(self, password: str): self.password = password
    def set_confirm_password(self, confirm_password: str): self.confirm_password = confirm_password