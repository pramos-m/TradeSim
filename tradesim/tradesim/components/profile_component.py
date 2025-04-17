# profile_component.py (VERSIÓN CORREGIDA)
import reflex as rx
import re
import base64
from typing import List, Optional
import asyncio

# Imports de BD, Controladores, Estado, etc.
from ..database import SessionLocal
from ..controller.user import (
    update_profile_picture, get_user_profile_picture, get_user_by_username,
    get_user_by_email, get_user_by_id )
from ..state.auth_state import AuthState, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

# --- Constants ---
DEFAULT_AVATAR = "/default_avatar.png"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPLOAD_ID = "avatar-upload"
CARD_BG_COLOR = "rgb(245, 245, 245)"
CARD_BORDER_RADIUS = "lg"
CARD_SHADOW = "md"
IMAGE_SIZE = "150px"
IMAGE_BORDER_RADIUS = "md"
BLUE = "#4F67EB"
RED = "#E53E3E"
TEXT_DARK = "#202124"
TEXT_GRAY = "#5F6368"
LIGHT_GRAY_BORDER = "#E2E8F0"
WHITE = "#FFFFFF"


# --- Estado del Componente (ProfileState) ---
class ProfileState(AuthState):
    """Gestiona el estado y la lógica del componente de perfil."""
    # Variables heredadas NO se definen aquí.

    is_editing: bool = False
    temp_username: str = ""
    temp_email: str = ""
    new_password: str = ""
    current_password: str = ""
    username_error: str = ""
    email_error: str = ""
    password_error: str = ""
    general_message: str = ""
    message_color: str = "green"
    selected_files_ref: List[rx.UploadFile] = []

    @rx.var
    def password_mismatch(self) -> bool:
        return self.new_password != "" and self.new_password != self.confirm_password

    @rx.var
    def invalid_email(self) -> bool:
        return self.is_editing and self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email)

    @rx.var
    def username_empty(self) -> bool:
        return self.is_editing and not self.temp_username.strip()

    @rx.var
    def can_save(self) -> bool:
         mismatch = self.new_password != "" and self.new_password != self.confirm_password
         invalid_mail = self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email)
         empty_user = not self.temp_username.strip()
         return self.is_editing and not mismatch and not invalid_mail and not empty_user

    def _get_user_id(self) -> int:
        try:
            token = str(self.auth_token or "")
            if not token: return -1
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("sub", -1))
        except Exception as e: print(f"Error obteniendo user_id: {e}"); return -1

    def _reset_errors(self):
        self.username_error = ""; self.email_error = ""; self.password_error = ""; self.general_message = ""

    def _reset_temp_fields(self):
        self.temp_username = self.username; self.temp_email = self.email; self.new_password = ""
        self.confirm_password = ""; self.current_password = ""; self.selected_files_ref = []

    def load_user_data(self):
        user_id_to_load = self._get_user_id()
        print(f"Attempting to load data for user ID: {user_id_to_load}")
        if user_id_to_load <= 0:
            self.username = ""; self.email = ""; self.profile_image_url = DEFAULT_AVATAR; self._reset_temp_fields(); return
        db = None
        try:
            db = SessionLocal(); user = get_user_by_id(db, user_id_to_load)
            if user:
                self.username = user.username; self.email = user.email
                picture_data, picture_type = get_user_profile_picture(db, user.id)
                if picture_data and picture_type:
                    base64_image = base64.b64encode(picture_data).decode("utf-8")
                    self.profile_image_url = f"data:{picture_type};base64,{base64_image}"
                else: self.profile_image_url = DEFAULT_AVATAR
            else: self.username = ""; self.email = ""; self.profile_image_url = DEFAULT_AVATAR
            self._reset_temp_fields()
        except Exception as e: print(f"Error loading profile data: {e}"); import traceback; traceback.print_exc()
        finally:
            if db: db.close(); print("Database session closed.")

    def start_editing(self):
        if not self.username and self._get_user_id() > 0: self.load_user_data()
        if self.username:
            self.is_editing = True; self._reset_errors(); self._reset_temp_fields(); self.selected_files_ref = []
            print("Mode edició activat")
        else: self.general_message = "No s'han pogut carregar les dades per editar."; self.message_color = "red"

    def cancel_editing(self):
        self.is_editing = False; self._reset_errors(); self._reset_temp_fields()
        return rx.clear_selected_files(UPLOAD_ID)

    async def handle_upload(self, files: List[rx.UploadFile]):
        if files:
            print(f"Fitxer seleccionat: {files[0].name}, Mida: {files[0].size}")
            self.selected_files_ref = files; self.general_message = ""
        else: self.selected_files_ref = []

    def _validate_form_on_save(self) -> bool:
        self._reset_errors(); valid = True
        if not self.temp_username.strip(): self.username_error = "El nom d'usuari no pot estar buit."; valid = False
        if self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email): self.email_error = "Format de correu invàlid."; valid = False
        if self.new_password != "" and self.new_password != self.confirm_password: self.password_error = "Les contrasenyes no coincideixen."; valid = False
        if self.new_password and not self.confirm_password: self.password_error = "Confirma la nova contrasenya."; valid = False
        if not self.current_password: self.password_error = "La contrasenya actual és obligatòria."; valid = False
        return valid

    async def save_changes(self):
        if not self._validate_form_on_save():
            self.general_message = "Si us plau, corregeix els errors."; self.message_color = "red"; return
        user_id_to_save = self._get_user_id()
        if user_id_to_save <= 0:
            self.general_message = "Error: Sessió invàlida..."; self.message_color = "red"; return
        db = None
        try:
            print("Iniciant desat de canvis..."); db = SessionLocal(); user = get_user_by_id(db, user_id_to_save)
            if not user: self.general_message = "Error: Usuari no trobat."; self.message_color = "red"; db.close(); return
            if not hasattr(user, 'verify_password') or not hasattr(user, 'set_password'): self.general_message = "Error en mètodes User."; self.message_color = "red"; db.close(); return
            if not user.verify_password(self.current_password): self.password_error = "Contrasenya actual incorrecta."; self.general_message = "Corregeix els errors."; self.message_color = "red"; db.close(); return

            username_changed = self.temp_username != user.username
            email_changed = self.temp_email != user.email
            if username_changed:
                 if get_user_by_username(db, self.temp_username): self.username_error="Nom d'usuari ja en ús."; self.general_message = "Corregeix els errors."; self.message_color="red"; db.close(); return
            if email_changed:
                 if get_user_by_email(db, self.temp_email): self.email_error="Correu ja en ús."; self.general_message = "Corregeix els errors."; self.message_color="red"; db.close(); return

            if username_changed: user.username = self.temp_username
            if email_changed: user.email = self.temp_email
            if self.new_password: user.set_password(self.new_password)

            image_processed = False
            if self.selected_files_ref:
                file = self.selected_files_ref[0]
                try:
                    new_image_data = await file.read()
                    update_profile_picture(db, user.id, new_image_data, file.content_type)
                    image_processed = True
                except Exception as e: print(f"Error al processar fitxer: {e}"); self.general_message="Error al processar imatge."; self.message_color="red"; db.rollback(); db.close(); return

            db.commit(); print("Canvis desats a la base de dades."); db.refresh(user)

            self.is_editing = False; self.general_message = "Perfil actualitzat amb èxit!"; self.message_color = "green"
            self._reset_errors()
            yield self.load_user_data() # Força recàrrega/refresc
            # _reset_temp_fields() es crida dins de load_user_data
            yield rx.clear_selected_files(UPLOAD_ID)

        except Exception as e: print(f"Error en save_changes: {e}"); import traceback; traceback.print_exc(); db.rollback(); self.general_message = "Error inesperat al guardar."; self.message_color = "red"
        finally:
            if db: db.close(); print("Database session closed after save attempt.")

    def logout(self):
        print("Logging out..."); self.auth_token = ""; self.username = ""; self.email = ""; self.profile_image_url = DEFAULT_AVATAR
        self._reset_errors(); self._reset_temp_fields(); self.is_editing = False
        return rx.redirect("/login")
