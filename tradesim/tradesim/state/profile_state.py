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

class ProfileState(AuthState):
    # Variables de perfil
    profile_picture: str = ""
    
    # Variables de edición
    editing: bool = False
    temp_username: str = ""
    temp_email: str = ""
    temp_password: str = ""
    current_password: str = ""
    profile_confirm_password: str = ""
    edit_error: str = ""
    
    @rx.var
    def is_editing(self) -> bool:
        return self.editing
        
    @rx.event
    def open_file_picker(self):
        print("Intentando abrir selector de archivos...")
        return rx.call_script(
            'document.getElementById("profile_picture_input").click()'
        )
    
    @rx.event
    def handle_file_upload(self, file: str):
        try:
            print(f"Archivo recibido: {file[:30]}...")
            if not file or not isinstance(file, str) or not file.startswith("data:"):
                print("Formato de archivo no válido")
                return

            data_split = file.split(";base64,")
            if len(data_split) != 2:
                print("No se pudo separar tipo y datos")
                return
                
            file_type = data_split[0].replace("data:", "")
            file_base64 = data_split[1]
            
            print(f"Tipo de archivo: {file_type}")
            
            file_bytes = base64.b64decode(file_base64)
            
            user_id = self._get_user_id()
            
            if user_id > 0:
                db = SessionLocal()
                try:
                    user = get_user_by_id(db, user_id)
                    if user:
                        print(f"Usuario encontrado con ID: {user.id}")
                        update_profile_picture(db, user.id, file_bytes, file_type)
                        print("Imagen de perfil actualizada en la base de datos")
                        self.profile_picture = file
                        print("Imagen de perfil actualizada en la UI")
                finally:
                    db.close()
                
        except Exception as e:
            print(f"Error uploading profile picture: {e}")

    # Changed from @rx.var to a regular method to avoid the confusion
    def _get_user_id(self) -> int:
        try:
            token = str(self.auth_token or "")
            if token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return int(payload.get("sub", -1))
        except Exception as e:
            print(f"Error obteniendo user_id: {e}")
        return -1

    @rx.event
    def load_profile(self):
        try:
            print("Cargando perfil...")
            user_id = self._get_user_id()
            if user_id > 0:
                db = SessionLocal()
                try:
                    user = get_user_by_id(db, user_id)
                    if user:
                        print(f"Usuario encontrado: {user.id}")
                        # Usamos las variables heredadas de AuthState
                        self.username = user.username
                        self.email = user.email
                        self.temp_username = user.username
                        self.temp_email = user.email
                        print(f"Username cargado: {self.temp_username}")
                        print(f"Email cargado: {self.temp_email}")
                        
                        picture_data, picture_type = get_user_profile_picture(db, user.id)
                        if picture_data and picture_type:
                            print("Imagen de perfil encontrada")
                            base64_image = base64.b64encode(picture_data).decode("utf-8")
                            self.profile_picture = f"data:{picture_type};base64,{base64_image}"
                        else:
                            print("No se encontró imagen de perfil")
                finally:
                    db.close()
        except Exception as e:
            print(f"Error loading profile: {e}")
    
    @rx.event
    def edit_profile(self):
        if not self.is_editing:
            print("Iniciando edición de perfil")
            user_id = self._get_user_id()
            if user_id > 0:
                db = SessionLocal()
                try:
                    user = get_user_by_id(db, user_id)
                    if user:
                        self.temp_username = user.username
                        self.temp_email = user.email
                        print(f"Editando perfil de {self.temp_username} ({self.temp_email})")
                finally:
                    db.close()
            self.temp_password = ""
            self.current_password = ""
            self.profile_confirm_password = ""
            self.edit_error = ""
            self.editing = True
    
    @rx.event
    def cancel_edit(self):
        print("Cancelando edición de perfil")
        self.editing = False
        self.edit_error = ""
    
    @rx.event
    def save_profile_changes(self):
        try:
            # Basic validations
            if self.temp_password != self.profile_confirm_password:
                self.edit_error = "Las contraseñas no coinciden"
                return
            if not self.current_password:
                self.edit_error = "La contraseña actual es obligatoria"
                return

            user_id = self._get_user_id()
            if user_id <= 0:
                self.edit_error = "No se pudo obtener el ID del usuario"
                return

            db = SessionLocal()
            try:
                user = get_user_by_id(db, user_id)
                if not user:
                    self.edit_error = "No se encontró el usuario"
                    return

                # Verify current password
                if not user.verify_password(self.current_password):
                    self.edit_error = "Contraseña actual incorrecta"
                    return

                # Update username if it has changed
                if self.temp_username != user.username:
                    existing_username = get_user_by_username(db, self.temp_username)
                    if existing_username and existing_username.id != user.id:
                        self.edit_error = "Nombre de usuario ya está en uso"
                        return
                    user.username = self.temp_username
                    self.username = self.temp_username  # Update state

                # Update email if it has changed
                if self.temp_email != user.email:
                    existing_email = get_user_by_email(db, self.temp_email)
                    if existing_email and existing_email.id != user.id:
                        self.edit_error = "Email ya está en uso"
                        return
                    user.email = self.temp_email
                    self.email = self.temp_email  # Update state

                # Update password if provided
                if self.temp_password:
                    user.set_password(self.temp_password)

                db.commit()
                self.editing = False
                self.edit_error = ""
                return rx.window_alert("Perfil actualizado con éxito!")

            except Exception as e:
                db.rollback()  # Rollback in case of error
                self.edit_error = f"Error: {str(e)}"
                print(f"Error saving profile: {e}")
            finally:
                db.close()

        except Exception as e:
            self.edit_error = f"Unexpected error: {str(e)}"
            print(f"Unexpected error: {e}")

    def set_temp_username(self, username: str) -> None:
        self.temp_username = username
        
    def set_temp_email(self, email: str) -> None:
        self.temp_email = email
        
    def set_temp_password(self, password: str) -> None:
        self.temp_password = password
        
    def set_current_password(self, password: str) -> None:
        self.current_password = password
        
    def set_confirm_password(self, password: str) -> None:
        self.profile_confirm_password = password

    def set_edit_error(self, error: str) -> None:
        self.edit_error = error