# tradesim/components/layouts/landing_layout.py
import reflex as rx

def landing_layout(content: rx.Component) -> rx.Component:
    """Layout specifically for the landing page."""
    return rx.box(
        rx.box(
            rx.image(
                src="/home.svg",
                position="absolute",
                top="0",
                left="0",
                width="100vw",
                height="100vh",
                object_fit="cover",
                z_index="0",
                opacity="0.7",
            ),
            bg="rgb(82, 109, 254)",
            width="100%",
            height="100vh",
            position="fixed",
        ),
        rx.box(
            content,
            position="relative",
            z_index="1",
        ),
        width="100%",
        height="100vh",
        position="relative",
        overflow_x="hidden",
    )