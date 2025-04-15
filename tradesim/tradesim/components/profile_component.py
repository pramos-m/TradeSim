# profile_component.py (VERSIÓ COMPLETA AMB ÚLTIMES CORRECCIONS)
import reflex as rx
import re
import base64
from typing import List, Optional
import asyncio # Importa asyncio per rx.sleep

# Imports de BD, Controladors, Estat, etc.
from ..database import SessionLocal
from ..controller.user import (
    update_profile_picture, get_user_profile_picture, get_user_by_username,
    get_user_by_email, get_user_by_id )
from ..state.auth_state import AuthState, SECRET_KEY, ALGORITHM # Assumeix que AuthState té les vars heretades
from jose import jwt, JWTError

# --- Constants ---
DEFAULT_AVATAR = "/default_avatar.png" # Assegura't que aquesta imatge existeix a assets/
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPLOAD_ID = "avatar-upload" # Identificador únic per al component rx.upload
# Noves constants per estil (ajusta si cal)
CARD_BG_COLOR = "rgb(237, 237, 237)" # Gris clar de la teva imatge original
CARD_BORDER_RADIUS = "xl" # Cantonades arrodonides (pots provar "lg", "xl")
CARD_SHADOW = "md"      # Ombra (pots provar "sm", "md", "lg")
IMAGE_SIZE = "200px"    # Mida per la imatge de perfil rectangular
IMAGE_BORDER_RADIUS = "lg" # Cantonades per la imatge

# --- Estat del Component (ProfileState) ---
class ProfileState(AuthState):
    """Gestiona l'estat i la lògica del component de perfil."""
    # Variables heretades NO es defineixen aquí.

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
        if self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email): self.email_error = "...format...invàlid."; valid = False
        if self.new_password != "" and self.new_password != self.confirm_password: self.password_error = "...no coincideixen."; valid = False
        if self.new_password and not self.confirm_password: self.password_error = "Confirma la nova contrasenya."; valid = False
        if not self.current_password: self.password_error = "...actual és obligatòria..."; valid = False
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
            if not hasattr(user, 'verify_password') or not hasattr(user, 'set_password'): self.general_message = "...mètodes User..."; self.message_color = "red"; db.close(); return
            if not user.verify_password(self.current_password): self.password_error = "...actual incorrecta."; self.general_message = "...corregeix..."; self.message_color = "red"; db.close(); return

            username_changed = self.temp_username != user.username
            email_changed = self.temp_email != user.email
            if username_changed: # ... (validació conflicte username) ...
                 if get_user_by_username(db, self.temp_username): self.username_error="...en ús."; self.general_message = "..."; self.message_color="red"; db.close(); return
            if email_changed: # ... (validació conflicte email) ...
                 if get_user_by_email(db, self.temp_email): self.email_error="...en ús."; self.general_message = "..."; self.message_color="red"; db.close(); return

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
                except Exception as e: print(f"Error...fitxer: {e}"); self.general_message="Error...imatge."; self.message_color="red"; db.rollback(); db.close(); return

            db.commit(); print("Canvis desats a la base de dades."); db.refresh(user)

            self.is_editing = False; self.general_message = "Perfil actualitzat amb èxit!"; self.message_color = "green"
            self._reset_errors()
            yield self.load_user_data() # Força recàrrega/refresc
            # _reset_temp_fields() es crida dins de load_user_data
            yield rx.clear_selected_files(UPLOAD_ID)

        except Exception as e: print(f"...error save_changes: {e}"); import traceback; traceback.print_exc(); db.rollback(); self.general_message = "...error inesperat..."; self.message_color = "red"
        finally:
            if db: db.close(); print("Database session closed after save attempt.")

    def logout(self):
        print("Logging out..."); self.auth_token = ""; self.username = ""; self.email = ""; self.profile_image_url = DEFAULT_AVATAR
        self._reset_errors(); self._reset_temp_fields(); self.is_editing = False
        return rx.redirect("/login")
# <<< FI DE LA CLASSE ProfileState >>>


# --- Funcions UI Refactoritzades per al Nou Disseny ---

