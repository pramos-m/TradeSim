import reflex as rx

config = rx.Config(
    app_name="tradesim",
    db_url="sqlite:///data/database.db",
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
    telemetry_enabled=False,
    # Removemos module_name ya que usaremos la estructura estándar
)