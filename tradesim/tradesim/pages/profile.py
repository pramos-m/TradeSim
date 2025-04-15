# profile.py
import reflex as rx
# Ajusta la ruta d'importació segons la teva estructura de carpetes
# Si 'profile.py' està a 'your_app/pages' i 'profile_component.py' a 'your_app/components',
# la importació seria així:
from ..components.profile_component import profile_component, ProfileState
from ..state.auth_state import AuthState # Mantén si encara el necessites per AuthState
from ..utils.auth_middleware import require_auth
from ..components.layout import layout # El teu layout general

@rx.page(
    route="/profile",
    title="TradeSim - Perfil",
    # Assegura't que ProfileState.load_user_data s'importa correctament
    on_load=[
        AuthState.on_load, # Si encara és necessari
        ProfileState.load_user_data # Carrega les dades des de l'estat del component
    ]
)
@require_auth
def profile_page() -> rx.Component:
    """Defineix la pàgina de perfil, utilitzant el component importat."""
    # Aquí simplement crides al component que has creat i importat
    # i l'embolcalles amb el teu layout si cal.
    return layout(
        profile_component() # Aquesta és la clau! Utilitza el component importat.
    )

# <<<=== AFEGEIX AQUESTA LÍNIA DE NOU ===>>>
profile = profile_page
# <<<====================================>>>