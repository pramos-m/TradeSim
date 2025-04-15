# profile_component.py
import reflex as rx
import re
import base64
from typing import List
from ..database import SessionLocal
from ..controller.user import (
    update_profile_picture,
    get_user_profile_picture,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    )
from ..state.auth_state import AuthState, SECRET_KEY, ALGORITHM # Assumeix que AuthState té 'auth_token'
from jose import jwt, JWTError

# --- Constants ---
DEFAULT_AVATAR = "/default_avatar.png"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
UPLOAD_ID = "avatar-upload"

# --- Estat del Component ---
class ProfileState(AuthState): # Hereda d'AuthState
    """Gestiona l'estat i la lògica del component de perfil."""

    # <<< Variables eliminades perquè s'hereten d'AuthState >>>
    # user_id: int = -1
    # username: str = ""
    # email: str = ""

    # Variable específica d'aquest estat
    # profile_image_url: str = DEFAULT_AVATAR

    # Estat d'edició
    # Variables heretades (username, email, confirm_password, profile_image_url) NO es defineixen aquí

    # Estat d'edició
    is_editing: bool = False

    # Camps temporals per a l'edició
    temp_username: str = ""
    temp_email: str = ""
    new_password: str = ""
    current_password: str = ""

    # Errors de validació
    username_error: str = ""
    email_error: str = ""
    password_error: str = ""
    general_message: str = ""
    message_color: str = "green"

    # <<< NOU/CORREGIT: Variable per guardar referència >>>
    selected_files_ref: List[rx.UploadFile] = []

    # --- Computed Vars ---
    @rx.var
    def password_mismatch(self) -> bool:
        """Comprova si les contrasenyes no coincideixen."""
        return self.new_password != "" and self.new_password != self.confirm_password # Usa l'heretat

    @rx.var
    def invalid_email(self) -> bool:
        """Comprova si l'email temporal té un format invàlid."""
        return self.is_editing and self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email)

    @rx.var
    def username_empty(self) -> bool:
        """Comprova si el nom d'usuari temporal està buit."""
        return self.is_editing and not self.temp_username.strip()

    @rx.var
    def can_save(self) -> bool:
        """Determina si el botó de desar hauria d'estar habilitat."""
        # Només es pot desar si s'està editant i no hi ha errors de validació pendents
        # La comprovació de current_password es farà a _validate_form
        return (
            self.is_editing and
            not (self.new_password != "" and self.new_password != self.confirm_password) and # No hi ha mismatch
            not (self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email)) and # Email vàlid si no buit
            not (not self.temp_username.strip()) # Username no buit
        )

    # --- Event Handlers ---

    def _get_user_id(self) -> int:
        # ... (codi _get_user_id sense canvis) ...
        try:
            token = str(self.auth_token or "")
            if not token: return -1
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload.get("sub", -1))
        except Exception as e:
            print(f"Error obteniendo user_id: {e}")
            return -1


    def _reset_errors(self):
        self.username_error = ""
        self.email_error = ""
        self.password_error = ""
        self.general_message = ""

    # <<< MODIFICAT: Neteja selected_files_ref >>>
    def _reset_temp_fields(self):
        self.temp_username = self.username
        self.temp_email = self.email
        self.new_password = ""
        self.confirm_password = "" # Assigna a l'heretat
        self.current_password = ""
        self.selected_files_ref = [] # Neteja referència

    def load_user_data(self):
        """Carrega les dades reals de l'usuari des del backend."""
        user_id_to_load = self._get_user_id()
        print(f"Attempting to load data for user ID: {user_id_to_load}")

        if user_id_to_load <= 0:
            print("User ID not valid, cannot load profile.")
            self.username = "" # Reseteja l'heretat
            self.email = ""    # Reseteja l'heretat
            self.profile_image_url = DEFAULT_AVATAR
            self._reset_temp_fields()
            return

        db = None
        try:
            db = SessionLocal()
            user = get_user_by_id(db, user_id_to_load)
            if user:
                print(f"User found: {user.username}")
                self.username = user.username # Assigna a l'heretat
                self.email = user.email       # Assigna a l'heretat

                picture_data, picture_type = get_user_profile_picture(db, user.id)
                if picture_data and picture_type:
                    base64_image = base64.b64encode(picture_data).decode("utf-8")
                    self.profile_image_url = f"data:{picture_type};base64,{base64_image}"
                    print(f"Loaded profile picture: type {picture_type}")
                else:
                    self.profile_image_url = DEFAULT_AVATAR
                    print("No profile picture found, using default.")
            else:
                 print(f"User with ID {user_id_to_load} not found in database.")
                 self.username = ""
                 self.email = ""
                 self.profile_image_url = DEFAULT_AVATAR

            self._reset_temp_fields()

        except Exception as e:
            print(f"Error loading profile data: {e}")
            import traceback
            traceback.print_exc()
            self.general_message = "Error carregant el perfil."
            self.message_color = "red"
        finally:
            if db:
                db.close()
                print("Database session closed.")

    def start_editing(self):
        if not self.username and self._get_user_id() > 0: self.load_user_data()
        if self.username:
            self.is_editing = True
            self._reset_errors()
            self._reset_temp_fields() # Això neteja la ref
            print("Mode edició activat")

        if self.username: # Comprova l'heretat
            self.is_editing = True
            self._reset_errors()
            self._reset_temp_fields()
            print("Mode edició activat")
        else:
             print("Cannot enter edit mode: No user data loaded.")
             self.general_message = "No s'han pogut carregar les dades per editar."
             self.message_color = "red"

    def cancel_editing(self):
        self.is_editing = False
        self._reset_errors()
        self._reset_temp_fields() # Neteja la ref
        return rx.clear_selected_files(UPLOAD_ID) # Neteja preview

    async def handle_upload(self, files: List[rx.UploadFile]):
        """Gestiona la selecció de fitxers i desa la referència."""
        if files:
            # Utilitza .name en lloc de .filename (Deprecated)
            print(f"Fitxer seleccionat: {files[0].name}, Mida: {files[0].size}")
            self.selected_files_ref = files
            self.general_message = "" # Neteja missatges previs si el fitxer és vàlid
        else:
            self.selected_files_ref = []
            print("No s'ha seleccionat cap fitxer o s'ha eliminat.")

    def _validate_form(self) -> bool:
        self._reset_errors()
        valid = True
        if not self.temp_username.strip(): # Comprovació simplificada
            self.username_error = "El nom d'usuari no pot estar buit."
            valid = False
        if self.temp_email != "" and not re.match(EMAIL_REGEX, self.temp_email): # Comprovació simplificada
            self.email_error = "El format del correu electrònic no és vàlid."
            valid = False
        if self.new_password != "" and self.new_password != self.confirm_password:
             self.password_error = "Les noves contrasenyes no coincideixen."
             valid = False
        # Comprova confirmació només si hi ha nova contrasenya
        if self.new_password and not self.confirm_password:
             self.password_error = "Confirma la nova contrasenya."
             valid = False
        # Comprova contrasenya actual SEMPRE
        if not self.current_password:
             self.password_error = "La contrasenya actual és obligatòria per desar."
             valid = False
        return valid

    async def save_changes(self):
        """Valida i desa els canvis del perfil al backend."""
        if not self._validate_form():
            self.general_message = "Si us plau, corregeix els errors."
            self.message_color = "red"
            # No retornis res aquí perquè els errors es mostrin
            return

        user_id_to_save = self._get_user_id()
        if user_id_to_save <= 0:
            self.general_message = "Error: Sessió invàlida o ID d'usuari no trobat."
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
                db.close()
                return
            if not hasattr(user, 'verify_password') or not hasattr(user, 'set_password'):
                 self.general_message = "Error intern del servidor (mètodes User)."
                 self.message_color = "red"
                 db.close()
                 return

            if not user.verify_password(self.current_password):
                self.password_error = "Contrasenya actual incorrecta."
                self.general_message = "Si us plau, corregeix els errors."
                self.message_color = "red"
                db.close()
                return

            # Prepara actualitzacions i valida conflictes (abans de modificar l'objecte user)
            username_changed = self.temp_username != user.username
            email_changed = self.temp_email != user.email

            if username_changed:
                existing_username = get_user_by_username(db, self.temp_username)
                if existing_username and existing_username.id != user.id:
                    self.username_error = "Aquest nom d'usuari ja està en ús."
                    self.general_message = "Si us plau, corregeix els errors."
                    self.message_color = "red"
                    db.close()
                    return

            if email_changed:
                existing_email = get_user_by_email(db, self.temp_email)
                if existing_email and existing_email.id != user.id:
                    self.email_error = "Aquest correu electrònic ja està en ús."
                    self.general_message = "Si us plau, corregeix els errors."
                    self.message_color = "red"
                    db.close()
                    return

            # Aplica canvis a l'objecte user SI les validacions han passat
            if username_changed:
                user.username = self.temp_username
                print(f"Username canviat a: {user.username}")
            if email_changed:
                user.email = self.temp_email
                print(f"Email canviat a: {user.email}")
            if self.new_password:
                user.set_password(self.new_password)
                print("Contrasenya actualitzada (a l'objecte user).")

            # Gestiona la nova imatge
            image_updated_in_db = False
            new_image_url_for_state = self.profile_image_url # Assumeix que no canvia
            if self.selected_files_ref:
                file = self.selected_files_ref[0]
                try:
                    new_image_data = await file.read()
                    print(f"Preparant per pujar nova imatge: {file.name} ({len(new_image_data)} bytes)")
                    update_profile_picture(db, user.id, new_image_data, file.content_type)
                    image_updated_in_db = True # Marca que s'ha intentat actualitzar
                    print("Imatge de perfil actualitzada a la base de dades.")
                except Exception as e:
                    print(f"Error processant/pujant el fitxer: {e}")
                    self.general_message = "Error actualitzant la imatge."
                    self.message_color = "red"
                    db.rollback()
                    db.close()
                    return

            # Desa els canvis a la base de dades (usuari i possiblement imatge)
            db.commit()
            print("Canvis desats a la base de dades.")
            db.refresh(user) # Refresca l'objecte user amb les dades de la BD

            # Actualitza l'estat local AMB LES DADES FINALS
            # Assigna directament des de les variables temporals validades o de l'objecte refrescat
            self.username = user.username # Actualitza l'estat heretat
            self.email = user.email       # Actualitza l'estat heretat

            # Actualitza la imatge només si s'ha processat una nova
            if image_updated_in_db:
                # Torna a carregar la imatge DESPRÉS del commit per assegurar la darrera versió
                picture_data, picture_type = get_user_profile_picture(db, user.id)
                if picture_data and picture_type:
                    base64_image = base64.b64encode(picture_data).decode("utf-8")
                    self.profile_image_url = f"data:{picture_type};base64,{base64_image}" # Actualitza l'estat heretat
                    print("URL d'imatge a l'estat actualitzada post-desat.")
                else:
                     self.profile_image_url = DEFAULT_AVATAR
                     print("No s'ha trobat imatge post-desat, utilitzant default.")


            # Finalització neta
            self.is_editing = False
            self.general_message = "Perfil actualitzat amb èxit!"
            self.message_color = "green"
            # Neteja els camps temporals DESPRÉS d'actualitzar l'estat principal
            self._reset_temp_fields() # Neteja refs i camps temporals
            self._reset_errors()
            # Retorna clear_selected_files per netejar la preview del frontend
            return rx.clear_selected_files(UPLOAD_ID)

        except Exception as e:
            print(f"Error inesperat durant save_changes: {e}")
            import traceback
            traceback.print_exc()
            if db: db.rollback()
            self.general_message = f"Error inesperat desant el perfil."
            self.message_color = "red"
        finally:
            if db: db.close()


