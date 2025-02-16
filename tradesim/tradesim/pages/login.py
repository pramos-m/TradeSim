# import reflex as rx
# from ..components.layout import layout
# from ..state.auth_state import AuthState

# # Constantes para las imágenes
# BACKGROUND_IMAGE = "/background.png"
# LOGO_IMAGE = "/logo.svg"

# def login_form() -> rx.Component:
#     """Componente del formulario de login."""
#     return rx.box(
#         rx.vstack(
#             rx.heading("Iniciar Sesión", size="9", mb="6"),
#             rx.vstack(
#                 rx.box(
#                     rx.text("EMAIL", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         placeholder="ElonMusk@iCloud.com",
#                         value=AuthState.email,
#                         on_change=AuthState.set_email,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 rx.box(
#                     rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         type_="password",
#                         value=AuthState.password,
#                         on_change=AuthState.set_password,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 spacing="4",
#                 width="100%",
#             ),
#             rx.button(
#                 "Iniciar Sesión",
#                 on_click=AuthState.login,
#                 width="100%",
#                 bg="blue.500",
#                 color="white",
#                 size="3",
#                 _hover={"bg": "blue.600"},
#             ),
#             rx.link(
#                 "¿No tienes cuenta? Regístrate",
#                 on_click=AuthState.set_active_tab("register"),
#                 color="blue.500",
#                 text_align="center",
#                 font_size="1",
#             ),
#             spacing="6",
#             width="100%",
#         ),
#         display=rx.cond(AuthState.active_tab == "login", "block", "none"),
#         bg="transparent",  # Cambiado a transparente
#         padding="8",
#         border_radius="lg",
#         box_shadow="lg",
#     )

# def register_form() -> rx.Component:
#     """Componente del formulario de registro."""
#     return rx.box(
#         rx.vstack(
#             rx.heading("Registro", size="9", mb="6"),
#             rx.vstack(
#                 rx.box(
#                     rx.text("NOMBRE", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         placeholder="Elon Musk",
#                         value=AuthState.username,
#                         on_change=AuthState.set_username,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 rx.box(
#                     rx.text("EMAIL", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         placeholder="ElonMusk@iCloud.com",
#                         value=AuthState.email,
#                         on_change=AuthState.set_email,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 rx.box(
#                     rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         type_="password",
#                         value=AuthState.password,
#                         on_change=AuthState.set_password,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 rx.box(
#                     rx.text("CONFIRMAR CONTRASEÑA", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         type_="password",
#                         value=AuthState.confirm_password,
#                         on_change=AuthState.set_confirm_password,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 spacing="4",
#                 width="100%",
#             ),
#             rx.button(
#                 "Registrarse",
#                 on_click=AuthState.register,
#                 width="100%",
#                 bg="blue.500",
#                 color="white",
#                 size="3",
#                 _hover={"bg": "blue.600"},
#             ),
#             rx.link(
#                 "¿Ya tienes cuenta? Inicia Sesión",
#                 on_click=AuthState.set_active_tab("login"),
#                 color="blue.500",
#                 text_align="center",
#                 font_size="1",
#             ),
#             spacing="6",
#             width="100%",
#         ),
#         display=rx.cond(AuthState.active_tab == "register", "block", "none"),
#         bg="transparent",  # Cambiado a transparente
#         padding="8",
#         border_radius="lg",
#         box_shadow="lg",
#     )

