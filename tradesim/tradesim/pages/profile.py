import reflex as rx
from ..state.profile_state import ProfileState
from ..utils.auth_middleware import require_auth
from ..state.auth_state import AuthState

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
    return rx.box(
        rx.vstack(
            # Sidebar (ya existe en otra rama, no modificamos)
            rx.box(
                rx.vstack(
                    rx.image(src="/logo.svg", height="50px"),
                    rx.vstack(
                        rx.link(
                            rx.hstack(
                                rx.icon(tag="home", color="gray.500"),
                                rx.text("Inicio", color="gray.700")
                            ),
                            href="/dashboard"
                        ),
                        rx.hstack(
                            rx.icon(tag="trending_up", color="blue.500"),
                            rx.text("Estadísticas", color="gray.700")
                        ),
                        rx.hstack(
                            rx.icon(tag="file", color="gray.500"),
                            rx.text("Documentos", color="gray.700")
                        ),
                        rx.hstack(
                            rx.icon(tag="search", color="gray.500"),
                            rx.text("Buscar", color="gray.700")
                        ),
                        spacing="4",
                        align_items="start",
                        width="100%",
                        padding_left="4",
                        margin_top="8"
                    ),
                    width="250px",
                    height="100vh",
                    border_right="1px solid",
                    border_color="gray.200",
                    position="fixed",
                    left="0",
                    top="0",
                    background="white",
                    z_index="10"
                )
            ),
            # Contenido principal
            rx.box(
                rx.vstack(
                    # Título principal con mejor espaciado
                    rx.text(
                        "Perfil", 
                        font_size="2xl", 
                        font_weight="bold", 
                        margin_bottom="8", 
                        align_self="start",
                        padding_top="2"
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
                                    padding_top="2"
                                ),
                                # Contenido condicional mejorado
                                rx.cond(
                                    ProfileState.profile_picture != "",
                                    rx.image(
                                        src=ProfileState.profile_picture,
                                        width="200px", 
                                        height="200px", 
                                        border_radius="full",  # Imagen circular
                                        object_fit="cover",
                                        border="3px solid",
                                        border_color="blue.400"
                                    ),
                                    rx.box(
                                        rx.vstack(
                                            rx.icon(
                                                tag="add_photo_alternate",
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
                                        border_radius="full",  # Placeholder circular
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
                                        rx.icon(tag="edit", font_size="sm"),
                                        rx.text("Editar Foto"),
                                        spacing="2"
                                    ),
                                    width="80%",
                                    margin_top="6",
                                    color="white",
                                    background="rgb(86, 128, 255)",
                                    border_radius="full",  # Botón redondeado
                                    _hover={"background": "rgb(70, 110, 230)"},
                                    padding_y="2",
                                    on_click=rx.call_script(
                                        'document.getElementById("profile_picture_input").click()'
                                    )
                                ),
                                align_items="center",
                                justify_content="center",
                                padding="8",
                                width="100%",
                                height="100%"
                            ),
                            background="rgb(237, 237, 237)",
                            border_radius="2xl",  # Bordes más redondeados
                            width="300px",
                            padding="6",
                            box_shadow="0px 4px 12px rgba(0, 0, 0, 0.1)",
                            margin_right={
                                "base": "0",  # En móvil, sin margen
                                "md": "8"     # En desktop, margen derecho
                            },
                            margin_bottom={
                                "base": "6",  # En móvil, margen inferior
                                "md": "0"     # En desktop, sin margen inferior
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
                                    padding_top="2"
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
                                                    rx.icon(tag="save", font_size="sm"),
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
                                                    rx.icon(tag="close", font_size="sm"),
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
                                            padding_x="10%",
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
                                                    rx.icon(tag="edit", font_size="sm"),
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
                                                    rx.icon(tag="logout", font_size="sm"),
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
                                            padding_x="10%",
                                        ),
                                        spacing="2",
                                        align_items="start",
                                        width="100%",
                                        height="100%"
                                    ),
                                ),
                                spacing="4",
                                align_items="start",
                                justify_content="flex-start",
                                padding="8",
                                width="100%",
                                height="100%"
                            ),
                            background="rgb(237, 237, 237)",
                            border_radius="2xl",  # Bordes más redondeados
                            flex="1",
                            box_shadow="0px 4px 12px rgba(0, 0, 0, 0.1)",
                            min_width={{
                                "base": "100%",  # En móvil, ancho completo
                                "md": "400px"    # En desktop, ancho mínimo
                            }}
                        ),
                        flex_direction={{
                            "base": "column",    # En móvil, apilados verticalmente
                            "md": "row"          # En desktop, en fila
                        }},
                        align_items="stretch",
                        width="100%",
                        gap="8"  # Espacio uniforme entre elementos
                    ),
                    spacing="8",
                    padding_left="250px",  # Espacio para el sidebar
                    width="100%",
                    padding="10",  # Padding general aumentado
                    max_width="1200px",  # Ancho máximo para pantallas grandes
                    margin="0 auto"     # Centrar en pantallas muy grandes
                ),
                width="100%"
            ),
            width="100%"
        )
    )

# Exportar la función profile_page como 'profile'
profile = profile_page