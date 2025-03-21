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
                # Título principal con mejor espaciado
                rx.text(
                    "Perfil", 
                    font_size="2xl", 
                    font_weight="bold", 
                    margin_bottom="8", 
                    align_self="flex-start",
                    padding_top="4"
                ),
                
                # Contenedor principal mejorado - Convertido a flex responsivo
                rx.flex(
                    # Tarjeta 1: Foto de Perfil
                    rx.box(
                        rx.vstack(
                            # Título de la tarjeta con mejor espaciado
                            rx.heading(
                                "FOTO DE PERFIL", 
                                size="4", 
                                font_weight="bold", 
                                margin_bottom="6", 
                                color="black",
                                padding_top="2",
                                align_self="flex-start"
                            ),
                            # Contenido condicional mejorado
                            rx.cond(
                                ProfileState.profile_picture != "",
                                rx.image(
                                    src=ProfileState.profile_picture,
                                    width="200px", 
                                    height="200px", 
                                    border_radius="full",
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
                                    border_radius="full",
                                    display="flex",
                                    justify_content="center",
                                    align_items="center"
                                )
                            ),
                            # Input para subida de archivos
                            rx.html("""
                                <input 
                                    type="file" 
                                    id="profile_picture_input" 
                                    accept="image/png,image/jpeg,image/jpg"
                                    style="display: none;"
                                />
                            """),
                            # Script para manejar archivos
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
                                                    
                                                    // Enviar el evento correctamente usando CustomEvent
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
                            # Botón para editar foto mejorado
                            rx.button(
                                rx.hstack(
                                    rx.icon(tag="pencil", font_size="sm"),
                                    rx.text("Editar Foto"),
                                    spacing="2"
                                ),
                                width="80%",
                                margin_top="6",
                                color="white",
                                background="rgb(86, 128, 255)",
                                border_radius="full",
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
                        background="rgb(237, 237, 237)",
                        border_radius="2xl",
                        width={
                            "base": "100%",
                            "md": "300px"
                        },
                        padding="6",
                        box_shadow="0px 4px 12px rgba(0, 0, 0, 0.1)",
                        margin_right={
                            "base": "0",
                            "md": "8"
                        },
                        margin_bottom={
                            "base": "6",
                            "md": "0"
                        }
                    ),
                    
                    # Tarjeta 2: Información de Perfil
                    rx.box(
                        rx.vstack(
                            # Título de la tarjeta mejorado
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
                                # Modo edición mejorado
                                rx.vstack(
                                    # Campo nombre de usuario
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
                                        margin_bottom="5",
                                        spacing="2",
                                    ),
                                    # Campo email
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
                                        margin_bottom="5",
                                        spacing="2",
                                    ),
                                    # Campo contraseña actual
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
                                        margin_bottom="5",
                                        spacing="2",
                                    ),
                                    # Campo nueva contraseña
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
                                        margin_bottom="5",
                                        spacing="2",
                                    ),
                                    # Campo confirmar contraseña
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
                                        margin_bottom="5",
                                        spacing="2",
                                    ),
                                    # Mensaje de error
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
                                    # Botones de acción mejorados
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
                                # Modo visualización mejorado
                                rx.vstack(
                                    # Mostrar nombre de usuario
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="user", color="blue.500", box_size="6"),
                                            rx.text("NOMBRE:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.box(
                                            rx.text(
                                                ProfileState.username, 
                                                font_size="md"
                                            ),
                                            padding="3",
                                            background="white",
                                            border_radius="md",
                                            width="100%",
                                            margin_top="1"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="6",
                                        spacing="2",
                                    ),
                                    # Mostrar email
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="mail", color="blue.500", box_size="6"),
                                            rx.text("EMAIL:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.box(
                                            rx.text(
                                                ProfileState.email, 
                                                font_size="md"
                                            ),
                                            padding="3",
                                            background="white",
                                            border_radius="md",
                                            width="100%",
                                            margin_top="1"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="6",
                                        spacing="2",
                                    ),
                                    # Mostrar marcador de contraseña
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon(tag="lock", color="blue.500", box_size="6"),
                                            rx.text("CONTRASEÑA:", font_weight="bold", color="gray.700"),
                                            width="100%",
                                        ),
                                        rx.box(
                                            rx.text(
                                                "**********", 
                                                font_size="md"
                                            ),
                                            padding="3",
                                            background="white",
                                            border_radius="md",
                                            width="100%",
                                            margin_top="1"
                                        ),
                                        align_items="flex-start",
                                        width="100%",
                                        margin_bottom="6",
                                        spacing="2",
                                    ),
                                    # Botones de acción mejorados
                                    rx.hstack(
                                        rx.button(
                                            rx.hstack(
                                                rx.icon(tag="pencil", font_size="sm"),
                                                rx.text("Editar Información"),
                                                spacing="2"
                                            ),
                                            color="gray.700",
                                            background="white",
                                            border="1px solid",
                                            border_color="gray.300",
                                            _hover={"background": "rgb(245, 245, 245)"},
                                            border_radius="md",
                                            on_click=ProfileState.edit_profile,
                                            width="48%",
                                            padding_y="2"
                                        ),
                                        rx.button(
                                            rx.hstack(
                                                rx.icon(tag="log_out", font_size="sm"),
                                                rx.text("Cerrar Sesión"),
                                                spacing="2"
                                            ),
                                            color="white",
                                            background="rgb(205, 37, 44)",
                                            _hover={"background": "rgb(180, 30, 40)"},
                                            border_radius="md",
                                            on_click=ProfileState.logout,
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
                            ),
                            spacing="4",
                            align_items="stretch",
                            padding="8",
                            width="100%",
                            height="100%"
                        ),
                        background="rgb(237, 237, 237)",
                        border_radius="2xl",
                        flex="1",
                        box_shadow="0px 4px 12px rgba(0, 0, 0, 0.1)",
                        min_width={
                            "base": "100%",
                            "md": "400px"
                        }
                    ),
                    flex_direction={
                        "base": "column",
                        "md": "row"
                    },
                    align_items="stretch",
                    width="100%",
                    gap="8"
                ),
                spacing="8",
                width="100%",
                align_items="flex-start",
                padding={
                    "base": "4",
                    "md": "6"
                },
                max_width="1400px", # Increased max-width
            ),
            width="100%",
            padding={
                "base": "2",
                "md": "6 6 6 260px", # Left padding accounts for sidebar
            },
            overflow_x="hidden"
        )
    )

# Exportar la función profile_page como 'profile'
profile = profile_page