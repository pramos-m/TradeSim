import reflex as rx

config = rx.Config(
    app_name="tradesim",
    db_url="sqlite:///data/database.db",
    env=rx.Env.DEV,
    frontend_port=3000,
    backend_port=8000,
    telemetry_enabled=False,
    # Forzar React 18 para compatibilidad
    frontend_packages=[
        "react@18.2.0",
        "react-dom@18.2.0"
    ]
)