def logout(self):
    """Neteja el token i redirigeix a login."""
    print("Logging out...")
    self.auth_token = "" # Neteja el token a AuthState
    # Neteja les variables heretades
    self.username = ""
    self.email = ""
    # Neteja les variables locals
    self.profile_image_url = DEFAULT_AVATAR
    self._reset_errors()
    self._reset_temp_fields()
    self.is_editing = False
    return rx.redirect("/login")

def profile_avatar(state: ProfileState) -> rx.Component:
    """Mostra l'avatar actual o el component d'upload/preview."""
    return rx.box(
        # Avatar en mode visualització
        rx.cond(
            ~state.is_editing,
            rx.avatar(
                name=state.username,
                src=state.profile_image_url,
                # <<< CANVI AQUÍ >>>
                fallback=rx.cond(state.username != "", state.username[:1].upper(), "?"),
                size="9",
                radius="full",
                high_contrast=False,
            )
        ),
        # Component d'upload en mode edició
        rx.cond(
            state.is_editing,
            rx.upload(
                rx.vstack(
                    # Previsualització o Avatar Actual
                    rx.cond(
                         rx.selected_files(UPLOAD_ID).length() > 0,
                         rx.foreach(
                            rx.selected_files(UPLOAD_ID),
                            # L'avatar de previsualització no necessita el fallback basat en username
                            lambda file: rx.avatar(src=rx.get_upload_url(file), fallback="?", size="9", radius="full"),
                         ),
                         # Avatar actual (si NO hi ha fitxer seleccionat per preview)
                         rx.avatar(
                            name=state.username,
                            src=state.profile_image_url,
                            # <<< CANVI AQUÍ TAMBÉ >>>
                            fallback=rx.cond(state.username != "", state.username[:1].upper(), "?"),
                            size="9",
                            radius="full",
                            style={"opacity": 0.6, "border": f"3px dashed {rx.color('gray', 8)}"}
                        )
                    ),
                    rx.button(
                        "Canviar Imatge", size="1", variant="soft", color_scheme="blue", margin_top="10px", type="button", ),
                    align="center", spacing="3",
                ),
                id=UPLOAD_ID, border="none", padding="0", style={"cursor": "pointer", "width":"fit-content", "margin": "0 auto"},
                on_drop=ProfileState.handle_upload(rx.upload_files(upload_id=UPLOAD_ID)),
                accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"], "image/gif": [".gif"]}, max_files=1,
            )
        ),
        margin_bottom="6", width="100%", display="flex", justify_content="center",
    )

