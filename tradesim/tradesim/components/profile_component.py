# profile_component.py (CORREGIDO Y COMPLETO)
import reflex as rx
import re
import base64
from typing import List, Optional
import asyncio

# Imports de BD, Controladores, Estado, etc.
from ..database import SessionLocal
from ..controller.user import (
    update_profile_picture, get_user_profile_picture, get_user_by_username,
    get_user_by_email, get_user_by_id
)
from ..state.auth_state import AuthState, SECRET_KEY, ALGORITHM # AuthState ya tiene profile_image_url
from jose import jwt, JWTError

# --- Constants ---
DEFAULT_AVATAR = "/default_avatar.png"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPLOAD_ID = "avatar-upload"

# Colores y estilos específicos del diseño
PROFILE_CARD_BG = "#ededed"
BUTTON_BLUE_BG = "rgb(86, 128, 255)"
BUTTON_BLUE_HOVER_BG = "rgb(70, 110, 230)"
BUTTON_RED_BG = "#c62828"
BUTTON_RED_HOVER_BG = "#b71c1c"
TEXT_BLACK = "black"
TEXT_GRAY_700 = "gray.700"
TEXT_GRAY_500 = "gray.500"
BORDER_GRAY_300 = "gray.300"
ICON_BLUE = "blue.500"

IMAGE_SIZE = "200px"
IMAGE_BORDER_RADIUS = "20px"

