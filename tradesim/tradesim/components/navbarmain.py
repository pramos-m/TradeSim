import reflex as rx

PRIMARY_COLOR = "#5271FF"  # Azul para el fondo del avatar
OUTER_GREY_BORDER_COLOR = "#5271FF" # Color del borde exterior gris

# --- AJUSTA EL GROSOR DEL BORDE GRIS AQUÍ ---
OUTER_GREY_BORDER_THICKNESS = "1px" # Prueba con "2px", "2.5px", "3px", etc.

def navbar(user_name: str, user_image_url: str, logo_url: str) -> rx.Component:
    """
    Crea un componente de barra de navegación.

    Args:
        user_name (str): El nombre del usuario.
        user_image_url (str): La URL de la imagen de perfil del usuario.
        logo_url (str): La URL del logo del sitio web.

    Returns:
        rx.Component: El componente de la barra de navegación.
    """
    # print(f"DEBUG: Grosor del borde configurado a: {OUTER_GREY_BORDER_THICKNESS}, Color: {OUTER_GREY_BORDER_COLOR}")

    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.avatar(
                        src=user_image_url,
                        fallback=rx.cond(user_name != "", user_name[:1].upper(), "?"),
                        size="4",
                        bg=PRIMARY_COLOR, # El fondo del avatar es azul
                        # Aplicando el borde con el color y grosor deseados:
                        border=f"{OUTER_GREY_BORDER_THICKNESS} solid {OUTER_GREY_BORDER_COLOR}",
                    ),
                    rx.text(user_name, font_size="1.5em", font_weight="bold"),
                    spacing="3", # Mantén o ajusta según sea necesario
                    align="center",
                    _hover={"opacity": 0.8},
                    transition="all 0.2s ease-in-out",
                ),
                href="/profile",
                _hover={"text_decoration": "none"},
            ),
            rx.spacer(),
            rx.box(
                rx.image(src=logo_url, width="120px"),
                padding="0.5em",
                border_radius="md",
            ),
            width="100%",
            padding="1em",
            bg="white",
            border_bottom="1px solid #ddd",
        ),
        width="100%",
        bg="white",
    )