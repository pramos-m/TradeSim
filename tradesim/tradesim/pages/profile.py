# pages/profile.py
import reflex as rx
from ..state.auth_state import AuthState
from ..state.profile_state import ProfileState
from ..utils.auth_middleware import require_auth

@require_auth
def profile_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Sidebar
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
                            rx.icon(tag="trending-up", color="blue.500"),
                            rx.text("Estadísticas", color="gray.700")
                        ),
                        rx.hstack(
                            rx.icon(tag="file-text", color="gray.500"),
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
                    top="0"
                )
            ),
            
            # Profile Content
            rx.box(
                rx.vstack(
                    rx.text("Perfil", font_size="2xl", font_weight="bold", margin_bottom="6"),
                    rx.hstack(
                        # Profile Picture
                        rx.box(
                            rx.cond(
                                ProfileState.profile_picture,
                                rx.image(
                                    src=ProfileState.profile_picture,
                                    width="200px", 
                                    height="200px", 
                                    border_radius="full",
                                    object_fit="cover"
                                ),
                                rx.box(
                                    rx.text("Añadir Foto", color="gray.500"),
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
                            on_click=ProfileState.open_file_picker,
                            cursor="pointer"
                        ),
                        
                        # Input invisible para subir archivos
                        rx.input(
                            type_="file", 
                            id="profile_picture_input", 
                            accept=".png,.jpg,.jpeg",
                            display="none",
                            on_change=ProfileState.handle_file_upload
                        ),
                        
                        # Profile Info - Modo edición condicional
                        rx.cond(
                            ProfileState.editing,
                            # Modo edición - Campos de formulario
                            rx.vstack(
                                rx.vstack(
                                    rx.text("NOMBRE:"),
                                    rx.input(
                                        value=ProfileState.temp_username,
                                        on_change=ProfileState.set_temp_username,
                                        placeholder="Nombre de usuario"
                                    ),
                                    align_items="flex-start",
                                    width="100%",
                                    margin_bottom="2"
                                ),
                                rx.vstack(
                                    rx.text("EMAIL:"),
                                    rx.input(
                                        type_="email",
                                        value=ProfileState.temp_email,
                                        on_change=ProfileState.set_temp_email,
                                        placeholder="Email"
                                    ),
                                    align_items="flex-start",
                                    width="100%",
                                    margin_bottom="2"
                                ),
                                rx.vstack(
                                    rx.text("CONTRASEÑA ACTUAL:"),
                                    rx.input(
                                        type_="password",
                                        value=ProfileState.current_password,
                                        on_change=ProfileState.set_current_password,
                                        placeholder="Requerida para guardar cambios"
                                    ),
                                    align_items="flex-start",
                                    width="100%",
                                    margin_bottom="2"
                                ),
                                rx.vstack(
                                    rx.text("NUEVA CONTRASEÑA:"),
                                    rx.input(
                                        type_="password",
                                        value=ProfileState.temp_password,
                                        on_change=ProfileState.set_temp_password,
                                        placeholder="Dejar en blanco para no cambiar"
                                    ),
                                    align_items="flex-start",
                                    width="100%",
                                    margin_bottom="2"
                                ),
                                rx.vstack(
                                    rx.text("CONFIRMAR CONTRASEÑA:"),
                                    rx.input(
                                        type_="password",
                                        value=ProfileState.confirm_password,
                                        on_change=ProfileState.set_confirm_password,
                                        placeholder="Confirmar nueva contraseña"
                                    ),
                                    align_items="flex-start",
                                    width="100%",
                                    margin_bottom="2"
                                ),
                                # Mostrar mensaje de error si existe
                                rx.cond(
                                    ProfileState.edit_error,
                                    rx.text(
                                        ProfileState.edit_error,
                                        color="red",
                                        font_size="sm",
                                        margin_top="2"
                                    )
                                ),
                                spacing="3",
                                align_items="start",
                                width="100%"
                            ),
                            # Modo visualización - Texto simple
                            rx.vstack(
                                rx.hstack(
                                    rx.text("NOMBRE:", font_weight="bold"),
                                    rx.text(AuthState.username)  # Usar AuthState.username directamente
                                ),
                                rx.hstack(
                                    rx.text("EMAIL:", font_weight="bold"),
                                    rx.text(AuthState.email)  # Usar AuthState.email directamente
                                ),
                                rx.hstack(
                                    rx.text("CONTRASEÑA:", font_weight="bold"),
                                    rx.text("**********")
                                ),
                                spacing="4",
                                align_items="start"
                            ),
                        ),
                        spacing="8",
                        align_items="flex-start"
                    ),
                    
                    # Botón de acción: Editar/Guardar o Cancelar
                    rx.hstack(
                        # Botón principal: Editar o Guardar dependiendo del estado
                        rx.button(
                            rx.cond(
                                ProfileState.editing,
                                "Guardar Cambios",
                                "Editar Información"
                            ),
                            color_scheme="blue",
                            variant=rx.cond(ProfileState.editing, "solid", "outline"),
                            on_click=ProfileState.edit_profile
                        ),
                        # Botón de cancelar (solo visible en modo edición)
                        rx.cond(
                            ProfileState.editing,
                            rx.button(
                                "Cancelar", 
                                color_scheme="gray",
                                on_click=ProfileState.cancel_edit
                            )
                        ),
                        # Botón de cerrar sesión (solo visible fuera del modo edición)
                        rx.cond(
                            ~ProfileState.editing,
                            rx.button(
                                "Cerrar Sesión", 
                                color_scheme="red",
                                on_click=AuthState.logout
                            )
                        ),
                        spacing="4"
                    ),
                    
                    spacing="8",
                    padding_left="250px",
                    width="100%"
                ),
                width="100%"
            ),
            
            width="100%"
        )
    )

# Define la página con eventos de carga
profile = rx.page(
    route="/profile",
    title="TradeSim - Perfil",
    on_load=[AuthState.on_load, ProfileState.load_profile]
)(profile_page)