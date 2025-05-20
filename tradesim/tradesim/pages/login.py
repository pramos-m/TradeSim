# tradesim/pages/login.py
import reflex as rx
# Asegúrate de importar AuthState para usarlo en la UI
from ..state.auth_state import AuthState
# Importar el middleware si lo usas (public_only o require_auth según corresponda)
from ..utils.auth_middleware import public_only # O el que uses para páginas públicas
# Importar componentes (si usas navbar/footer aquí)
# from ..components.navbar import navbar
# from ..components.footer import footer
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Componentes UI ---
def login_form() -> rx.Component:
    """Componente del formulario de login."""
    return rx.form(
        rx.vstack(
            rx.heading("Iniciar Sesión", size="9", mb="6"),
            rx.cond( AuthState.error_message != "", rx.text(AuthState.error_message, color="#5271FF", font_size="2", text_align="center")),
            rx.vstack(
                rx.box( rx.text("EMAIL", font_size="1", font_weight="500", color="black"), rx.input( placeholder="ElonMusk@iCloud.com", value=AuthState.email, on_change=AuthState.set_email, bg="gray.100", border="0px", size="3", padding="6"), width="100%"),
                rx.box( 
                    rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"), 
                    rx.hstack(
                        rx.input( 
                            id="password-input",
                            custom_attrs={"type": AuthState.password_field_type},
                            value=AuthState.password, 
                            on_change=AuthState.set_password,
                            bg="gray.100", 
                            border="0px", 
                            size="3", 
                            padding="6",
                            width="75%"
                        ),
                        rx.button(
                            rx.cond(
                                AuthState.show_password,
                                rx.text("Ocultar", font_size="1"),
                                rx.text("Mostrar", font_size="1"),
                            ),
                            bg="blue.100",
                            border="0px",
                            size="3",
                            padding="6",
                            width="25%",
                            on_click=AuthState.toggle_password_visibility,
                        ),
                    ),
                    width="100%"
                ),
                spacing="4", width="100%",
            ),
            rx.button("Iniciar Sesión", on_click=AuthState.login, width="100%", bg="#5271FF", color="white", size="3", _hover={"bg": "blue.600"}, is_loading=AuthState.loading, type_="submit"),
            rx.link("¿No tienes cuenta? Regístrate", on_click=lambda: AuthState.set_active_tab("register"), color="#5271FF", text_align="center", font_size="1"),
            spacing="6", width="100%",
        ),
        bg="transparent", padding="8", border_radius="lg", box_shadow="lg", on_submit=AuthState.login, width="100%", max_width="400px", display="block", align_items="stretch", style={"width": "100%", "display": "block"}
    )

def register_form() -> rx.Component:
    """Componente del formulario de registro."""
    return rx.form(
        rx.vstack(
            rx.heading("Registro", size="9", mb="6"),
            rx.cond( AuthState.error_message != "", rx.text( AuthState.error_message, color="red.500", font_size="sm", text_align="center")),
            rx.vstack(
                rx.box( rx.text("NOMBRE", font_size="1", font_weight="500", color="black"), rx.input( placeholder="Elon Musk", value=AuthState.username, on_change=AuthState.set_username, bg="gray.100", border="0px", size="3", padding="6"), width="100%"),
                rx.box( rx.text("EMAIL", font_size="1", font_weight="500", color="black"), rx.input( placeholder="ElonMusk@iCloud.com", value=AuthState.email, on_change=AuthState.set_email, bg="gray.100", border="0px", size="3", padding="6"), width="100%"),
                rx.box( 
                    rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"), 
                    rx.input( 
                        # Reemplazamos type_="password" con custom_attrs
                        custom_attrs={"type": "password"},
                        value=AuthState.password, 
                        on_change=AuthState.set_password,
                        bg="gray.100", 
                        border="0px", 
                        size="3", 
                        padding="6"
                    ), 
                    width="100%"
                ),
                rx.box( 
                    rx.text("CONFIRMAR CONTRASEÑA", font_size="1", font_weight="500", color="black"), 
                    rx.input( 
                        # Reemplazamos type_="password" con custom_attrs
                        custom_attrs={"type": "password"},
                        value=AuthState.confirm_password, 
                        on_change=AuthState.set_confirm_password,
                        bg="gray.100", 
                        border="0px", 
                        size="3", 
                        padding="6"
                    ), 
                    width="100%"
                ),
                spacing="4", width="100%",
            ),
            rx.button("Registrarse", on_click=AuthState.register, width="100%", bg="#5271FF", color="white", size="3", _hover={"bg": "blue.600"}, is_loading=AuthState.loading, type_="submit"),
            rx.link("¿Ya tienes cuenta? Inicia Sesión", on_click=lambda: AuthState.set_active_tab("login"), color="#5271FF", text_align="center", font_size="1"),
            spacing="6", width="100%",
        ),
        bg="transparent", padding="8", border_radius="lg", box_shadow="lg", on_submit=AuthState.register, width="100%", max_width="400px", display="block", align_items="stretch", style={"width": "100%", "display": "block"}
    )

# --- Estructura de la Página ---
@public_only # Este decorador es importante aquí
def login_page() -> rx.Component:
    """Página principal de login."""
    return rx.box(
        rx.box( # Fondo
            rx.image(src="/background.svg", position="fixed", top="0", left="0", width="100vw", height="100vh", object_fit="cover", z_index="-1"),
        ),
        rx.box( # Logo
            rx.image(src="/logo.svg", height="200px"), position="absolute", top="0", left="20px",
        ),
        rx.hstack( # Contenedor formulario
            rx.spacer(),
            rx.box(
                rx.cond(AuthState.active_tab == "login", login_form(), register_form()),
                width="50%", height="100vh", display="flex", align_items="center", justify_content="center",
            ),
        ),
        width="100vw", height="100vh", position="relative",
        background="url('/background.svg')", background_size="cover",
    )

# Configuración de la página
login = rx.page(
    route="/login",
    title="TradeSim - Login",
    # on_load=AuthState.on_load # <--- LÍNEA ELIMINADA/COMENTADA
)(login_page)