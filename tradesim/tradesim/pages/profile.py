import reflex as rx
from ..state.profile_state import ProfileState
from ..utils.auth_middleware import require_auth
from ..state.auth_state import AuthState

@require_auth
def profile_page() -> rx.Component:
    return rx.box(
        rx.vstack(
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
                        padding_left="4"
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
            rx.box(
                rx.vstack(
                    rx.text("Perfil", font_size="2", font_weight="bold", margin_bottom="6"),
                    rx.hstack(
                        rx.box(
                            rx.vstack(
                                rx.heading("FOTO DE PERFIL:", size="2", margin_bottom="4"),
                                rx.box(
                                    rx.cond(
                                        ProfileState.profile_picture != "",
                                        rx.image(
                                            src=ProfileState.profile_picture,
                                            width="260px", 
                                            height="260px", 
                                            border_radius="md",
                                            object_fit="cover"
                                        ),
                                        rx.box(
                                            rx.text("Añadir Foto", color="gray.500"),
                                            width="260px", 
                                            height="260px", 
                                            border="2px dashed", 
                                            border_color="gray.300",
                                            border_radius="md",
                                            display="flex",
                                            justify_content="center",
                                            align_items="center"
                                        )
                                    ),
                                    on_click=ProfileState.open_file_picker,
                                    cursor="pointer"
                                ),
                                rx.button(
                                    "Editar Foto",
                                    on_click=ProfileState.open_file_picker,
                                    color_scheme="blue",
                                    width="100%",
                                    margin_top="4"
                                ),
                                align_items="center",
                                justify_content="center",
                                padding="6",
                                width="100%"
                            ),
                            background="white",
                            border_radius="lg",
                            border="1px solid",
                            border_color="gray.200",
                            box_shadow="sm",
                            width="350px"
                        ),
                        rx.box(
                            rx.vstack(
                                rx.heading("INFORMACIÓN DE PERFIL", size="4", margin_bottom="4"),
                                rx.cond(
                                    ProfileState.is_editing,
                                    rx.vstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="user", color="gray.500"),
                                                rx.text("NOMBRE:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.input(
                                                value=ProfileState.temp_username,
                                                on_change=ProfileState.set_temp_username,
                                                placeholder="Nombre de usuario",
                                                width="100%"
                                            ),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="mail", color="gray.500"),
                                                rx.text("EMAIL:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.input(
                                                type_="email",
                                                value=ProfileState.temp_email,
                                                on_change=ProfileState.set_temp_email,
                                                placeholder="Email",
                                                width="100%"
                                            ),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="lock", color="gray.500"),
                                                rx.text("CONTRASEÑA ACTUAL:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.input(
                                                type_="password",
                                                value=ProfileState.current_password,
                                                on_change=ProfileState.set_current_password,
                                                placeholder="Requerida para guardar cambios",
                                                width="100%"
                                            ),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="key", color="gray.500"),
                                                rx.text("NUEVA CONTRASEÑA:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.input(
                                                type_="password",
                                                value=ProfileState.temp_password,
                                                on_change=ProfileState.set_temp_password,
                                                placeholder="Dejar en blanco para no cambiar",
                                                width="100%"
                                            ),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="check", color="gray.500"),
                                                rx.text("CONFIRMAR CONTRASEÑA:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.input(
                                                type_="password",
                                                value=ProfileState.profile_confirm_password,
                                                on_change=ProfileState.set_confirm_password,
                                                placeholder="Confirmar nueva contraseña",
                                                width="100%"
                                            ),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.cond(
                                            ProfileState.edit_error != "",
                                            rx.text(
                                                ProfileState.edit_error,
                                                color="red",
                                                font_size="2",
                                                margin_top="2"
                                            )
                                        ),
                                        rx.hstack(
                                            rx.button(
                                                "Guardar Cambios",
                                                color_scheme="blue",
                                                on_click=ProfileState.save_profile_changes,
                                                width="50%"
                                            ),
                                            rx.button(
                                                "Cancelar",
                                                color_scheme="gray",
                                                on_click=ProfileState.cancel_edit,
                                                width="50%"
                                            ),
                                            width="100%",
                                            margin_top="4",
                                            spacing="4"
                                        ),
                                        spacing="2",
                                        align_items="start",
                                        width="100%"
                                    ),
                                    rx.vstack(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="user", color="gray.500"),
                                                rx.text("NOMBRE:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.text(ProfileState.username, font_size="7"),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="mail", color="gray.500"),
                                                rx.text("EMAIL:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.text(ProfileState.email, font_size="7"),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon(tag="lock", color="gray.500"),
                                                rx.text("CONTRASEÑA:", font_weight="bold"),
                                                width="100%"
                                            ),
                                            rx.text("**********", font_size="7"),
                                            align_items="flex-start",
                                            width="100%",
                                            margin_bottom="4",
                                            spacing="2"
                                        ),
                                        rx.hstack(
                                            rx.button(
                                                "Editar Información",
                                                color_scheme="blue",
                                                on_click=ProfileState.edit_profile,
                                                width="50%"
                                            ),
                                            rx.button(
                                                "Cerrar Sesión",
                                                color_scheme="red",
                                                on_click=ProfileState.logout,
                                                width="50%"
                                            ),
                                            width="100%",
                                            margin_top="4",
                                            spacing="4"
                                        ),
                                        spacing="2",
                                        align_items="start",
                                        width="100%"
                                    )
                                ),
                                spacing="4",
                                align_items="start",
                                justify_content="flex-start",
                                padding="6",
                                width="100%"
                            ),
                            background="white",
                            border_radius="lg",
                            border="1px solid",
                            border_color="gray.200",
                            box_shadow="sm",
                            flex="1"
                        ),
                        spacing="6",
                        align_items="stretch",
                        width="100%"
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
                                            window.Reflex.setState('ProfileState.handle_file_upload', e.target.result);
                                        };
                                        reader.readAsDataURL(file);
                                    }
                                })();
                            "
                        />
                        """
                    ),
                    spacing="8",
                    padding_left="250px",
                    width="100%",
                    padding="8"
                ),
                width="100%"
            ),
            width="100%"
        )
    )

profile = rx.page(
    route="/profile",
    title="TradeSim - Perfil",
    on_load=[
        AuthState.on_load,
        ProfileState.load_profile
    ]
)(profile_page)