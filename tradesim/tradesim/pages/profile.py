# profile.py
import reflex as rx
# Ajusta la ruta de importación según tu estructura de carpetas
from ..components.profile_component import profile_component, ProfileState
from ..state.auth_state import AuthState  # Mantén si aún lo necesitas para AuthState
from ..utils.auth_middleware import require_auth
from ..components.layout import layout  # Tu layout general

@rx.page(
    route="/profile",
    title="TradeSim - Perfil",
    # Asegúrate que ProfileState.load_user_data se importa correctamente
    on_load=[
        AuthState.on_load,  # Si aún es necesario
        ProfileState.load_user_data  # Carga los datos desde el estado del componente
    ]
)
@require_auth
def profile_page() -> rx.Component:
    """Define la página de perfil, utilizando el componente importado."""
    # Aquí simplemente llamas al componente que has creado e importado
    # y lo envuelves con tu layout si es necesario.
    return layout(
        profile_component()  # Esta es la clave! Utiliza el componente importado.
    )

# Esta línea es crítica - asegura que la página se exporte correctamente
profile = profile_page