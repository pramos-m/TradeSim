import reflex as rx

def custom_upload(**props) -> rx.Component:
    """
    Componente personalizado para la subida de archivos usando input de tipo file.
    """
    return rx.vstack(
        rx.box(
            rx.vstack(
                rx.icon(tag="upload", size=24, color="gray.500"),
                rx.text("Arrastra y suelta una imagen aquí", color="gray.500"),
                rx.text("o haz clic para seleccionarla", color="gray.500", font_size="sm"),
                align="center",
                spacing="2",
            ),
            border="2px dashed",
            border_color="gray.300",
            border_radius="md",
            padding="4",
            width="260px",
            height="260px",
            display="flex",
            justify_content="center",
            align_items="center",
            background="gray.50",
            _hover={
                "border_color": "blue.500",
                "background": "gray.100",
            },
            on_click=props.get("on_click", lambda: rx.set_value("profile-picture-upload", "")),
            cursor="pointer",
        ),
        rx.html(
    """
    <input 
        type="file" 
        id="profile_picture_input" 
        accept=".png,.jpg,.jpeg"
        style="display: none;"
        onchange="
            (function() {
                const file = document.getElementById('profile_picture_input').files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        window.reflexState('ProfileState.handle_file_upload', e.target.result);
                    };
                    reader.readAsDataURL(file);
                }
            })();
        "
    />
    """
        ),
        rx.cond(
            props.get("files"),
            rx.text(
                lambda: props.get("files")[0]["name"] if props.get("files") and len(props.get("files")) > 0 else "",
                color="gray.700",
                font_size="sm",
                margin_top="2",
            ),
        ),
        spacing="2",
        align="center",
    )