# <<< FI DE LA CLASSE ProfileState >>>


# --- Funciones UI Refactorizadas para el Nuevo Diseño ---

def profile_picture_card_content(state: ProfileState) -> rx.Component:
    """Contenido de la tarjeta de la foto de perfil."""
    placeholder = rx.box(
    rx.vstack( 
        rx.icon(tag="image", size=48, color=rx.color("gray", 8)), 
        rx.text("Afegir Foto", color=rx.color("gray", 9), size="2"),
        spacing="2", 
        align="center", 
        justify="center", 
    ),
    width="100%",  # Ocupar el ancho completo del contenedor
    height="280px",  # Altura fija que coincida con el espacio de la línea discontinua
    border=f"2px dashed {rx.color('gray', 6)}", 
    border_radius=IMAGE_BORDER_RADIUS,
    display="flex", 
    align_items="center", 
    justify_content="center", 
)


    return rx.vstack(
        rx.heading("FOTO DE PERFIL:", size="4", weight="medium", margin_bottom="6", align_self="start"),
        rx.upload(
            rx.box(
                rx.cond(
                    state.is_editing & (rx.selected_files(UPLOAD_ID).length() > 0),
                    rx.foreach(
                        rx.selected_files(UPLOAD_ID), 
                        lambda file: rx.image(
                            src=rx.get_upload_url(file), 
                            width=IMAGE_SIZE, 
                            height=IMAGE_SIZE, 
                            object_fit="cover", 
                            border_radius=IMAGE_BORDER_RADIUS,
                        )
                    ),
                    rx.cond(
                        state.profile_image_url != DEFAULT_AVATAR,
                        rx.image(
                            src=state.profile_image_url, 
                            width=IMAGE_SIZE, 
                            height=IMAGE_SIZE, 
                            object_fit="cover", 
                            border_radius=IMAGE_BORDER_RADIUS,
                            opacity=rx.cond(state.is_editing, 0.7, 1.0), 
                            border=rx.cond(state.is_editing, f"3px dashed {rx.color('gray', 8)}", "none")
                        ),
                        placeholder
                    )
                ),
                padding=0, 
                border="none", 
                cursor=rx.cond(state.is_editing, "pointer", "default"),
            ),
            id=UPLOAD_ID, 
            on_drop=ProfileState.handle_upload(rx.upload_files(upload_id=UPLOAD_ID)), 
            accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"], "image/gif": [".gif"]},
            max_files=1, 
            disabled=~state.is_editing, 
            style={"padding": 0, "border": "none"}
        ),
        rx.button(
            "Editar Foto",
            on_click=ProfileState.start_editing,
            variant="solid",
            color="white",
            bg=BLUE,
            size="2",
            width="100%",
            margin_top="4",
            border_radius="md",
        ),
        align_items="center", 
        width="100%", 
        spacing="3",
        height="100%",
        padding="8",
        bg=CARD_BG_COLOR,
        border_radius="lg",
        border="1px solid",
        border_color="rgba(0, 0, 0, 0.1)",
    )