def display_view(state: ProfileState) -> rx.Component:
    """Mostra la informació del perfil en mode visualització (Radix)."""
    return rx.vstack(
         rx.vstack(
             rx.text("Nom d'usuari:", color_scheme="gray", size="2", weight="bold"),
             rx.text(state.username, size="3"), # Mostra l'heretat
             spacing="1", align_items="start", width="100%", margin_bottom="3",
         ),
         rx.vstack(
             rx.text("Correu electrònic:", color_scheme="gray", size="2", weight="bold"),
             rx.text(state.email, size="3"), # Mostra l'heretat
             spacing="1", align_items="start", width="100%", margin_bottom="3",
         ),
         rx.vstack(
             rx.text("Contrasenya:", color_scheme="gray", size="2", weight="bold"),
             rx.text("**********", size="3"),
             spacing="1", align_items="start", width="100%", margin_bottom="5",
         ),
         rx.hstack(
             rx.button("Tancar Sessió", on_click=ProfileState.logout, color_scheme="red", variant="soft", size="2", type="button"),
             rx.button("Editar Perfil", on_click=ProfileState.start_editing, color_scheme="blue", size="2", type="button"),
             spacing="3", justify="end", width="100%", margin_top="4",
         ),
        align_items="stretch", width="100%", spacing="3",
    )