# --- Estado del Componente (ProfileState) ---
class ProfileState(AuthState):
    """Gestiona el estado y la lógica del componente de perfil."""
    is_editing: bool = False
    temp_username: str = ""
    temp_email: str = ""
    new_password: str = ""
    confirm_new_password: str = "" # <--- CORREGIDO: Renombrado de confirm_password
    current_password: str = ""
    
    username_error: str = ""
    email_error: str = ""
    password_error: str = ""
    general_message: str = ""
    message_color: str = "green"

    selected_files_ref: List[rx.UploadFile] = []

    # Setter para confirm_new_password  <--- NUEVO: Setter para la variable renombrada
    def set_confirm_new_password(self, password: str):
        self.confirm_new_password = password

    @rx.var
    def password_mismatch(self) -> bool:
        return self.new_password != "" and self.new_password != self.confirm_new_password # <--- CORREGIDO

    @rx.var
    def invalid_email(self) -> bool:
        return self.is_editing and self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email)

    @rx.var
    def username_empty(self) -> bool:
        return self.is_editing and not self.temp_username.strip()

    @rx.var
    def can_save(self) -> bool:
        mismatch = self.new_password != "" and self.new_password != self.confirm_new_password # <--- CORREGIDO
        invalid_mail = self.is_editing and self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email)
        empty_user = self.is_editing and not self.temp_username.strip()
        return self.is_editing and not mismatch and not invalid_mail and not empty_user

    def _get_user_id(self) -> int:
        try:
            token = str(self.auth_token or "")
            if not token: return -1
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("sub", -1))
        except JWTError:
            print(f"Error decodificando token JWT")
            return -1
        except Exception as e:
            print(f"Error obteniendo user_id: {e}")
            return -1
            
    def _reset_errors(self):
        self.username_error = ""
        self.email_error = ""
        self.password_error = ""
        self.general_message = ""

    def _reset_temp_fields(self):
        self.temp_username = self.username
        self.temp_email = self.email
        self.new_password = ""
        self.confirm_new_password = "" # <--- CORREGIDO
        self.current_password = ""
        self.selected_files_ref = []

    def load_user_data(self):
        user_id_to_load = self._get_user_id()
        print(f"Attempting to load data for user ID: {user_id_to_load}")
        if user_id_to_load <= 0:
            self.username = "" # Heredado de AuthState
            self.email = ""    # Heredado de AuthState
            self.profile_image_url = DEFAULT_AVATAR # Heredado de AuthState
            self._reset_temp_fields()
            return

        db = None
        try:
            db = SessionLocal()
            user = get_user_by_id(db, user_id_to_load)
            if user:
                self.username = user.username
                self.email = user.email
                picture_data, picture_type = get_user_profile_picture(db, user.id)
                if picture_data and picture_type:
                    base64_image = base64.b64encode(picture_data).decode("utf-8")
                    self.profile_image_url = f"data:{picture_type};base64,{base64_image}"
                else:
                    self.profile_image_url = DEFAULT_AVATAR
            else:
                self.username = ""
                self.email = ""
                self.profile_image_url = DEFAULT_AVATAR
            
            self._reset_temp_fields()
            self.is_editing = False
            self._reset_errors()

        except Exception as e:
            print(f"Error loading profile data: {e}")
            import traceback
            traceback.print_exc()
            self.general_message = "Error al cargar el perfil."
            self.message_color = "red"
        finally:
            if db:
                db.close()
                print("Database session closed after loading data.")

    def start_editing(self):
        if not self.username and self._get_user_id() > 0 :
             self.load_user_data()

        if self.username :
            self.is_editing = True
            self._reset_errors()
            self.temp_username = self.username
            self.temp_email = self.email
            self.new_password = ""
            self.confirm_new_password = "" # <--- CORREGIDO
            self.current_password = ""
            self.selected_files_ref = []
            print("Modo edición activado")
        else:
            self.general_message = "No se han podido cargar los datos para editar."
            self.message_color = "red"

    def cancel_editing(self):
        self.is_editing = False
        self._reset_errors()
        self._reset_temp_fields()
        self.load_user_data() 
        return rx.clear_selected_files(UPLOAD_ID)

    async def handle_upload(self, files: List[rx.UploadFile]):
        if files:
            uploaded_file = files[0]
            print(f"Fitxer seleccionat: {uploaded_file.name}, Mida: {uploaded_file.size}")
            
            MAX_FILE_SIZE = 5 * 1024 * 1024
            VALID_MIME_TYPES = ["image/jpeg", "image/png", "image/gif"]

            if uploaded_file.size > MAX_FILE_SIZE:
                self.general_message = f"El fitxer és massa gran (max {MAX_FILE_SIZE / (1024*1024)}MB)."
                self.message_color = "red"
                self.selected_files_ref = []
                return rx.clear_selected_files(UPLOAD_ID)

            if uploaded_file.content_type not in VALID_MIME_TYPES:
                self.general_message = "Format d'imatge no vàlid (només JPG, PNG, GIF)."
                self.message_color = "red"
                self.selected_files_ref = []
                return rx.clear_selected_files(UPLOAD_ID)

            self.selected_files_ref = files
            self.general_message = ""
        else:
            self.selected_files_ref = []

    def _validate_form_on_save(self) -> bool:
        self._reset_errors()
        valid = True
        if not self.temp_username.strip():
            self.username_error = "El nom d'usuari no pot estar buit."
            valid = False
        
        if self.temp_email.strip() == "":
            self.email_error = "El correu electrònic no pot estar buit."
            valid = False
        elif not re.match(EMAIL_REGEX, self.temp_email):
            self.email_error = "Format de correu invàlid."
            valid = False

        if self.new_password.strip(): 
            if len(self.new_password) < 6:
                self.password_error += " La nova contrasenya ha de tenir almenys 6 caràcters."
                valid = False
            if self.new_password != self.confirm_new_password: # <--- CORREGIDO
                self.password_error += " Les noves contrasenyes no coincideixen."
                valid = False
            if not self.confirm_new_password.strip(): # <--- CORREGIDO
                 self.password_error += " Confirma la nova contrasenya."
                 valid = False
        
        if not self.current_password.strip():
            if self.password_error: self.password_error += " "
            self.password_error += "La contrasenya actual és obligatòria per desar canvis."
            valid = False
        
        if not valid and not self.general_message:
            self.general_message = "Si us plau, corregeix els errors."
            self.message_color = "red"
            
        return valid

    async def save_changes(self):
        if not self._validate_form_on_save():
            return

        user_id_to_save = self._get_user_id()
        if user_id_to_save <= 0:
            self.general_message = "Error: Sessió invàlida. Si us plau, torna a iniciar sessió."
            self.message_color = "red"
            return

        db = None
        try:
            print("Iniciant desat de canvis...")
            db = SessionLocal()
            user = get_user_by_id(db, user_id_to_save)

            if not user:
                self.general_message = "Error: Usuari no trobat."
                self.message_color = "red"
                return

            if not user.verify_password(self.current_password):
                self.password_error = "Contrasenya actual incorrecta."
                self.general_message = "La contrasenya actual no és correcta."
                self.message_color = "red"
                return

            if self.temp_username != user.username:
                existing_user_by_username = get_user_by_username(db, self.temp_username)
                if existing_user_by_username and existing_user_by_username.id != user.id:
                    self.username_error = "Aquest nom d'usuari ja està en ús."
                    self.general_message = "Si us plau, corregeix els errors."
                    self.message_color = "red"
                    return
                user.username = self.temp_username

            if self.temp_email != user.email:
                existing_user_by_email = get_user_by_email(db, self.temp_email)
                if existing_user_by_email and existing_user_by_email.id != user.id:
                    self.email_error = "Aquest correu electrònic ja està en ús."
                    self.general_message = "Si us plau, corregeix els errors."
                    self.message_color = "red"
                    return
                user.email = self.temp_email
            
            if self.new_password.strip():
                user.set_password(self.new_password)

            if self.selected_files_ref:
                file_to_upload = self.selected_files_ref[0]
                try:
                    image_data = await file_to_upload.read()
                    update_profile_picture(db, user.id, image_data, file_to_upload.content_type)
                    print(f"Imatge de perfil actualitzada: {file_to_upload.name}")
                except Exception as e:
                    print(f"Error processant la imatge pujada: {e}")
                    self.general_message = "Error al processar la imatge. Intenta-ho de nou."
                    self.message_color = "red"
                    db.rollback()
                    return

            db.commit()
            db.refresh(user)
            print("Canvis desats a la base de dades.")

            self.username = user.username # Actualiza el estado base
            self.email = user.email       # Actualiza el estado base

            self.is_editing = False
            self.general_message = "Perfil actualitzat amb èxit!"
            self.message_color = "green"
            self._reset_errors()
            
            yield self.load_user_data() 
            yield rx.clear_selected_files(UPLOAD_ID)

        except Exception as e:
            print(f"Error en save_changes: {e}")
            import traceback
            traceback.print_exc()
            if db: db.rollback()
            self.general_message = f"Error inesperat al guardar: {str(e)}"
            self.message_color = "red"
        finally:
            if db:
                db.close()
                print("Database session closed after save attempt.")

    def logout(self):
        print("Logging out...")
        # Llama al logout de AuthState que ya resetea sus campos y el token
        # y maneja la redirección.
        # super().logout() # AuthState.logout()
        
        # Reseteo adicional de campos específicos de ProfileState
        self.is_editing = False
        self._reset_errors()
        self._reset_temp_fields()
        # El profile_image_url también debería ser reseteado a DEFAULT_AVATAR
        # Esto ya lo hace el AuthState.logout() al limpiar self.username, etc.
        # Si AuthState.logout() no limpia profile_image_url, hazlo aquí explícitamente.
        # self.profile_image_url = DEFAULT_AVATAR 

        # Llama al logout del AuthState para limpiar el token y redirigir.
        # El método logout en AuthState ya maneja la redirección con rx.call_script.
        # Si prefieres rx.redirect aquí, asegúrate que no haya doble redirección.
        # Por ahora, confiamos en que AuthState.logout() hace la limpieza y redirección.
        return super().logout()