def display_view_card(state: ProfileState) -> rx.Component:
    """Nueva vista de display con iconos."""
    return rx.vstack(
        # Nombre con icono de usuario
        rx.hstack(
            rx.box(
                rx.icon("user", size=20), 
                width="40px", 
                height="40px", 
                # background_color="black", 
                color="black", 
                border_radius="md", 
                display="flex", 
                align_items="center", 
                justify_content="center"
            ),
            rx.vstack(
                rx.text("NOMBRE:", weight="bold", size="3"),
                rx.text(state.username, size="3"),
                spacing="1", 
                align_items="start"
            ),
            spacing="4", 
            align_items="center", 
            width="100%"
        ),
        rx.divider(margin_y="4"),

        # Email con icono de correo
        rx.hstack(
            rx.box(
                rx.icon("mail", size=20), 
                width="40px", 
                height="40px", 
                # background_color="black", 
                color="black", 
                border_radius="md", 
                display="flex", 
                align_items="center", 
                justify_content="center"
            ),
            rx.vstack(
                rx.text("EMAIL:", weight="bold", size="3"),
                rx.text(state.email, size="3"),
                spacing="1", 
                align_items="start"
            ),
            spacing="4", 
            align_items="center", 
            width="100%"
        ),
        rx.divider(margin_y="4"),

        # Contraseña con icono de escudo
        rx.hstack(
            rx.box(
                rx.icon("shield", size=20), 
                width="40px", 
                height="40px", 
                # background_color="black", 
                color="black", 
                border_radius="md", 
                display="flex", 
                align_items="center", 
                justify_content="center"
            ),
            rx.vstack(
                rx.text("CONTRASEÑA:", weight="bold", size="3"),
                rx.text("************", size="3"),
                spacing="1", 
                align_items="start"
            ),
            spacing="4", 
            align_items="center", 
            width="100%"
        ),

        spacing="3", 
        align_items="start", 
        width="100%", 
        padding_bottom="4"
    )