def edit_view(state: ProfileState) -> rx.Component:
    """Mostra el formulari d'edició del perfil (Radix - Estructura Simplificada)."""
    return rx.form.root(
        rx.vstack(
            # Missatge general
            rx.cond(
                state.general_message,
                rx.callout.root(
                    rx.callout.icon(rx.icon(tag=rx.cond(state.message_color == "red", "alert-triangle", "check-circle-2"))),
                    rx.callout.text(state.general_message),
                    color_scheme=state.message_color, variant="soft", margin_bottom="4", width="100%", role="alert", ) ),

            # Nom d'usuari (Sense rx.form.control)
            rx.form.field(
                rx.form.label("Nom d'usuari:", html_for="username"),
                # <<< CANVI: Input directament dins de field >>>
                rx.input(
                    id="username", value=state.temp_username, on_change=ProfileState.set_temp_username, required=True, placeholder="El teu nom d'usuari",
                    border_color=rx.cond(state.username_error != "", rx.color("red", 7), None)),
                rx.cond(state.username_error != "", rx.form.message(state.username_error, color_scheme="red", force_match=True)),
                margin_bottom="3", width="100%", name="username", ),

            # Correu electrònic (Sense rx.form.control)
            rx.form.field(
                rx.form.label("Correu electrònic:", html_for="email"),
                 # <<< CANVI: Input directament dins de field >>>
                rx.input(
                    id="email", type="email", value=state.temp_email, on_change=ProfileState.set_temp_email, required=True, placeholder="El teu correu electrònic",
                    border_color=rx.cond(state.email_error != "", rx.color("red", 7), None)),
                rx.cond(state.email_error != "", rx.form.message(state.email_error, color_scheme="red", force_match=True)),
                margin_bottom="3", width="100%", name="email", ),

            # Contrasenya Actual (Sense rx.form.control)
            rx.form.field(
                rx.form.label("Contrasenya Actual:", html_for="current_password"),
                # <<< CANVI: Input directament dins de field >>>
                rx.input(
                    id="current_password", type="password", value=state.current_password, on_change=ProfileState.set_current_password,
                    placeholder="Obligatòria per desar canvis", required=True,
                    border_color=rx.cond(state.password_error.contains("actual"), rx.color("red", 7), None), ),
                 rx.cond(state.password_error.contains("actual"),
                    rx.form.message(state.password_error, color_scheme="red", force_match=True) ),
                 margin_bottom="3", width="100%", name="current_password", ),

            # Nova Contrasenya (Sense rx.form.control)
            rx.form.field(
                rx.form.label("Nova Contrasenya (opcional):", html_for="new_password"),
                # <<< CANVI: Input directament dins de field >>>
                rx.input(
                    id="new_password", type="password", value=state.new_password, on_change=ProfileState.set_new_password, placeholder="Deixar en blanc per no canviar"),
                 margin_bottom="3", width="100%", name="new_password", ),

            # Confirmar Contrasenya (Sense rx.form.control)
            rx.form.field(
                rx.form.label("Confirmar Nova Contrasenya:", html_for="confirm_password"),
                 # <<< CANVI: Input directament dins de field >>>
                rx.input(
                    id="confirm_password", type="password", value=state.confirm_password, on_change=ProfileState.set_confirm_password, placeholder="Repeteix la nova contrasenya",
                    border_color=rx.cond(state.password_error.contains("coincideixen") | state.password_error.contains("Confirma"), rx.color("red", 7), None)),
                 rx.cond(state.password_error.contains("coincideixen") | state.password_error.contains("Confirma"),
                    rx.form.message(state.password_error, color_scheme="red", force_match=True) ),
                 margin_bottom="5", width="100%", name="confirm_password", ),

            # Botons d'acció (sense canvis)
            rx.flex(
                rx.button("Cancel·lar", on_click=ProfileState.cancel_editing, color_scheme="gray", variant="soft", type="button", size="2"),
                rx.form.submit( rx.button( "Desar Canvis", color_scheme="blue", disabled=~state.can_save, size="2" ), as_child=True ),
                justify="end", width="100%", gap="10px", ),

            align_items="stretch", width="100%", spacing="3", ), # Tancament del vstack principal
        on_submit=ProfileState.save_changes, width="100%", ) # Tancament del form.root


# --- Component Principal ---
def profile_component() -> rx.Component:
    """Component funcional per a la pàgina de perfil."""
    return rx.box(
        rx.heading("Perfil d'Usuari", size="7", margin_bottom="6", align="center"),
        rx.flex(
            rx.box( profile_avatar(ProfileState), width=["100%", "30%"], padding_right=["0", "6"], margin_bottom=["6", "0"], ),
            rx.box( rx.cond( ProfileState.is_editing, edit_view(ProfileState), display_view(ProfileState), ), width=["100%", "70%"], ),
            align="start", spacing="6", direction={"base": "column", "md": "row"}, width="100%", max_width="900px", margin="0 auto",
        ),
        padding="6", border="1px solid", border_color=rx.color("gray", 3), border_radius="lg", box_shadow="sm",
    )