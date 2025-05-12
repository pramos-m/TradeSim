# import reflex as rx
# import base64
# from ..database import SessionLocal
# from ..controller.user import (
#     update_profile_picture, 
#     get_user_profile_picture, 
#     get_user_by_username, 
#     get_user_by_email, 
#     get_user_by_id
# )
# from ..state.auth_state import AuthState, SECRET_KEY, ALGORITHM
# from jose import jwt

# class ProfileState(AuthState):
#     # Variables de perfil
#     profile_picture: str = ""
    
#     # Variables de edición
#     editing: bool = False
#     temp_username: str = ""
#     temp_email: str = ""
#     temp_password: str = ""
#     current_password: str = ""
#     profile_confirm_password: str = ""
#     edit_error: str = ""
    
#     @rx.var
#     def is_editing(self) -> bool:
#         return self.editing
    
#     @rx.event
#     def handle_file_upload(self, event_data):
#         """Handle file upload from the custom event."""
#         try:
#             if not event_data or "detail" not in event_data:
#                 return

#             detail = event_data["detail"]
#             file_content = detail.get("content")
#             file_type = detail.get("type")
            
#             if not file_content or not file_type:
#                 self.edit_error = "Error: información de archivo incompleta"
#                 return
                
#             # Extraer la parte de base64 de la cadena dataURL
#             # El formato es data:image/jpeg;base64,<datos>
#             base64_content = file_content.split(',')[1] if ',' in file_content else file_content
            
#             # Decode base64 content
#             file_bytes = base64.b64decode(base64_content)
            
#             user_id = self._get_user_id()
#             if user_id > 0:
#                 db = SessionLocal()
#                 try:
#                     update_profile_picture(db, user_id, file_bytes, file_type)
#                     # Almacenar la URL de datos completa para mostrar la imagen
#                     self.profile_picture = file_content
#                     return rx.window_alert("Foto actualizada con éxito!")
#                 finally:
#                     db.close()
#         except Exception as e:
#             print(f"Error uploading profile picture: {e}")
#             self.edit_error = f"Error al subir la imagen: {str(e)}"

#     def _get_user_id(self) -> int:
#         try:
#             token = str(self.auth_token or "")
#             if token:
#                 payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#                 return int(payload.get("sub", -1))
#         except Exception as e:
#             print(f"Error obteniendo user_id: {e}")
#         return -1

#     @rx.event
#     def load_profile(self):
#         try:
#             user_id = self._get_user_id()
#             if user_id > 0:
#                 db = SessionLocal()
#                 try:
#                     user = get_user_by_id(db, user_id)
#                     if user:
#                         self.username = user.username
#                         self.email = user.email
#                         self.temp_username = user.username
#                         self.temp_email = user.email
                        
#                         # Recuperar la imagen de perfil
#                         picture_data, picture_type = get_user_profile_picture(db, user_id)
#                         if picture_data and picture_type:
#                             # Convertir bytes a base64 y crear una URL de datos
#                             base64_image = base64.b64encode(picture_data).decode("utf-8")
#                             self.profile_picture = f"data:{picture_type};base64,{base64_image}"
#                             print(f"Loaded profile picture: {len(self.profile_picture)} chars")
#                         else:
#                             self.profile_picture = ""
#                             print("No profile picture found")
#                 finally:
#                     db.close()
#         except Exception as e:
#             print(f"Error loading profile: {e}")
#             import traceback
#             traceback.print_exc()

#     @rx.event
#     def edit_profile(self):
#         self.editing = True
    
#     @rx.event
#     def cancel_edit(self):
#         self.editing = False
#         self.edit_error = ""
    
#     @rx.event
#     def save_profile_changes(self):
#         try:
#             if self.temp_password != self.profile_confirm_password:
#                 self.edit_error = "Las contraseñas no coinciden"
#                 return
#             if not self.current_password:
#                 self.edit_error = "La contraseña actual es obligatoria"
#                 return

#             user_id = self._get_user_id()
#             if user_id <= 0:
#                 self.edit_error = "No se pudo obtener el ID del usuario"
#                 return

#             db = SessionLocal()
#             try:
#                 user = get_user_by_id(db, user_id)
#                 if not user or not user.verify_password(self.current_password):
#                     self.edit_error = "Contraseña actual incorrecta"
#                     return

#                 if self.temp_username and self.temp_username != user.username:
#                     existing_username = get_user_by_username(db, self.temp_username)
#                     if existing_username:
#                         self.edit_error = "Nombre de usuario ya está en uso"
#                         return
#                     user.username = self.temp_username

