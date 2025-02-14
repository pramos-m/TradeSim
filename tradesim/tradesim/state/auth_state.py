import reflex as rx
from ..database import SessionLocal
from ..models.user import User

class AuthState(rx.State):
    """Estado de autenticación."""
    username: str = ""
    email: str = ""
    password: str = ""
    confirm_password: str = ""
    is_logged: bool = False
    error_message: str = ""
    active_tab: str = "register"

    def set_username(self, username: str):
        """Establecer nombre de usuario."""
        self.username = username
        self.error_message = ""

    def set_email(self, email: str):
        """Establecer email."""
        self.email = email
        self.error_message = ""

    def set_password(self, password: str):
        """Establecer contraseña."""
        self.password = password
        self.error_message = ""

    def set_confirm_password(self, password: str):
        """Establecer confirmación de contraseña."""
        self.confirm_password = password
        self.error_message = ""

    def set_active_tab(self, tab: str):
        """Cambiar entre login y registro."""
        self.active_tab = tab

    def login(self):
        """Manejar el inicio de sesión."""
        with SessionLocal() as session:
            user = session.query(User).filter_by(username=self.username).first()
            if user and User.verify_password(self.password, user.hashed_password):
                self.is_logged = True
                self.error_message = ""
                return rx.redirect("/dashboard")
            else:
                self.error_message = "Usuario o contraseña inválidos"
                self.is_logged = False

    def logout(self):
        """Cerrar sesión."""
        self.is_logged = False
        self.username = ""
        self.email = ""
        self.password = ""
        self.confirm_password = ""
        self.error_message = ""
        return rx.redirect("/login")

    def register(self):
        """Registrar un nuevo usuario."""
        if not all([self.username, self.email, self.password, self.confirm_password]):
            self.error_message = "Todos los campos son obligatorios"
            return

        if self.password != self.confirm_password:
            self.error_message = "Las contraseñas no coinciden"
            return

        with SessionLocal() as session:
            if session.query(User).filter_by(username=self.username).first():
                self.error_message = "El nombre de usuario ya existe"
                return
            
            if session.query(User).filter_by(email=self.email).first():
                self.error_message = "El email ya está registrado"
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
            except Exception:
                session.rollback()
                self.error_message = "Error al crear usuario"
