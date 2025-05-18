# profile.py
import reflex as rx
# Ajusta la ruta de importación según tu estructura de carpetas
from ..components.profile_component import profile_component, ProfileState
from ..state.auth_state import AuthState
from ..utils.auth_middleware import require_auth
from ..components.layout import layout  # Tu layout general

@rx.page(
    route="/profile",
    title="TradeSim - Perfil",
    on_load=[
        AuthState.on_load,
        ProfileState.load_user_data  # Carga los datos desde el estado del componente
    ]
)
@require_auth
def profile_page() -> rx.Component:
    """Define la página de perfil, utilizando el componente importado."""
    return layout(  # Asumiendo que tu layout maneja la sidebar y el padding principal
        rx.box(
            profile_component(), # Esta es la clave! Utiliza el componente importado y estilizado.
            width="100%",
            # El padding de la página, especialmente el izquierdo para la sidebar,
            # idealmente debería ser manejado por el componente `layout`.
            # Si `layout` no lo hace, puedes añadirlo aquí, por ejemplo:
            # padding_left={"base": "4", "md": "260px"}, # Si la sidebar tiene 260px
            # padding_right={"base": "4", "md": "6"},
            # padding_y={"base": "4", "md": "6"},
        )
    )

profile = profile_page