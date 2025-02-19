
# gradient color for fields "#555555"
# botones tipo no tienes cuenta? "#5271FF"

import reflex as rx
from ..state.auth_state import AuthState
from ..utils.auth_middleware import public_only

# Constantes para las imágenes
BACKGROUND_IMAGE = "./background.png"
LOGO_IMAGE = "./logo.svg"

def login_form() -> rx.Component:
    """Componente del formulario de login."""
    return rx.box(
        rx.vstack(
            rx.heading("Iniciar Sesión", size="9", mb="6"),
            rx.cond(
                AuthState.error_message != "",
                rx.text(
                    AuthState.error_message,
                    color="#5271FF",
                    font_size="sm",
                    text_align="center",
                ),
            ),
            rx.vstack(
                rx.box(
                    rx.text("EMAIL", font_size="1", font_weight="500", color="black"),
                    rx.input(
                        placeholder="ElonMusk@iCloud.com",
                        value=AuthState.email,
                        on_change=AuthState.set_email,
                        bg="gray.100",
                        border="0px",
                        size="3",
                        padding="6",
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"),
                    rx.input(
                        type_="password",
                        value=AuthState.password,
                        on_change=AuthState.set_password,
                        bg="gray.100",
                        border="0px",
                        size="3",
                        padding="6",
                    ),
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.button(
                "Iniciar Sesión",
                on_click=AuthState.login,
                width="100%",
                bg="#5271FF",
                color="white",
                size="3",
                _hover={"bg": "blue.600"},
                is_loading=AuthState.loading,
            ),
            rx.link(
                "¿No tienes cuenta? Regístrate",
                on_click=lambda: AuthState.set_active_tab("register"),
                color="#5271FF",
                text_align="center",
                font_size="1",
            ),
            spacing="6",
            width="100%",
        ),
        bg="transparent",
        padding="8",
        border_radius="lg",
        box_shadow="lg",
    )

def register_form() -> rx.Component:
    """Componente del formulario de registro."""
    return rx.box(
        rx.vstack(
            rx.heading("Registro", size="9", mb="6"),
            rx.cond(
                AuthState.error_message != "",
                rx.text(
                    AuthState.error_message,
                    color="red.500",
                    font_size="sm",
                    text_align="center",
                ),
            ),
            rx.vstack(
                rx.box(
                    rx.text("NOMBRE", font_size="1", font_weight="500", color="black"),
                    rx.input(
                        placeholder="Elon Musk",
                        value=AuthState.username,
                        on_change=AuthState.set_username,
                        bg="gray.100",
                        border="0px",
                        size="3",
                        padding="6",
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.text("EMAIL", font_size="1", font_weight="500", color="black"),
                    rx.input(
                        placeholder="ElonMusk@iCloud.com",
                        value=AuthState.email,
                        on_change=AuthState.set_email,
                        bg="gray.100",
                        border="0px",
                        size="3",
                        padding="6",
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"),
                    rx.input(
                        type_="password",
                        value=AuthState.password,
                        on_change=AuthState.set_password,
                        bg="gray.100",
                        border="0px",
                        size="3",
                        padding="6",
                    ),
                    width="100%",
                ),
                rx.box(
                    rx.text("CONFIRMAR CONTRASEÑA", font_size="1", font_weight="500", color="black"),
                    rx.input(
                        type_="password",
                        value=AuthState.confirm_password,
                        on_change=AuthState.set_confirm_password,
                        bg="gray.100",
                        border="0px",
                        size="3",
                        padding="6",
                    ),
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.button(
                "Registrarse",
                on_click=AuthState.register,
                width="100%",
                bg="#5271FF",
                color="white",
                size="3",
                _hover={"bg": "blue.600"},
                is_loading=AuthState.loading,
            ),
            rx.link(
                "¿Ya tienes cuenta? Inicia Sesión",
                on_click=lambda: AuthState.set_active_tab("login"),
                color="#5271FF",
                text_align="center",
                font_size="1",
            ),
            spacing="6",
            width="100%",
        ),
        bg="transparent",
        padding="8",
        border_radius="lg",
        box_shadow="lg",
    )

@public_only
def login_page() -> rx.Component:
    """Página principal de login."""
    return rx.box(
        # Contenedor principal con fondo
        rx.box(
            rx.image(
                src=BACKGROUND_IMAGE,
                position="fixed",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                object_fit="cover",
                z_index="-1",
                border="2px solid red",  # Borde temporal para depuración
            ),
        ),
        # Logo en la esquina superior izquierda
        rx.box(
            rx.image(src="/logo.svg", height="200px"),
            position="absolute",
            top="0",
            left="20px",
        ),
        # Contenedor del formulario a la derecha
        rx.hstack(
            rx.spacer(),  # Esto empuja el contenido hacia la derecha
            rx.box(
                rx.cond(
                    AuthState.active_tab == "login",
                    login_form(),
                    register_form(),
                ),
                width="50%",
                height="100vh",
                display="flex",
                align_items="center",
                justify_content="center",
            ),
        ),
        width="100vw",
        height="100vh",
        position="relative",
        background="url('/background.png')",
        background_size="cover",
    )