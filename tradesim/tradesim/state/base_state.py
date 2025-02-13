import reflex as rx
from typing import Optional
from ..models.user import User
from ..database import SessionLocal
from jose import jwt, JWTError
from datetime import datetime, timedelta

# Constantes para JWT
SECRET_KEY = "your-secret-key-here"  # En producción, usar variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class State(rx.State):
    """Estado base que incluye autenticación y otras funcionalidades."""
    
    # Variables de estado para autenticación
    username: str = ""
    password: str = ""
    email: str = ""
    is_logged: bool = False
    error_message: Optional[str] = None
    
    # Variables de estado originales
    count: int = 0
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def login(self):
        """Procesa el inicio de sesión."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.username == self.username).first()
            
            # Verificar credenciales
            if not user or not User.verify_password(self.password, user.hashed_password):
                self.error_message = "Usuario o contraseña incorrectos"
                return
            
            # Crear token y actualizar estado
            token = self.create_access_token({"sub": user.username})
            self.is_logged = True
            self.error_message = None
            
            # Guardar token y redirigir
            rx.window_localStorage.set_item("token", token)
            return rx.redirect("/dashboard")
    
    def register(self):
        """Registra un nuevo usuario."""
        with SessionLocal() as db:
            # Verificar si el usuario ya existe
            existing_user = db.query(User).filter(
                (User.username == self.username) | (User.email == self.email)
            ).first()
            
            if existing_user:
                self.error_message = "Usuario o email ya registrado"
                return
            
            # Crear nuevo usuario
            new_user = User(
                username=self.username,
                email=self.email,
                hashed_password=User.get_password_hash(self.password)
            )
            
            db.add(new_user)
            db.commit()
            
            # Iniciar sesión automáticamente
            self.login()
    
    def logout(self):
        """Cierra la sesión del usuario."""
        self.is_logged = False
        self.username = ""
        self.password = ""
        self.email = ""
        return rx.window_localStorage.remove_item("token")
    
    def check_auth(self):
        """Verifica si hay un token válido."""
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
    
    # Métodos originales del contador
    def increment(self):
        """Incrementa el contador."""
        self.count += 1
    
    def decrement(self):
        """Decrementa el contador."""
        self.count -= 1