def edit_view_card(state: ProfileState) -> rx.Component:
    """Nueva vista de edición con iconos."""
    return rx.form.root(
        rx.vstack(
            rx.cond(
                state.general_message, 
                rx.callout.root(
                    rx.callout.icon(rx.icon(tag=rx.cond(state.message_color == "red", "alert-triangle", "check-circle-2"))), 
                    rx.callout.text(state.general_message), 
                    color_scheme=state.message_color, 
                    variant="soft", 
                    margin_bottom="4", 
                    width="100%", 
                    role="alert", 
                )
            ),
            rx.form.field(
                rx.hstack(rx.icon("user", size=20), rx.form.label("Nom d'usuari:", html_for="username")),
                rx.input(
                    id="username", 
                    value=state.temp_username, 
                    on_change=ProfileState.set_temp_username, 
                    required=True, 
                    placeholder="El teu nom d'usuari", 
                    border_color=rx.cond(state.username_error != "", rx.color("red", 7), None)
                ),
                rx.cond(state.username_error != "", rx.form.message(state.username_error, color_scheme="red", force_match=True)),
                margin_bottom="3", 
                width="100%", 
                name="username",
            ),
            rx.form.field(
                rx.hstack(rx.icon("mail", size=20), rx.form.label("Correu electrònic:", html_for="email")),
                rx.input(
                    id="email", 
                    type="email", 
                    value=state.temp_email, 
                    on_change=ProfileState.set_temp_email, 
                    required=True, 
                    placeholder="El teu correu electrònic", 
                    border_color=rx.cond(state.email_error != "", rx.color("red", 7), None)
                ),
                rx.cond(state.email_error != "", rx.form.message(state.email_error, color_scheme="red", force_match=True)),
                margin_bottom="3", 
                width="100%", 
                name="email",
            ),
            rx.form.field(
                rx.hstack(rx.icon("lock", size=20), rx.form.label("Contrasenya Actual:", html_for="current_password")),
                rx.input(
                    id="current_password", 
                    type="password", 
                    value=state.current_password, 
                    on_change=ProfileState.set_current_password, 
                    placeholder="Obligatòria per desar canvis", 
                    required=True, 
                    border_color=rx.cond(state.password_error.contains("actual"), rx.color("red", 7), None),
                ),
                rx.cond(state.password_error.contains("actual"), rx.form.message(state.password_error, color_scheme="red", force_match=True)),
                margin_bottom="3", 
                width="100%", 
                name="current_password",
            ),
            rx.form.field(
                rx.hstack(rx.icon("key", size=20), rx.form.label("Nova Contrasenya (opcional):", html_for="new_password")),
                rx.input(
                    id="new_password", 
                    type="password", 
                    value=state.new_password, 
                    on_change=ProfileState.set_new_password, 
                    placeholder="Deixar en blanc per no canviar"
                ),
                margin_bottom="3", 
                width="100%", 
                name="new_password",
            ),
            rx.form.field(
                rx.hstack(rx.icon("check", size=20), rx.form.label("Confirmar Nova Contrasenya:", html_for="confirm_password")),
                rx.input(
                    id="confirm_password", 
                    type="password", 
                    value=state.confirm_password, 
                    on_change=ProfileState.set_confirm_password, 
                    placeholder="Repeteix la nova contrasenya", 
                    border_color=rx.cond(state.password_error.contains("coincideixen") | state.password_error.contains("Confirma"), rx.color("red", 7), None)
                ),
                rx.cond(state.password_error.contains("coincideixen") | state.password_error.contains("Confirma"), rx.form.message(state.password_error, color_scheme="red", force_match=True)),
                margin_bottom="5", 
                width="100%", 
                name="confirm_password",
            ),
            rx.flex(
                rx.button("Cancel·lar", on_click=ProfileState.cancel_editing, color_scheme="gray", variant="soft", type="button", size="2"),
                rx.form.submit(rx.button("Desar Canvis", color="black",bg=WHITE, size="2"), as_child=True),
                justify="end", 
                width="100%", 
                gap="10px", 
                margin_top="4"
            ),
            align_items="stretch", 
            width="100%", 
            spacing="4",  # Aumentado de 3 a 4
            padding_y="2",  # Añadir padding vertical
        ),
        on_submit=ProfileState.save_changes, 
        width="100%",
    )