def profile_picture_card_content(state: ProfileState) -> rx.Component:
    """Contingut de la targeta de la foto de perfil."""
    placeholder = rx.box(
        rx.vstack( rx.icon(tag="image", size=48, color=rx.color("gray", 8)), rx.text("Afegir Foto", color=rx.color("gray", 9), size="2"),
            spacing="2", align="center", justify="center", ),
        width=IMAGE_SIZE, height=IMAGE_SIZE, border=f"2px dashed {rx.color('gray', 6)}", border_radius=IMAGE_BORDER_RADIUS,
        display="flex", align_items="center", justify_content="center", )

    return rx.vstack(
        rx.heading("FOTO DE PERFIL", size="4", weight="bold", margin_bottom="4", align_self="start"),
        rx.upload(
            rx.box(
                rx.cond(
                    state.is_editing & (rx.selected_files(UPLOAD_ID).length() > 0),
                    rx.foreach( rx.selected_files(UPLOAD_ID), lambda file: rx.image( src=rx.get_upload_url(file), width=IMAGE_SIZE, height=IMAGE_SIZE, object_fit="cover", border_radius=IMAGE_BORDER_RADIUS,) ),
                    rx.cond( state.profile_image_url != DEFAULT_AVATAR,
                         rx.image( src=state.profile_image_url, width=IMAGE_SIZE, height=IMAGE_SIZE, object_fit="cover", border_radius=IMAGE_BORDER_RADIUS,
                            opacity=rx.cond(state.is_editing, 0.7, 1.0), border=rx.cond(state.is_editing, f"3px dashed {rx.color('gray', 8)}", "none")),
                        placeholder ) ),
                padding=0, border="none", cursor=rx.cond(state.is_editing, "pointer", "default"), ),
            id=UPLOAD_ID, on_drop=ProfileState.handle_upload(rx.upload_files(upload_id=UPLOAD_ID)), accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"], "image/gif": [".gif"]},
            max_files=1, disabled=~state.is_editing, style={"padding": 0, "border": "none"} ),
        rx.cond( ~state.is_editing, rx.button( "Editar Foto", on_click=ProfileState.start_editing, variant="soft", color_scheme="blue", size="2", width="80%", margin_top="4" ) ),
        align_items="center", width="100%", spacing="3" )

def info_card_content(state: ProfileState) -> rx.Component:
    """Contingut de la targeta d'informació (vista o edició)."""
    return rx.vstack(
        rx.heading("INFORMACIÓN DE PERFIL", size="4", weight="bold", margin_bottom="4", align_self="start"),
        rx.cond( state.is_editing, edit_view_card(state), display_view_card(state) ),
        rx.cond( ~state.is_editing,
            rx.hstack( rx.button("Tancar Sessió", on_click=ProfileState.logout, color_scheme="red", variant="soft", size="2", type="button"),
                       rx.button("Editar Informació", on_click=ProfileState.start_editing, color_scheme="blue", size="2", type="button"),
                       spacing="3", justify="end", width="100%", margin_top="auto", padding_top="5" ) ),
        align_items="stretch", width="100%", flex_grow="1", justify_content="space-between", )

def display_view_card(state: ProfileState) -> rx.Component:
    """Nova vista de display amb icones."""
    return rx.vstack(
        rx.hstack(rx.icon("user", size=20), rx.text("NOMBRE:", weight="bold")),
        rx.text(state.username, size="3", margin_left="26px"),
        rx.divider(margin_y="2", size="4"),

        rx.hstack(rx.icon("mail", size=20), rx.text("EMAIL:", weight="bold")),
        rx.text(state.email, size="3", margin_left="26px"),
        rx.divider(margin_y="2", size="4"),

        # <<< ICONA CORREGIDA AQUÍ >>>
        rx.hstack(rx.icon("shield", size=20), rx.text("CONTRASEÑA:", weight="bold")),
        rx.text("**********", size="3", margin_left="26px"),

        spacing="1", align_items="start", width="100%", padding_bottom="4" )