# --- Funciones UI Refactorizadas para el Nuevo Diseño ---

def profile_picture_card_content(state: ProfileState) -> rx.Component:
    upload_placeholder = rx.vstack(
        rx.icon(tag="image", color="gray.400", font_size="4xl"),
        rx.text("Afegir Foto", color=TEXT_GRAY_500, margin_top="2"),
        width=IMAGE_SIZE,
        height=IMAGE_SIZE,
        border="2px dashed",
        border_color=BORDER_GRAY_300,
        border_radius=IMAGE_BORDER_RADIUS,
        display="flex",
        justify_content="center",
        align_items="center",
        padding="4",
    )

    return rx.vstack(
        rx.heading(
            "FOTO DE PERFIL",
            size="4",
            font_weight="bold",
            margin_bottom="6",
            color=TEXT_BLACK,
            padding_top="2",
            align_self="flex-start"
        ),
        rx.upload(
            rx.cond( 
                state.is_editing & (rx.selected_files(UPLOAD_ID).length() > 0),
                rx.foreach(
                    rx.selected_files(UPLOAD_ID), 
                    lambda file: rx.image(
                        src=rx.get_upload_url(file),
                        width=IMAGE_SIZE,
                        height=IMAGE_SIZE,
                        border_radius=IMAGE_BORDER_RADIUS,
                        object_fit="cover",
                        border="3px solid", 
                        border_color="blue.400" 
                    )
                ),
                rx.cond(
                    state.profile_image_url != DEFAULT_AVATAR,
                    rx.image(
                        src=state.profile_image_url, # Usa la variable de estado para la URL
                        width=IMAGE_SIZE,
                        height=IMAGE_SIZE,
                        border_radius=IMAGE_BORDER_RADIUS,
                        object_fit="cover",
                        border=rx.cond(state.is_editing, f"3px dashed {BORDER_GRAY_300}", "3px solid transparent"), 
                        opacity=rx.cond(state.is_editing, 0.7, 1.0)
                    ),
                    upload_placeholder 
                )
            ),
            id=UPLOAD_ID,
            on_drop=ProfileState.handle_upload(rx.upload_files(upload_id=UPLOAD_ID)),
            accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"], "image/gif": [".gif"]},
            max_files=1,
            disabled=~state.is_editing,
            border="none", 
            padding=0, 
            cursor=rx.cond(state.is_editing, "pointer", "default"),
            display="inline-block", 
        ),
        rx.button(
            rx.hstack(
                rx.icon(tag="pencil", font_size="sm"),
                rx.text("Editar Foto"),
                spacing="2"
            ),
            width="100%",
            margin_top="16px", 
            color="white",
            background_color=BUTTON_BLUE_BG,
            border_radius="12px",
            _hover={"background_color": BUTTON_BLUE_HOVER_BG},
            padding_y="12px", 
            on_click=ProfileState.start_editing, 
        ),
        align_items="center",
        width="100%",
        spacing="3", # <--- ESTE ESPACIADO
    )

