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
                rx.avatar(src=user_image_url, name=user_name, size="4"),  # Adjust the size of the profile picture
                rx.text(user_name, font_size="1.5em", font_weight="bold"),  # Adjust the font size of the username
                spacing="2",
                align="center",
            ),
            # Spacer to push the logo to the far right
            rx.spacer(),
            # Logo (Far Right)
            rx.box(
                rx.image(src=logo_url, width="120px"),  # Adjust the width of the logo
                padding="0.5em",  # Add some padding around the logo
                border_radius="md",  # Add border radius to the logo box
            ),
            width="100%",  # Ensure the navbar spans the full width
            padding="1em",  # Add some padding
            bg="white",  # Set the background color of the navbar
            border_bottom="1px solid #ddd",  # Add a border at the bottom
        ),
        width="100%",  # Ensure the navbar spans the full width
        bg="white",  # Set the background color of the entire navbar
    )