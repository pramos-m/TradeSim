import reflex as rx
from ..state.profile_state import ProfileState
from ..utils.auth_middleware import require_auth
from ..state.auth_state import AuthState
from ..components.sidebar import sidebar
from ..components.layout import layout

@rx.page(
    route="/profile",
    title="TradeSim - Perfil",
    on_load=[
        AuthState.on_load,
        ProfileState.load_profile
    ]
)
@require_auth
def profile_page() -> rx.Component:
    return layout(
        rx.box(
            rx.vstack(
                # Título principal
                rx.heading(
                    "Perfil",
                    size="6",
                    margin_y="50",
                    align_self="flex-start",
                    margin_left="30px",
                    margin_top="20px",
                ),
                # Contenedor principal
                rx.flex(
                    # Tarjeta 1: Foto de Perfil
                    rx.box(
                        rx.vstack(
                            rx.heading(
                                "FOTO DE PERFIL", 
                                size="4", 
                                font_weight="bold", 
                                margin_bottom="6", 
                                color="black",
                                padding_top="2",
                                align_self="flex-start"
                            ),
                            rx.cond(
                                ProfileState.profile_picture != "",
                                rx.image(
                                    src=ProfileState.profile_picture,
                                    width="200px", 
                                    height="200px", 
                                    border_radius="20px",
                                    object_fit="cover",
                                    border="3px solid",
                                    border_color="blue.400"
                                ),
                                rx.box(
                                    rx.vstack(
                                        rx.icon(
                                            tag="image",
                                            color="gray.400",
                                            font_size="4xl"
                                        ),
                                        rx.text(
                                            "Añadir Foto", 
                                            color="gray.500",
                                            margin_top="2"
                                        ),
                                    ),
                                    width="200px", 
                                    height="200px", 
                                    border="2px dashed", 
                                    border_color="gray.300",
                                    border_radius="20px",
                                    display="flex",
                                    justify_content="center",
                                    align_items="center"
                                )
                            ),
                            rx.html("""
                                <input 
                                    type="file" 
                                    id="profile_picture_input" 
                                    accept="image/png,image/jpeg,image/jpg"
                                    style="display: none;"
                                />
                            """),
                            rx.script("""
                                document.addEventListener('DOMContentLoaded', function() {
                                    const input = document.getElementById('profile_picture_input');
                                    if (input) {
                                        input.addEventListener('change', function() {
                                            const file = input.files[0];
                                            if (file) {
                                                const reader = new FileReader();
                                                reader.onload = function(e) {
                                                    const base64Image = e.target.result;
                                                    const event = new CustomEvent('ProfileState.handle_file_upload', {
                                                        detail: {
                                                            content: base64Image,
                                                            type: file.type
                                                        }
                                                    });
                                                    document.dispatchEvent(event);
                                                };
                                                reader.readAsDataURL(file);
                                            }
                                        });
                                    }
                                });
                            """),
                            rx.button(
                                rx.hstack(
                                    rx.icon(tag="pencil", font_size="sm"),
                                    rx.text("Editar Foto"),
                                    spacing="2"
                                ),
                                width="100%",
                                margin_top="16px",
                                color="white",
                                background="rgb(86, 128, 255)",
                                border_radius="12px",
                                _hover={"background": "rgb(70, 110, 230)"},
                                padding_y="2",
                                on_click=rx.call_script(
                                    'document.getElementById("profile_picture_input").click()'
                                )
                            ),
                            align_items="center",
                            padding="8",
                            width="100%",
                            height="100%"
                        ),
                        background="#ededed",
                        border_radius="32px",
                        width={
                            "base": "100%",
                            "md": "320px"
                        },
                        min_height="420px",
                        padding="24px",
                        margin_left="32px",
                        margin_right={
                            "base": "0",
                            "md": "0"
                        },
                        margin_bottom={
                            "base": "6",
                            "md": "0"
                        }
                    ),
                    # Tarjeta 2: Información de Perfil
                    rx.box(
                        rx.vstack(
                            rx.heading(
                                "INFORMACIÓN DE PERFIL", 
                                size="4", 
                                font_weight="bold", 
                                margin_bottom="6", 
                                color="black",
                                padding_top="2",
                                align_self="flex-start"
                            ),
                            rx.cond(
                                ProfileState.is_editing,
                                # Modo edición
                                rx.vstack(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="user", color="blue.500"),
                                            rx.text("NOMBRE:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.input(
                                            value=ProfileState.temp_username,
                                            on_change=ProfileState.set_temp_username,
                                            placeholder="Nombre de usuario",
                                            width="100%",
                                            border_radius="md",
                                            border="1px solid",
                                            border_color="gray.300",
                                            padding="2"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="3",
                                        spacing="2",
                                    ),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="mail", color="blue.500"),
                                            rx.text("EMAIL:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.input(
                                            type_="email",
                                            value=ProfileState.temp_email,
                                            on_change=ProfileState.set_temp_email,
                                            placeholder="Email",
                                            width="100%",
                                            border_radius="md",
                                            border="1px solid",
                                            border_color="gray.300",
                                            padding="2"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="3",
                                        spacing="2",
                                    ),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="lock", color="blue.500"),
                                            rx.text("CONTRASEÑA ACTUAL:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.input(
                                            type_="password",
                                            value=ProfileState.current_password,
                                            on_change=ProfileState.set_current_password,
                                            placeholder="Requerida para guardar cambios",
                                            width="100%",
                                            border_radius="md",
                                            border="1px solid",
                                            border_color="gray.300",
                                            padding="2"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="3",
                                        spacing="2",
                                    ),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="key", color="blue.500"),
                                            rx.text("NUEVA CONTRASEÑA:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.input(
                                            type_="password",
                                            value=ProfileState.temp_password,
                                            on_change=ProfileState.set_temp_password,
                                            placeholder="Dejar en blanco para no cambiar",
                                            width="100%",
                                            border_radius="md",
                                            border="1px solid",
                                            border_color="gray.300",
                                            padding="2"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="3",
                                        spacing="2",
                                    ),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="check", color="blue.500"),
                                            rx.text("CONFIRMAR CONTRASEÑA:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.input(
                                            type_="password",
                                            value=ProfileState.profile_confirm_password,
                                            on_change=ProfileState.set_confirm_password,
                                            placeholder="Confirmar nueva contraseña",
                                            width="100%",
                                            border_radius="md",
                                            border="1px solid",
                                            border_color="gray.300",
                                            padding="2"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="3",
                                        spacing="2",
                                    ),
                                    rx.cond(
                                        ProfileState.edit_error != "",
                                        rx.text(
                                            ProfileState.edit_error,
                                            color="red.500",
                                            font_size="sm",
                                            margin_top="2",
                                            padding="2",
                                            border_radius="md",
                                            background="red.50"
                                        )
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            rx.hstack(
                                                rx.icon(tag="check", font_size="sm"),
                                                rx.text("Guardar Cambios"),
                                                spacing="2"
                                            ),
                                            color="white",
                                            background="rgb(86, 128, 255)",
                                            _hover={"background": "rgb(70, 110, 230)"},
                                            border_radius="md",
                                            on_click=ProfileState.save_profile_changes,
                                            width="48%",
                                            padding_y="2"
                                        ),
                                        rx.button(
                                            rx.hstack(
                                                rx.icon(tag="x", font_size="sm"),
                                                rx.text("Cancelar"),
                                                spacing="2"
                                            ),
                                            color="gray.700",
                                            background="white",
                                            border="1px solid",
                                            border_color="gray.300",
                                            _hover={"background": "rgb(245, 245, 245)"},
                                            border_radius="md",
                                            on_click=ProfileState.cancel_edit,
                                            width="48%",
                                            padding_y="2"
                                        ),
                                        width="100%",
                                        margin_top="6",
                                        spacing="4",
                                        justify_content="space-between",
                                        padding_x="5%",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                    width="100%",
                                ),
                                # Modo visualización
                                rx.vstack(
                                    # NOMBRE
                                    rx.hstack(
                                        rx.icon(tag="user", color="black", box_size="7"),
                                        rx.text("NOMBRE:", font_weight="bold", color="black", font_size="xl"),
                                    ),
                                    rx.text(
                                        ProfileState.username, 
                                        font_size="xl",
                                        color="black",
                                        margin_left="48px",
                                        margin_top="-16px",
                                        margin_bottom="18px"
                                    ),
                                    # EMAIL
                                    rx.hstack(
                                        rx.icon(tag="mail", color="black", box_size="7"),
                                        rx.text("EMAIL:", font_weight="bold", color="black", font_size="xl"),
                                    ),
                                    rx.text(
                                        ProfileState.email, 
                                        font_size="xl",
                                        color="black",
                                        margin_left="48px",
                                        margin_top="-16px",
                                        margin_bottom="18px"
                                    ),
                                    # CONTRASEÑA
                                    rx.hstack(
                                        rx.icon(tag="shield", color="black", box_size="7"),
                                        rx.text("CONTRASEÑA:", font_weight="bold", color="black", font_size="xl"),
                                    ),
                                    rx.text(
                                        "**********", 
                                        font_size="xl",
                                        color="black",
                                        margin_left="48px",
                                        margin_top="-16px",
                                        margin_bottom="18px"
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            rx.text("Editar Información", color="black", font_size="lg"),
                                            color="black",
                                            background="white",
                                            border_radius="16px",
                                            border="none",
                                            _hover={"background": "#f0f0f0"},
                                            on_click=ProfileState.edit_profile,
                                            width="48%",
                                            padding_y="18px",
                                            font_weight="bold"
                                        ),
                                        rx.button(
                                            rx.text("Cerrar Sesion", color="white", font_size="lg"),
                                            color="white",
                                            background="#c62828",
                                            border_radius="16px",
                                            border="none",
                                            _hover={"background": "#b71c1c"},
                                            on_click=ProfileState.logout,
                                            width="48%",
                                            padding_y="18px",
                                            font_weight="bold"
                                        ),
                                        width="100%",
                                        margin_top="24px",
                                        spacing="4",
                                        justify_content="space-between",
                                        padding_x="0",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                    width="100%",
                                ),
                            ),
                            spacing="4",
                            align_items="stretch",
                            padding="32px",
                            width="100%",
                            height="100%"
                        ),
                        background="#ededed",
                        border_radius="32px",
                        flex="1",
                        min_height="420px",
                        max_width="600px",
                        margin_left="32px"
                    ),
                    flex_direction={
                        "base": "column",
                        "md": "row"
                    },
                    align_items="stretch",
                    width="100%",
                    gap="32px"
                ),
                spacing="8",
                width="100%",
                align_items="flex-start",
                padding={
                    "base": "4",
                    "md": "6"
                },
                max_width="1400px",
            ),
            width="100%",
            padding={
                "base": "2",
                "md": "6 6 6 260px",
            },
            overflow_x="hidden"
        )
    )

profile = profile_page