def _info_item(icon_name: str, label: str, value: rx.Var | str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(tag=icon_name, color=TEXT_BLACK, size=28), 
            rx.text(label, font_weight="bold", color=TEXT_BLACK, font_size="xl"), 
            spacing="3",
            align_items="center"
        ),
        rx.text(
            value,
            font_size="xl",
            color=TEXT_BLACK,
            margin_left="40px", 
            margin_top="-12px", 
            margin_bottom="18px",
            word_break="break-word", 
        ),
        align_items="start",
        width="100%"
    )

def display_view_card(state: ProfileState) -> rx.Component:
    return rx.vstack(
        _info_item(icon_name="user", label="NOMBRE:", value=state.username),
        _info_item(icon_name="mail", label="EMAIL:", value=state.email),
        # Para el último ítem, podríamos querer un margin_bottom más pequeño
        # Opción A: Modificar _info_item para aceptar un margin_bottom opcional
        # Opción B: Envolver el último _info_item en un box y controlar su margin_bottom
        # Opción C (más simple para probar): Ajustar el padding del vstack o el margin_top de los botones como ya hicimos.
        
        # Vamos a probar una ligera modificación en el último ítem directamente aquí
        # (esto es menos elegante que modificar _info_item, pero rápido para probar)
        rx.vstack(
            rx.hstack(
                rx.icon(tag="shield", color=TEXT_BLACK, size=28), 
                rx.text("CONTRASEÑA:", font_weight="bold", color=TEXT_BLACK, font_size="xl"), 
                spacing="3",
                align_items="center"
            ),
            rx.text(
                "************",
                font_size="xl",
                color=TEXT_BLACK,
                margin_left="40px", 
                margin_top="-12px", 
                # margin_bottom="18px", # <--- VALOR ORIGINAL EN _info_item
                margin_bottom="4px",   # <--- Prueba con un valor más pequeño
            ),
            align_items="start",
            width="100%"
        ),
        # spacing="2", # Espaciado entre los _info_item y el vstack modificado
        # El vstack de display_view_card podría necesitar un padding_bottom="0" si el último margin_bottom no es suficiente
        # o si su propio spacing añade espacio extra.
        align_items="start",
        width="100%",
        spacing="2" # Mantenemos el espaciado entre los items. El ajuste se hace en el margin_bottom del último.
    )


