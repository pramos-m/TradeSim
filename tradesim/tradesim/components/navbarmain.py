# tradesim/tradesim/components/navbarmain.py

import reflex as rx

def navbar(user_name: str, user_image_url: str, logo_url: str) -> rx.Component:
    """
    Creates a navbar component.

    Args:
        user_name (str): The name of the user.
        user_image_url (str): The URL of the user's profile picture.
        logo_url (str): The URL of the website's logo.

    Returns:
        rx.Component: The navbar component.
    """
    return rx.box(
        rx.hstack(
            # Profile Section (Left Side)
            rx.hstack(
                rx.avatar(src=user_image_url, name=user_name, size="3"),  # Use a valid size value
                rx.text(user_name, font_size="1em", font_weight="bold"),  # User's name
                spacing="2",
                align="center",
            ),
            # Spacer to push the logo to the far right
            rx.spacer(),
            # Logo (Far Right)
            rx.image(src=logo_url, width="100px"),  # Website logo
            width="100%",  # Ensure the navbar spans the full width
            padding="1em",  # Add some padding
            bg="blue",  # Set the background color of the navbar to blue
            border_bottom="1px solid #ddd",  # Add a border at the bottom
        ),
        width="100%",  # Ensure the navbar spans the full width
        bg="blue",  # Set the background color of the entire navbar to blue
    )