#                 if self.temp_email and self.temp_email != user.email:
#                     existing_email = get_user_by_email(db, self.temp_email)
#                     if existing_email:
#                         self.edit_error = "Email ya está en uso"
#                         return
#                     user.email = self.temp_email

#                 if self.temp_password:
#                     user.set_password(self.temp_password)

#                 db.commit()
#                 self.editing = False
#                 self.edit_error = ""
#                 return rx.window_alert("Perfil actualizado con éxito!")
#             finally:
#                 db.close()
#         except Exception as e:
#             self.edit_error = f"Unexpected error: {str(e)}"

#     def set_temp_username(self, username: str) -> None:
#         self.temp_username = username
        
#     def set_temp_email(self, email: str) -> None:
#         self.temp_email = email
        
#     def set_temp_password(self, password: str) -> None:
#         self.temp_password = password
        
#     def set_current_password(self, password: str) -> None:
#         self.current_password = password
        
#     def set_confirm_password(self, password: str) -> None:
#         self.profile_confirm_password = password

#     def set_edit_error(self, error: str) -> None:
#         self.edit_error = error


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
    def handle_file_upload(self, event_data):
        """Handle file upload from the custom event."""
        try:
            if not event_data or "detail" not in event_data:
                print("Error: event_data or detail is missing")
                return

            detail = event_data["detail"]
            file_content = detail.get("content")
            file_type = detail.get("type")
            
            if not file_content or not file_type:
                self.edit_error = "Error: información de archivo incompleta"
                print("Error: file_content or file_type is missing")
                return
            
            print(f"File content received: {file_content[:50]}...")  # Depuración
            print(f"File type received: {file_type}")  # Depuración
            
            # Extraer la parte de base64 de la cadena dataURL
            base64_content = file_content.split(',')[1] if ',' in file_content else file_content
            
            # Decode base64 content
            file_bytes = base64.b64decode(base64_content)
            
            user_id = self._get_user_id()
            if user_id > 0:
                db = SessionLocal()
                try:
                    update_profile_picture(db, user_id, file_bytes, file_type)
                    # Almacenar la URL de datos completa para mostrar la imagen
                    self.profile_picture = file_content
                    print("Profile picture updated successfully!")  # Depuración
                    return rx.window_alert("Foto actualizada con éxito!")
                finally:
                    db.close()
        except Exception as e:
            print(f"Error uploading profile picture: {e}")
            self.edit_error = f"Error al subir la imagen: {str(e)}"
    
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
            user_id = self._get_user_id()
            if user_id > 0:
                db = SessionLocal()
                try:
                    user = get_user_by_id(db, user_id)
                    if user:
                        self.username = user.username
                        self.email = user.email
                        self.temp_username = user.username
                        self.temp_email = user.email
                        
                        # Recuperar la imagen de perfil
                        picture_data, picture_type = get_user_profile_picture(db, user_id)
                        if picture_data and picture_type:
                            # Convertir bytes a base64 y crear una URL de datos
                            base64_image = base64.b64encode(picture_data).decode("utf-8")
                            self.profile_picture = f"data:{picture_type};base64,{base64_image}"
                            print(f"Loaded profile picture: {len(self.profile_picture)} chars")
                        else:
                            self.profile_picture = ""
                            print("No profile picture found")
                finally:
                    db.close()
        except Exception as e:
            print(f"Error loading profile: {e}")
            import traceback
            traceback.print_exc()

    @rx.event
    def edit_profile(self):
        self.editing = True
    
    @rx.event
    def cancel_edit(self):
        self.editing = False
        self.edit_error = ""
    
    @rx.event
    def save_profile_changes(self):
        try:
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
                if not user or not user.verify_password(self.current_password):
                    self.edit_error = "Contraseña actual incorrecta"
                    return

                if self.temp_username and self.temp_username != user.username:
                    existing_username = get_user_by_username(db, self.temp_username)
                    if existing_username:
                        self.edit_error = "Nombre de usuario ya está en uso"
                        return
                    user.username = self.temp_username

                if self.temp_email and self.temp_email != user.email:
                    existing_email = get_user_by_email(db, self.temp_email)
                    if existing_email:
                        self.edit_error = "Email ya está en uso"
                        return
                    user.email = self.temp_email

                if self.temp_password:
                    user.set_password(self.temp_password)

                db.commit()
                self.editing = False
                self.edit_error = ""
                return rx.window_alert("Perfil actualizado con éxito!")
            finally:
                db.close()
        except Exception as e:
            self.edit_error = f"Unexpected error: {str(e)}"

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