import reflex as rx

def callout(message: str, color_scheme: str = "gray", size: str = "1", margin_top: str = "1em") -> rx.Component:
    """Custom callout component."""
    return rx.box(
        rx.hstack(
            rx.icon(tag="info", color=f"var(--{color_scheme}-500)", size=24),  # Icon size in pixels
            rx.text(message, color=f"var(--{color_scheme}-700)", size=size),
            spacing="2",  # Changed from '0.5em' to '2' (allowed value)
        ),
        padding="1em",
        border=f"1px solid var(--{color_scheme}-300)",
        border_radius="0.5em",
        background_color=f"var(--{color_scheme}-100)",
        margin_top=margin_top,
    )