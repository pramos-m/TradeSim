import reflex as rx

def sidebar() -> rx.Component:
    """
    Creates a sidebar component with icon buttons.

    Returns:
        rx.Component: The sidebar component.
    """
    return rx.box(
        rx.vstack(
            # Dashboard Button
            rx.image(
                src="/dashboard.png",  # Path to the dashboard icon
                width="40px",
                cursor="pointer",
                on_click=lambda: rx.redirect("/dashboard"),
            ),
            # Clasificacion Button
            rx.image(
                src="/clasificacion.png",  # Path to the clasificacion icon
                width="40px",
                cursor="pointer",
                on_click=lambda: rx.redirect("/clasificacion"),
            ),
            # Noticias Button
            rx.image(
                src="/noticias.png",  # Path to the noticias icon
                width="40px",
                cursor="pointer",
                on_click=lambda: rx.redirect("/noticias"),
            ),
            # Buscador Button
            rx.image(
                src="/buscador.png",  # Path to the buscador icon
                width="40px",
                cursor="pointer",
                on_click=lambda: rx.redirect("/buscador"),
            ),
            spacing="9",  # Increased spacing value (e.g., "8")
            align="center",  # Center-align buttons horizontally
            justify="center",  # Center-align buttons vertically
            height="100%",  # Take up full height of the sidebar
            padding_y="2",  # Add padding at the top and bottom
        ),
        width="90px",  # Width of the sidebar
        height="100vh",  # Full height of the viewport
        bg="white",  # Background color of the sidebar
        border_right="1px solid #ddd",  # Right border for separation
    )