def _edit_field(
    state: ProfileState, # Necesario para acceder a las variables específicas
    icon_name: str,
    label: str,
    value_var: rx.Var, # La variable de estado como rx.Var (e.g., state.temp_username)
    on_change_method: callable,
    placeholder: str,
    error_var: Optional[rx.Var[str]] = None, # La variable de error como rx.Var (e.g., state.username_error)
    type: str = "text",
    # is_required: bool = True, # No se usa actualmente para lógica, solo informativo
) -> rx.Component:
    
    border_color_reactive = BORDER_GRAY_300 
    error_message_reactive = rx.fragment()

    if error_var is not None:
        border_color_reactive = rx.cond(error_var != "", "red.500", BORDER_GRAY_300)
        error_message_reactive = rx.cond(
            error_var != "",
            rx.text(error_var, color="red.500", font_size="sm", margin_top="1"),
            rx.fragment()
        )

    return rx.vstack(
        rx.hstack(
            rx.icon(tag=icon_name, color=ICON_BLUE),
            rx.text(label, font_weight="bold", color=TEXT_GRAY_700),
            width="100%",
            spacing="2",
        ),
        rx.input(
            value=value_var, # Pasar la variable de estado directamente
            on_change=on_change_method,
            placeholder=placeholder,
            type_=type,
            width="100%",
            border_radius="md",
            border="1px solid", 
            border_color=border_color_reactive, # Reactivo
            padding_x="3",
            padding_y="2",
            focus_border_color="blue.500",
            _hover={"border_color": "blue.400"},
        ),
        error_message_reactive, # Reactivo
        align_items="flex-start",
        width="100%",
        spacing="1",
    )

def edit_view_card(state: ProfileState) -> rx.Component:
    return rx.form.root(
        rx.vstack(
            rx.cond(
                state.general_message != "",
                rx.callout.root(
                    rx.callout.icon(rx.icon(tag=rx.cond(state.message_color == "red", "alert-triangle", "check-circle-2"))),
                    rx.callout.text(state.general_message),
                    color_scheme=state.message_color,
                    variant="soft",
                    margin_bottom="4",
                    width="100%",
                    role="alert",
                ),
                rx.fragment()
            ),
            _edit_field(state, "user", "NOMBRE:", state.temp_username, ProfileState.set_temp_username, "Nombre de usuario", error_var=state.username_error),
            _edit_field(state, "mail", "EMAIL:", state.temp_email, ProfileState.set_temp_email, "Email", error_var=state.email_error, type="email"),
            _edit_field(state, "lock", "CONTRASEÑA ACTUAL:", state.current_password, ProfileState.set_current_password, "Requerida para guardar cambios", error_var=state.password_error, type="password"),
            _edit_field(state, "key", "NUEVA CONTRASEÑA:", state.new_password, ProfileState.set_new_password, "Dejar en blanco para no cambiar", error_var=state.password_error, type="password"), # is_required=False es implícito
            _edit_field(state, "check", "CONFIRMAR CONTRASEÑA:", state.confirm_new_password, ProfileState.set_confirm_new_password, "Confirmar nueva contraseña", error_var=state.password_error, type="password"), # <--- CORREGIDO: value_var y on_change_method
            
            rx.hstack(
                rx.button(
                    rx.hstack(rx.icon(tag="check", font_size="sm"), rx.text("Guardar Cambios"), spacing="2"),
                    color="white",
                    background_color=BUTTON_BLUE_BG,
                    _hover={"background_color": BUTTON_BLUE_HOVER_BG},
                    border_radius="md",
                    type="submit",
                    width="48%",
                    padding_y="12px",
                ),
                rx.button(
                    rx.hstack(rx.icon(tag="x", font_size="sm"), rx.text("Cancelar"), spacing="2"),
                    color=TEXT_BLACK,
                    background_color="white",
                    border="1px solid",
                    border_color=BORDER_GRAY_300,
                    _hover={"background_color": "rgb(245, 245, 245)"},
                    border_radius="md",
                    on_click=ProfileState.cancel_editing,
                    type="button",
                    width="48%",
                    padding_y="12px",
                ),
                width="100%",
                margin_top="6",
                spacing="4",
                justify_content="space-between",
            ),
            spacing="4",
            align_items="stretch",
            width="100%",
        ),
        on_submit=ProfileState.save_changes,
        width="100%",
        reset_on_submit=False,
    )