def edit_view_card(state: ProfileState) -> rx.Component:
    """Nova vista d'edició amb icones."""
    return rx.form.root(
        rx.vstack(
            rx.cond( state.general_message, rx.callout.root( rx.callout.icon(rx.icon(tag=rx.cond(state.message_color == "red", "alert-triangle", "check-circle-2"))), rx.callout.text(state.general_message), color_scheme=state.message_color, variant="soft", margin_bottom="4", width="100%", role="alert", ) ),
            rx.form.field( rx.hstack(rx.icon("user", size=20), rx.form.label("Nom d'usuari:", html_for="username")),
                           rx.input(id="username", value=state.temp_username, on_change=ProfileState.set_temp_username, required=True, placeholder="El teu nom d'usuari", border_color=rx.cond(state.username_error != "", rx.color("red", 7), None)),
                           rx.cond(state.username_error != "", rx.form.message(state.username_error, color_scheme="red", force_match=True)),
                           margin_bottom="3", width="100%", name="username", ),
            rx.form.field( rx.hstack(rx.icon("mail", size=20), rx.form.label("Correu electrònic:", html_for="email")),
                           rx.input(id="email", type="email", value=state.temp_email, on_change=ProfileState.set_temp_email, required=True, placeholder="El teu correu electrònic", border_color=rx.cond(state.email_error != "", rx.color("red", 7), None)),
                           rx.cond(state.email_error != "", rx.form.message(state.email_error, color_scheme="red", force_match=True)),
                           margin_bottom="3", width="100%", name="email", ),
            rx.form.field( rx.hstack(rx.icon("lock", size=20), rx.form.label("Contrasenya Actual:", html_for="current_password")),
                           rx.input( id="current_password", type="password", value=state.current_password, on_change=ProfileState.set_current_password, placeholder="Obligatòria per desar canvis", required=True, border_color=rx.cond(state.password_error.contains("actual"), rx.color("red", 7), None), ),
                           rx.cond(state.password_error.contains("actual"), rx.form.message(state.password_error, color_scheme="red", force_match=True) ),
                           margin_bottom="3", width="100%", name="current_password", ),
            rx.form.field( rx.hstack(rx.icon("key", size=20), rx.form.label("Nova Contrasenya (opcional):", html_for="new_password")),
                           rx.input(id="new_password", type="password", value=state.new_password, on_change=ProfileState.set_new_password, placeholder="Deixar en blanc per no canviar"),
                           margin_bottom="3", width="100%", name="new_password", ),
            rx.form.field( rx.hstack(rx.icon("check", size=20), rx.form.label("Confirmar Nova Contrasenya:", html_for="confirm_password")),
                           rx.input(id="confirm_password", type="password", value=state.confirm_password, on_change=ProfileState.set_confirm_password, placeholder="Repeteix la nova contrasenya", border_color=rx.cond(state.password_error.contains("coincideixen") | state.password_error.contains("Confirma"), rx.color("red", 7), None)),
                           rx.cond(state.password_error.contains("coincideixen") | state.password_error.contains("Confirma"), rx.form.message(state.password_error, color_scheme="red", force_match=True) ),
                           margin_bottom="5", width="100%", name="confirm_password", ),
            rx.flex( rx.button("Cancel·lar", on_click=ProfileState.cancel_editing, color_scheme="gray", variant="soft", type="button", size="2"),
                     rx.form.submit( rx.button( "Desar Canvis", color_scheme="blue", size="2" ), as_child=True ), # Treiem disabled=~state.can_save
                     justify="end", width="100%", gap="10px", margin_top="4" ),
            align_items="stretch", width="100%", spacing="3", ),
        on_submit=ProfileState.save_changes, width="100%", )

# --- Component Principal Refactoritzat ---
# DINS DE profile_component.py

# --- Component Principal Refactoritzat ---
def profile_component() -> rx.Component:
    """Component funcional per a la pàgina de perfil amb nou disseny."""
    card_style = {
        "background_color": CARD_BG_COLOR,
        "border_radius": CARD_BORDER_RADIUS,
        "padding": "1.5rem",
        "box_shadow": CARD_SHADOW,
        "height": "100%",
        "display": "flex",
        "flex_direction": "column",
    }

    return rx.box(
        # rx.heading("Perfil d'Usuari", size="7", margin_bottom="8", align="center"),
        rx.flex(
            rx.box( # Targeta Esquerra: Foto
                profile_picture_card_content(ProfileState),
                **card_style,
                # <<< CANVI AQUÍ: Sintaxi de diccionari per a width >>>
                width={
                    "base": "100%", # Amplada completa en mòbil
                    "sm": "100%",   # Amplada completa en petit
                    "md": "300px",  # Amplada fixa des de mida mitjana
                    "lg": "350px",
                    "xl": "400px"
                },
                # <<< CANVI AQUÍ: Sintaxi de diccionari per a margin_bottom >>>
                 margin_bottom={
                    "base": "4", # Marge inferior 4 en base i sm (Radix normalment usa números per escala d'espaiat)
                    "sm": "4",
                    "md": "0"   # Sense marge inferior des de md
                },
            ),
            rx.box( # Targeta Dreta: Informació
                info_card_content(ProfileState),
                **card_style,
                flex_grow="1", # Ocupa espai restant
            ),
            # Estils del contenidor flex principal
            align_items="stretch",
            gap="1.5rem", # Espai entre targetes
            direction={"base": "column", "md": "row"}, # Ja corregit
            width="100%",
            max_width="1100px",
            margin="2rem auto", # Marge vertical i centrat horitzontal
        ),
    )
