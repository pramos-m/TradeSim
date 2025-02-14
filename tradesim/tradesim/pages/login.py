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

# /pages/login.py
import reflex as rx
from ..state.auth_state import AuthState

def login_page():
    """Login and registration page."""
    return rx.box(
        rx.vstack(
            rx.image(src="/logo.svg", height="40px", margin_bottom="4"),
            # Add error message display
            rx.cond(
                AuthState.error_message,
                rx.text(
                    AuthState.error_message,
                    color="red.500",
                    font_size="sm",
                    text_align="center",
                ),
            ),
            rx.box(
                rx.cond(
                    AuthState.active_tab == "login",
                    login_form(),
                    register_form(),
                ),
                width="100%",
                max_width="400px",
                padding="6",
                bg="white",
                border_radius="lg",
                box_shadow="lg",
            ),
            spacing="4",
            align_items="center",
            padding_y="8",
            width="100%",
            height="100vh",
            justify_content="center",
        ),
        background_image=f"url('/background.png')",
        background_size="cover",
        background_position="center",
    )

def login_form() -> rx.Component:
    """Componente del formulario de login."""
    return rx.box(
        rx.vstack(
            rx.heading("Iniciar Sesión", size="9", mb="6"),
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
                bg="blue.500",
                color="white",
                size="3",
                _hover={"bg": "blue.600"},
            ),
            rx.link(
                "¿No tienes cuenta? Regístrate",
                on_click=lambda: AuthState.set_active_tab("register"),  # Using lambda to fix function call
                color="blue.500",
                text_align="center",
                font_size="1",
            ),
            spacing="6",
            width="100%",
        ),
        width="100%",
    )

def register_form() -> rx.Component:
    """Componente del formulario de registro."""
    return rx.box(
        rx.vstack(
            rx.heading("Registro", size="9", mb="6"),
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
                bg="blue.500",
                color="white",
                size="3",
                _hover={"bg": "blue.600"},
            ),
            rx.link(
                "¿Ya tienes cuenta? Inicia Sesión",
                on_click=lambda: AuthState.set_active_tab("login"),  # Using lambda for proper function call
                color="blue.500",
                text_align="center",
                font_size="1",
            ),
            spacing="6",
            width="100%",
        ),
        width="100%",
    )


