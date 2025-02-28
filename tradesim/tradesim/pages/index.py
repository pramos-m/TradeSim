import reflex as rx
from ..components.layouts.landing_layout import landing_layout
from ..components.buttons import navbar_button, comenzar_button
from ..state.auth_state import AuthState

LOGO_IMAGE = "./logo.svg"

def index_content() -> rx.Component:
    """Landing page content responsive."""
    return rx.box(
        # Logo con posición responsiva
        rx.box(
            rx.image(
                src="/logo.svg",
                height=["60px", "100px", "150px", "200px"],
                width="auto",
            ),
            position="absolute",
            top=["10px", "10px", "10px", "0"],
            left=["10px", "15px", "20px", "20px"],
            z_index="1",
        ),
        
        # Botón de navegación
        rx.box(
            rx.link(
                navbar_button(),
                href="/login",
            ),
            position="absolute",
            top=["10px", "20px", "40px", "60px"],
            right=["10px", "15px", "40px", "70px"],
            z_index="2",
        ),
        
        # DISEÑO UNIFICADO - Posición consistente en todos los tamaños
        rx.vstack(
            rx.box(
                rx.vstack(
                    # Primer título "Bienvenido"
                    rx.box(
                        rx.heading(
                            "Bienvenido",
                            font_family="mono",
                            font_size=["35px", "60px", "100px", "150px"],
                            white_space="nowrap",
                            color="black",
                            letter_spacing="tight",
                            font_weight="bold",
                        ),
                        bg="white",
                        padding=["10px", "15px", "25px", "40px"],
                        margin="0",
                        border_top_left_radius=["15px", "15px", "20px", "20px"],
                        border_top_right_radius=["15px", "15px", "20px", "20px"],
                        border_bottom_left_radius="0px",
                        border_bottom_right_radius=["-10px", "-15px", "-20px", "-20px"],
                        box_shadow="sm",
                        width=["200px", "350px", "500px", "750px"],
                        height=["auto", "auto", "120px", "175px"],
                        text_align="center",
                        justify_content="center",
                        display="flex",
                        align_items="center",
                        overflow="hidden",
                    ),
                    
                    # Segundo título "a TradeSim!!!"
                    rx.box(
                        rx.heading(
                            "a TradeSim!!!",
                            font_family="mono",
                            font_size=["35px", "60px", "100px", "150px"],
                            white_space="nowrap",
                            color="black",
                            letter_spacing="tight",
                            font_weight="bold",
                        ),
                        bg="white",
                        padding=["10px", "15px", "25px", "40px"],
                        margin="0",
                        border_top_left_radius="0px",
                        border_top_right_radius=["15px", "15px", "20px", "20px"],
                        border_bottom_left_radius=["15px", "15px", "20px", "20px"],
                        border_bottom_right_radius=["15px", "15px", "20px", "20px"],
                        box_shadow="sm",
                        width=["240px", "420px", "600px", "925px"],
                        height=["auto", "auto", "120px", "175px"],
                        text_align="center",
                        justify_content="center",
                        display="flex",
                        align_items="center",
                        overflow="hidden",
                    ),
                    spacing="0",
                    align_items="flex-start",
                    position="relative",
                ),
                # Margen consistente en todos los tamaños: 150px desde arriba
                margin_top=["150px", "150px", "150px", "150px"],
                padding_top="0",
            ),
            
            # Botón de comenzar
            rx.link(
                comenzar_button(),
                href="/login",
                margin_top=["25px", "40px", "60px", "80px"],
            ),
            # Posicionamiento consistente en todos los tamaños
            position="relative", # Cambiado a relative en todos los tamaños
            top="auto", # Eliminamos el posicionamiento vertical absoluto
            left="auto", # Eliminamos el posicionamiento horizontal absoluto
            align_items=["center", "center", "flex-start", "flex-start"],
            width="100%",
            justify_content=["center", "center", "flex-start", "flex-start"],
            padding_left=["0", "0", "5%", "10%"], # Desplazamiento horizontal controlado por padding
        ),
        width="100%",
        height="100vh",
        min_height="100vh",
        position="relative",
        overflow_x="hidden",
        display="flex",
        flex_direction="column",
    )

def index() -> rx.Component:
    # Asegurarnos de que no haya redirecciones basadas en autenticación
    # Eliminar cualquier rx.cond() o similar que redirija basado en AuthState.is_authenticated
    return landing_layout(index_content())

# Configure the page
index = rx.page(
    route="/",
    title="TradeSim - Inicio",