# state/profile_state.py
import reflex as rx
import base64
from ..database import SessionLocal
from ..controller.user import (
    update_profile_picture, 
    get_user_profile_picture, 
    get_user_by_username, 
    get_user_by_email, 
    get_user_by_id
)
from ..state.auth_state import AuthState, SECRET_KEY, ALGORITHM
from jose import jwt

class ProfileState(rx.State):
    # Variables de perfil
    profile_picture: str = ""
    
    # Variables de edición
    editing: bool = False
    temp_username: str = ""
    temp_email: str = ""
    temp_password: str = ""
    current_password: str = ""
    confirm_password: str = ""
    edit_error: str = ""
    
    @rx.event
    def open_file_picker(self):
        """Trigger hidden file input."""
        print("Intentando abrir selector de archivos...")
        return rx.call_script(
            'document.getElementById("profile_picture_input").click()'
        )
    
    @rx.event
    def handle_file_upload(self, file: str):
        """Handle file upload for profile picture."""
        try:
            print(f"Archivo recibido: {file[:30]}...")
            
            # Para archivos de entrada básicos, file será un string codificado en base64
            if not file or not file.startswith("data:"):
                print("Formato de archivo no válido")
                return

            # Extraer tipo y datos
            data_split = file.split(";base64,")
            if len(data_split) != 2:
                print("No se pudo separar tipo y datos")
                return
                
            file_type = data_split[0].replace("data:", "")
            file_base64 = data_split[1]
            
            print(f"Tipo de archivo: {file_type}")
            
            # Convertir base64 a bytes
            file_bytes = base64.b64decode(file_base64)
            
            # Obtener el token y verificarlo
            try:
                # Usar directamente el token de AuthState
                token = AuthState.auth_token
                if token:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = int(payload.get("sub"))
                    
                    if user_id > 0:
                        db = SessionLocal()
                        try:
                            user = get_user_by_id(db, user_id)
                            if user:
                                print(f"Usuario encontrado con ID: {user.id}")
                                update_profile_picture(db, user.id, file_bytes, file_type)
                                print("Imagen de perfil actualizada en la base de datos")
                                # Mostrar la imagen en la UI
                                self.profile_picture = file
                                print("Imagen de perfil actualizada en la UI")
                        finally:
                            db.close()
            except Exception as inner_e:
                print(f"Error accessing user from token: {inner_e}")
                
        except Exception as e:
            print(f"Error uploading profile picture: {e}")
   
    @rx.event
    def load_profile(self):
        """Load user profile data including profile picture."""
        try:
            print("Cargando perfil...")
            
            # Cargar username y email directamente de AuthState
            self.temp_username = AuthState.username
            self.temp_email = AuthState.email
            
            print(f"Username cargado: {AuthState.username}")
            print(f"Email cargado: {AuthState.email}")
            
            token = AuthState.auth_token
            if token:
                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                    user_id = int(payload.get("sub"))
                    
                    if user_id > 0:
                        db = SessionLocal()
                        try:
                            user = get_user_by_id(db, user_id)
                            if user:
                                print(f"Usuario encontrado: {user.id}")
                                
                                # Obtener la imagen de perfil y el tipo
                                picture_data, picture_type = get_user_profile_picture(db, user.id)
                                
                                # Si hay una imagen, convertirla a base64 para mostrarla
                                if picture_data and picture_type:
                                    print("Imagen de perfil encontrada")
                                    base64_image = base64.b64encode(picture_data).decode("utf-8")
                                    self.profile_picture = f"data:{picture_type};base64,{base64_image}"
                                else:
                                    print("No se encontró imagen de perfil")
                        finally:
                            db.close()
                except Exception as jwt_e:
                    print(f"Error decoding token: {jwt_e}")
            
        except Exception as e:
            print(f"Error loading profile: {e}")
            
    @rx.event
    def edit_profile(self):
        """Toggle edit profile mode."""
        if not self.editing:
            print("Iniciando edición de perfil")
            # Si empezamos a editar, inicializar campos temporales
            self.temp_username = AuthState.username
            self.temp_email = AuthState.email
            self.temp_password = ""
            self.current_password = ""
            self.confirm_password = ""
            self.edit_error = ""
            self.editing = True
        else:
            # Si ya estábamos editando, es un intento de guardar
            print("Guardando cambios de perfil")
            self._save_profile_changes()
    
    @rx.event
    def cancel_edit(self):
        """Cancel profile editing."""
        print("Cancelando edición de perfil")
        self.editing = False
        self.edit_error = ""
    
    @rx.event
    def _save_profile_changes(self):
        """Save profile changes."""
        # Validar campos
        if self.temp_password and self.temp_password != self.confirm_password:
            self.edit_error = "Las contraseñas no coinciden"
            return
            
        try:
            # Obtener usuario actual
            token = AuthState.auth_token
            if token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                user_id = int(payload.get("sub"))
                
                if user_id > 0:
                    db = SessionLocal()
                    try:
                        user = get_user_by_id(db, user_id)
                        if user:
                            # Verificar contraseña actual si se quiere cambiar algo
                            if not user.verify_password(self.current_password):
                                self.edit_error = "Contraseña actual incorrecta"
                                return
                                
                            # Actualizar username si ha cambiado
                            if self.temp_username != AuthState.username:
                                # Verificar que el nuevo username no esté en uso
                                existing = get_user_by_username(db, self.temp_username)
                                if existing and existing.id != user.id:
                                    self.edit_error = "Nombre de usuario ya está en uso"
                                    return
                                user.username = self.temp_username
                                # Actualizar AuthState
                                AuthState.username = self.temp_username
                            
                            # Actualizar email si ha cambiado
                            if self.temp_email != AuthState.email:
                                # Verificar que el nuevo email no esté en uso
                                existing = get_user_by_email(db, self.temp_email)
                                if existing and existing.id != user.id:
                                    self.edit_error = "Email ya está en uso"
                                    return
                                user.email = self.temp_email
                                # Actualizar AuthState
                                AuthState.email = self.temp_email
                            
                            # Actualizar contraseña si se ha introducido una nueva
                            if self.temp_password:
                                user.set_password(self.temp_password)
                                
                            # Guardar cambios en la base de datos
                            db.commit()
                            
                            # Resetear el modo de edición
                            self.editing = False
                            self.edit_error = ""
                            
                            # Mostrar mensaje de éxito
                            return rx.window_alert("Perfil actualizado con éxito!")
                    finally:
                        db.close()
        except Exception as e:
            self.edit_error = f"Error: {str(e)}"
            print(f"Error saving profile: {e}")
    
    # Setters para campos temporales
    def set_temp_username(self, username: str) -> None:
        """Set temporary username."""
        self.temp_username = username
        
    def set_temp_email(self, email: str) -> None:
        """Set temporary email."""
        self.temp_email = email
        
    def set_temp_password(self, password: str) -> None:
        """Set temporary password."""
        self.temp_password = password
        
    def set_current_password(self, password: str) -> None:
        """Set current password."""
        self.current_password = password
        
    def set_confirm_password(self, password: str) -> None:
        """Set confirm password."""
        self.confirm_password = password