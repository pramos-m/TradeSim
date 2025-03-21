import reflex as rx

def navbar(user_name: str, user_image_url: str, logo_url: str) -> rx.Component:
    """
    Creates a navbar component with a clickable username that navigates to the profile page.

    Args:
        user_name (str): The name of the user.
        user_image_url (str): The URL of the user's profile picture.
        logo_url (str): The URL of the website's logo.

    Returns:
        rx.Component: The navbar component.
    """
    return rx.box(
        rx.hstack(
            # Profile Section (Left Side) - Now clickable
            rx.link(
                rx.hstack(
                    # Use rx.cond instead of Python's or operator
                    rx.cond(
                        user_image_url != "",
                        rx.avatar(src=user_image_url, name=user_name, size="4"),
                        rx.avatar(name=user_name, size="4")
                    ),
                    rx.text(user_name, font_size="1.5em", font_weight="bold"),
                    spacing="2",
                    align="center",
                    _hover={"opacity": 0.8},
                    transition="all 0.2s ease-in-out",
                ),
                href="/profile",
                _hover={"text_decoration": "none"},
            ),
            # Spacer to push the logo to the far right
            rx.spacer(),
            # Logo (Far Right)
            rx.box(
                rx.image(src=logo_url, width="120px"),
                padding="0.5em",
                border_radius="md",
            ),
            width="100%",
            padding="1em",
            bg="white",
            border_bottom="1px solid #ddd",
            position="fixed",
            top="0",
            left="0",
            z_index="100",
        ),
        width="100%",
        bg="white",
    )