# def login_form() -> rx.Component:
#     """Componente del formulario de login."""
#     return rx.box(
#         rx.vstack(
#             rx.heading("Iniciar Sesión", size="9", mb="6"),
#             # Add error message display
#             rx.cond(
#                 AuthState.error_message,
#                 rx.text(
#                     AuthState.error_message,
#                     color="red.500",
#                     font_size="sm",
#                     text_align="center",
#                 ),
#             ),
#             rx.vstack(
#                 rx.box(
#                     rx.text("EMAIL", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         placeholder="ElonMusk@iCloud.com",
#                         value=AuthState.email,
#                         on_change=AuthState.set_email,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 rx.box(
#                     rx.text("CONTRASEÑA", font_size="1", font_weight="500", color="black"),
#                     rx.input(
#                         type_="password",
#                         value=AuthState.password,
#                         on_change=AuthState.set_password,
#                         bg="gray.100",
#                         border="0px",
#                         size="3",
#                         padding="6",
#                     ),
#                     width="100%",
#                 ),
#                 spacing="4",
#                 width="100%",
#             ),
#             rx.button(
#                 "Iniciar Sesión",
#                 on_click=AuthState.login,
#                 width="100%",
#                 bg="blue.500",
#                 color="white",
#                 size="3",
#                 _hover={"bg": "blue.600"},
#             ),
#             rx.link(
#                 "¿No tienes cuenta? Regístrate",
#                 on_click=AuthState.set_active_tab("register"),
#                 color="blue.500",
#                 text_align="center",
#                 font_size="1",
#             ),
#             spacing="6",
#             width="100%",
#         ),
#         display=rx.cond(AuthState.active_tab == "login", "block", "none"),
#         bg="transparent",
#         padding="8",
#         border_radius="lg",
#         box_shadow="lg",
#     )

import reflex as rx
from ..state.auth_state import AuthState
from ..utils.auth_middleware import public_only

def login_form() -> rx.Component:
    """Login form component."""
    return rx.vstack(
        rx.heading("Iniciar Sesión", size="4"),
        rx.input(
            placeholder="Email",
            value=AuthState.email,
            on_change=AuthState.set_email,
            type_="email",
        ),
        rx.input(
            placeholder="Contraseña",
            value=AuthState.password,
            on_change=AuthState.set_password,
            type_="password",
        ),
        rx.button(
            "Iniciar Sesión",
            on_click=AuthState.login,
            width="100%",
            color_scheme="blue",
            is_loading=AuthState.loading,
        ),
        rx.text(
            "¿No tienes cuenta? Regístrate",
            color="blue.500",
            cursor="pointer",
            on_click=lambda: AuthState.switch_tab("register"),
            text_align="center",
        ),
        width="100%",
        spacing="4",
    )

def register_form() -> rx.Component:
    """Registration form component."""
    return rx.vstack(
        rx.heading("Registro", size="4"),
        rx.input(
            placeholder="Nombre de usuario",
            value=AuthState.username,
            on_change=AuthState.set_username,
        ),
        rx.input(
            placeholder="Email",
            value=AuthState.email,
            on_change=AuthState.set_email,
            type_="email",
        ),
        rx.input(
            placeholder="Contraseña",
            value=AuthState.password,
            on_change=AuthState.set_password,
            type_="password",
        ),
        rx.input(
            placeholder="Confirmar Contraseña",
            value=AuthState.confirm_password,
            on_change=AuthState.set_confirm_password,
            type_="password",
        ),
        rx.button(
            "Registrarse",
            on_click=AuthState.register,
            width="100%",
            color_scheme="blue",
            is_loading=AuthState.loading,
        ),
        rx.text(
            "¿Ya tienes cuenta? Inicia Sesión",
            color="blue.500",
            cursor="pointer",
            on_click=lambda: AuthState.switch_tab("login"),
            text_align="center",
        ),
        width="100%",
        spacing="4",
    )

@public_only
def login_page() -> rx.Component:
    """Login/Register page."""
    return rx.center(
        rx.vstack(
            rx.image(src="/logo.svg", height="40px"),
            rx.box(
                rx.cond(
                    AuthState.error_message != "",
                    rx.text(
                        AuthState.error_message,
                        color="red.500",
                        margin_bottom="4",
                    ),
                ),
                rx.cond(
                    AuthState.active_tab == "login",
                    login_form(),
                    register_form(),
                ),
                padding="6",
                bg="white",
                border_radius="lg",
                box_shadow="lg",
                width="100%",
                max_width="400px",
            ),
            spacing="8",
            width="100%",
        ),
        padding_y="8",
        width="100%",
        min_height="100vh",
        background="url('/background.png')",
        background_size="cover",
    )