def info_card_content(state: ProfileState) -> rx.Component:
    return rx.vstack(
        rx.heading(
            "INFORMACIÓN DE PERFIL",
            size="4",
            font_weight="bold",
            margin_bottom="6", # 24px
            color=TEXT_BLACK,
            padding_top="2", 
            align_self="flex-start"
        ),
        rx.cond(
            state.is_editing,
            edit_view_card(state),
            display_view_card(state)
        ),
        rx.cond(
            ~state.is_editing,
            rx.hstack(
                rx.button(
                    rx.text("Editar Información", color=TEXT_BLACK, font_size="lg"), 
                    color_scheme="gray", 
                    variant="outline", 
                    background_color="white", 
                    border="1px solid", 
                    border_color=BORDER_GRAY_300,
                    border_radius="16px",
                    _hover={"background_color": "rgb(245,245,245)"}, 
                    on_click=ProfileState.start_editing,
                    width="48%",
                    padding_y="18px", 
                    font_weight="bold"
                ),
                rx.button(
                    rx.text("Cerrar Sesion", color="white", font_size="lg"),
                    background_color=BUTTON_RED_BG,
                    border_radius="16px",
                    _hover={"background_color": BUTTON_RED_HOVER_BG},
                    on_click=ProfileState.logout,
                    width="48%",
                    padding_y="18px",
                    font_weight="bold"
                ),
                width="100%",
                # margin_top="24px", # <--- VALOR ORIGINAL
                margin_top="8px",  # <--- Prueba con un valor más pequeño
                spacing="4", 
                justify_content="space-between", 
            ),
            rx.fragment()
        ),
        # spacing="4", # Espaciado general del vstack principal de la tarjeta
        # Podrías reducir este spacing general si el problema es más global
        # O añadir un padding_bottom más pequeño al display_view_card
        align_items="stretch", 
        width="100%",
        # height="100%", # Si el contenido es más corto que la tarjeta de foto, esto podría estirar.
                        # Prueba con "auto" o "fit-content" si es necesario, pero el "auto" del box padre ya debería gestionarlo.
        padding_bottom="6" # Asegurar un padding inferior consistente en la tarjeta de info. El "padding="32px"" del rx.box padre ya incluye esto.
                           # No creo que necesitemos modificar el height="100%" aquí, ya que el rx.box padre tiene height="auto"
    )



# --- Component Principal Refactoritzat ---
# --- Component Principal Refactoritzat ---
def profile_component() -> rx.Component:
    """Component funcional per a la pàgina de perfil amb nou disseny."""
    return rx.vstack(
        rx.heading(
            "Perfil",
            size="6",
            margin_top="20px", # Margen superior para separarlo del borde/navbar
            margin_bottom="4", # <--- Puedes probar con 4 (16px), 3 (12px) o incluso 2 (8px)
                               # O directamente en píxeles "10px", "15px"
            align_self="flex-start",
            margin_left="0px", # Asumiendo que el padding general lo maneja el layout
        ),
        rx.flex(
            # Tarjeta 1: Foto de Perfil
            rx.box(
                profile_picture_card_content(ProfileState),
                background_color=PROFILE_CARD_BG,
                border_radius="32px",
                width={"base": "100%", "md": "320px"},
                padding="24px",
                margin_bottom={"base": "32px", "md": "0"},
                height="fit-content", 
                overflow="visible",
            ),
            # Tarjeta 2: Información de Perfil
            rx.box(
                info_card_content(ProfileState),
                background_color=PROFILE_CARD_BG,
                border_radius="32px",
                flex_grow=1,
                max_width={"base": "100%", "md": "600px"},
                padding="32px",
                height="auto", 
            ),
            flex_direction={"base": "column", "md": "row"},
            align_items="stretch", 
            width="100%",
            gap="32px",
        ),
        # Este 'spacing' define el espacio entre el rx.heading y el rx.flex
        spacing="4", # <--- Prueba con 4 (16px), 3 (12px) o incluso 2 (8px)
        width="100%",
        align_items="flex-start", 
        padding_x={"base": "4", "lg": "6"}, 
        padding_y={"base": "4", "lg": "2"}, 
        max_width="1200px", 
        margin_x="auto", 
    )