def info_card_content(state: ProfileState) -> rx.Component:
    """Contenido de la tarjeta de información (vista o edición)."""
    return rx.vstack(
        rx.heading("INFORMACIÓN DE PERFIL", size="4", weight="medium", margin_bottom="6", align_self="start"),
        rx.cond(
            state.is_editing, 
            edit_view_card(state), 
            display_view_card(state)
        ),
        rx.cond(
            ~state.is_editing,
            rx.hstack(
                rx.button(
                    "Editar Información", 
                    on_click=ProfileState.start_editing, 
                    color="black",
                    bg=WHITE,
                    size="2", 
                    variant="solid",
                    border_radius="md",
                    type="button"
                ),
                rx.button(
                    "Cerrar Sesion", 
                    on_click=ProfileState.logout, 
                    color="white", 
                    bg=RED,
                    variant="solid",
                    border_radius="md",
                    size="2", 
                    type="button"
                ),
                spacing="3", 
                justify="end", 
                width="100%", 
                margin_top="4", 
                padding_top="3"
            )
        ),
        align_items="stretch", 
        width="100%", 
        height="100%",
        padding="8",
        bg=CARD_BG_COLOR,
        border_radius="lg",
        border="1px solid",
        border_color="rgba(0, 0, 0, 0.1)",
    )

# --- Component Principal Refactoritzat ---
def profile_component() -> rx.Component:
    """Component funcional per a la pàgina de perfil amb nou disseny."""
    return rx.box(
        rx.box(
            rx.vstack(
                # Título de la página
                rx.heading("Perfil", size="5", margin_bottom="6", align_self="start"),
                
                # Contenido principal - Tarjetas de perfil en una fila
                rx.flex(
                    # Tarjeta izquierda - Foto de perfil
                    rx.box(
                        profile_picture_card_content(ProfileState),
                        width={"base": "100%", "md": "30%"},  # Cambiado de 350px fijo a 30%
                        min_width={"base": "100%", "md": "300px"},  # Valor mínimo para asegurar legibilidad
                        margin_bottom={"base": "4", "md": "0"},
                        height="fit-content",  # Para que no se estire verticalmente
                    ),
                    
                    # Tarjeta derecha - Información
                    rx.box(
                        info_card_content(ProfileState),
                        flex_grow="1",
                        width={"base": "100%", "md": "70%"},  # Asignar el resto del espacio
                        height="fit-content",  # Para que no se estire verticalmente
                    ),
                    
                    # Configuración del contenedor flex de tarjetas
                    direction={"base": "column", "md": "row"},
                    gap="8",  # Aumentado de 6 a 8 para más separación
                    width="100%",
                    align_items="flex-start",  # Cambio de "stretch" a "flex-start"
                    justify_content="space-between",  # Mejor distribución horizontal
                ),
                
                # Configuración del vstack principal
                width="100%",
                max_width="1200px",
                margin="0 auto",
                spacing="4",
                padding="6",
            ),
            # Configuración general de la página
            width="100%",
            background=WHITE,
            min_height="100vh",
            padding={"base": "4", "md": "6"},
        )
    )