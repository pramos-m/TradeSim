# # # Contenido COMPLETO para: NOMBRE_DE_TU_APP_MODULO/pages/buscador.py

# # import reflex as rx
# # from ..components.layout import layout 
# # from ..state.search_state import SearchState 

# # def buscador_page() -> rx.Component:
# #     return layout( 
# #         rx.vstack(
# #             rx.heading("Buscador de Acciones", size="7", margin_bottom="20px", margin_top="30px", align_self="flex-start", padding_x="30px"),
# #             rx.vstack( 
# #                 rx.text("Encuentra Tu", size="8", text_align="center", width="100%"),
# #                 rx.text("Mejor Opción Aqui", size="8", font_weight="bold", color_scheme="blue", text_align="center", width="100%"),
# #                 align_items="center", width="100%", spacing="1", margin_top="20px", margin_bottom="15px",
# #             ),
# #             rx.text("Explora una amplia gama de acciones globales. Encuentra datos en tiempo real y toma decisiones de inversión informadas.",
# #                 size="4", color_scheme="gray", text_align="center", max_width="650px", margin_x="auto", margin_bottom="25px", padding_x="15px"),
# #             rx.box( 
# #                 rx.hstack(
# #                     rx.icon(tag="search", color_scheme="blue", size=24), 
# #                     rx.divider(orientation="vertical", size="2", margin_x="10px"),
# #                     rx.input(
# #                         placeholder="Buscar por símbolo o nombre de empresa...",
# #                         value=SearchState.search_query,
# #                         on_change=SearchState.set_search_query,
# #                         # ***** LÍNEA CORREGIDA Y SIMPLIFICADA *****
# #                         on_key_down=SearchState.handle_input_key_down, # Enlace directo al método
# #                         flex_grow="1", variant="surface", size="3", 
# #                     ),
# #                     rx.button("Buscar", on_click=SearchState.search_stock, is_loading=SearchState.is_searching, size="3", color_scheme="blue"),
# #                     spacing="3", align_items="center", width="100%",
# #                 ),
# #                 max_width="700px", width="90%", background_color="var(--gray-a2)", 
# #                 border_radius="var(--radius-3)", box_shadow="var(--shadow-3)",
# #                 padding="16px", margin_x="auto", margin_bottom="20px",
# #             ),
# #             rx.cond(
# #                 SearchState.search_error, # <--- CAMBIO AQUÍ
# #                 rx.callout.root(
# #                     rx.callout.icon(rx.icon("triangle_alert")),
# #                     # Asegúrate que el texto del error se muestra correctamente
# #                     rx.callout.text(SearchState.search_error), # <--- CAMBIO AQUÍ
# #                     color_scheme="red", variant="soft", margin_top="20px",
# #                     max_width="700px", width="90%", margin_x="auto",
# #                 )
# #             ),
# #             rx.cond(
# #                 (SearchState.search_result.get("Name") & SearchState.search_result.get("Logo")),
# #                 rx.box(
# #                     rx.hstack(
# #                         rx.vstack(
# #                             rx.text(SearchState.search_result.get("Current Price", "N/A"), weight="bold", size="6", color_scheme="green"),
# #                             rx.text(SearchState.search_result.get("Name", "Nombre no disponible"), size="4", margin_top="4px", font_weight="medium"),
# #                             rx.text(f"Símbolo: {SearchState.search_result.get('Symbol', 'N/A')}", size="2", color_scheme="gray", margin_top="2px"),
# #                             rx.button("Comprar", color_scheme="blue", variant="solid", size="2", margin_top="16px"),
# #                             align_items="start", spacing="2", flex_grow="1", 
# #                         ),
# #                         rx.vstack(
# #                             rx.image(
# #                                 src=SearchState.search_result.get("Logo", "/imagen_no_encontrada_placeholder.png"), 
# #                                 alt=f"Logo de {SearchState.search_result.get('Name', 'empresa')}",
# #                                 width="100px", height="auto", min_height="65px", 
# #                                 object_fit="contain", border="1px solid var(--gray-a6)", 
# #                                 border_radius="var(--radius-2)",
# #                             ),
# #                             rx.button("Ver Detalles", variant="ghost", color_scheme="gray", size="2", margin_top="10px"),
# #                             align_items="center", spacing="3",
# #                         ),
# #                         spacing="6", align_items="center", width="100%",
# #                     ),
# #                     max_width="500px", width="90%", padding="24px", border_radius="var(--radius-4)",
# #                     box_shadow="var(--shadow-4)", background_color="var(--gray-a1)", 
# #                     margin_top="20px", margin_x="auto", 
# #                 )
# #             ),
# #             align_items="center", width="100%", min_height="80vh", padding_x="15px", 
# #             padding_bottom="50px", spacing="5", 
# #         )
# #     )

# # buscador = rx.page(route="/buscador", title="TradeSim - Buscador")(buscador_page)

# # NOMBRE_DE_TU_APP_MODULO/pages/buscador.py

# import reflex as rx
# from ..components.layout import layout # Asegúrate que la ruta a tu layout es correcta
# from ..state.search_state import SearchState # Asegúrate que la ruta a tu SearchState es correcta

# def buscador_page_content() -> rx.Component:
#     """Contenido de la página del buscador de acciones."""
#     return rx.vstack(
#         rx.heading(
#             "Buscador de Acciones",
#             size="7",
#             margin_bottom="20px",
#             margin_top="30px",
#             align_self="flex-start",
#             padding_x="30px" # Añadido para consistencia
#         ),
#         rx.vstack(
#             rx.text("Encuentra Tu", size="8", text_align="center", width="100%"),
#             rx.text(
#                 "Mejor Opción Aquí",
#                 size="8",
#                 font_weight="bold",
#                 color_scheme="blue", # Radix color scheme
#                 text_align="center",
#                 width="100%"
#             ),
#             align_items="center",
#             width="100%",
#             spacing="1",
#             margin_top="20px",
#             margin_bottom="15px",
#         ),
#         rx.text(
#             "Explora una amplia gama de acciones. Encuentra datos y toma decisiones de inversión informadas.",
#             size="4", # Radix size
#             color_scheme="gray", # Radix color scheme
#             text_align="center",
#             max_width="650px",
#             margin_x="auto",
#             margin_bottom="25px",
#             padding_x="15px"
#         ),
#         rx.box(
#             rx.hstack(
#                 rx.icon(tag="search", color_scheme="blue", size=24), # Radix icon and size
#                 rx.divider(orientation="vertical", size="2", margin_x="10px"), # Radix divider
#                 rx.input(
#                     placeholder="Buscar por símbolo o nombre de empresa...",
#                     value=SearchState.search_query,
#                     on_change=SearchState.set_search_query,
#                     on_key_down=SearchState.handle_input_key_down, # Correcto
#                     flex_grow="1",
#                     variant="surface", # Radix variant
#                     size="3", # Radix size
#                 ),
#                 rx.button(
#                     "Buscar",
#                     on_click=SearchState.search_stock,
#                     is_loading=SearchState.is_searching,
#                     size="3", # Radix size
#                     color_scheme="blue" # Radix color scheme
#                 ),
#                 spacing="3", # Radix spacing
#                 align_items="center",
#                 width="100%",
#             ),
#             max_width="700px",
#             width="90%",
#             bg="var(--gray-a2)", # Usando variable de color Radix Alpha
#             border_radius="var(--radius-3)", # Usando variable de radio Radix
#             box_shadow="var(--shadow-3)", # Usando variable de sombra Radix
#             padding="16px",
#             margin_x="auto",
#             margin_bottom="20px",
#         ),

#         # Mensaje de error
#         rx.cond(
#             SearchState.search_error != "", # Mostrar si search_error no está vacío
#             rx.callout.root(
#                 rx.callout.icon(rx.icon(tag="alert_triangle")), # Icono más apropiado
#                 rx.callout.text(SearchState.search_error),
#                 color_scheme="red",
#                 variant="soft", # Radix variant
#                 margin_top="20px",
#                 max_width="700px",
#                 width="90%",
#                 margin_x="auto",
#             )
#         ),

#         # Resultados de la búsqueda
#         rx.cond(
#             SearchState.search_result.get("Symbol"), # Condición más simple: si hay un símbolo, hay resultado
#             rx.box(
#                 rx.hstack(
#                     rx.vstack(
#                         # Usar la clave "Price" que provee tu SearchState
#                         rx.text(
#                             f"${SearchState.search_result.get('Price', 0.0):,.2f}",
#                             weight="bold",
#                             size="6", # Radix size
#                             color_scheme="green" # O el color que corresponda al cambio si lo tuvieras
#                         ),
#                         rx.text(
#                             SearchState.search_result.get("Name", "Nombre no disponible"),
#                             size="4", # Radix size
#                             margin_top="4px",
#                             font_weight="medium"
#                         ),
#                         rx.text(
#                             f"Símbolo: {SearchState.search_result.get('Symbol', 'N/A')}",
#                             size="2", # Radix size
#                             color_scheme="gray",
#                             margin_top="2px"
#                         ),
#                         rx.button(
#                             "Ver Detalles",
#                             on_click=lambda: SearchState.go_to_stock_detail(SearchState.search_result.get("Symbol")),
#                             color_scheme="blue",
#                             variant="solid", # Radix variant
#                             size="2", # Radix size
#                             margin_top="16px"
#                         ),
#                         align_items="start",
#                         spacing="2", # Radix spacing
#                         flex_grow="1",
#                     ),
#                     # Si tienes un logo_url en tu Stock model y SearchState lo añade a search_result:
#                     rx.vstack(
#                         rx.image(
#                             src=SearchState.search_result.get("Logo", "/default_logo.png"), # Placeholder si no hay logo
#                             alt=f"Logo de {SearchState.search_result.get('Name', 'empresa')}",
#                             width="100px",
#                             height="auto", # Mantener relación de aspecto
#                             min_height="65px", # Para evitar que sea muy pequeño
#                             object_fit="contain",
#                             border="1px solid var(--gray-a6)",
#                             border_radius="var(--radius-2)", # Radix radius
#                         ),
#                         # El botón "Ver Detalles" ya está en el vstack de la izquierda,
#                         # no es necesario duplicarlo aquí a menos que quieras otro diseño.
#                         align_items="center",
#                         spacing="3", # Radix spacing
#                     ),
#                     spacing="6", # Radix spacing
#                     align_items="center",
#                     width="100%",
#                 ),
#                 max_width="500px",
#                 width="90%",
#                 padding="24px",
#                 border_radius="var(--radius-4)", # Radix radius
#                 box_shadow="var(--shadow-4)", # Radix shadow
#                 bg="var(--gray-a1)", # Radix Alpha color
#                 margin_top="20px",
#                 margin_x="auto",
#             )
#         ),
#         align_items="center",
#         width="100%",
#         min_height="calc(100vh - 120px)", # Ajustar para que ocupe la pantalla menos header/footer si los tienes
#         padding_x="15px",
#         padding_bottom="50px",
#         spacing="5", # Radix spacing
#     )

# def buscador_page() -> rx.Component:
#     """Página del buscador de acciones envuelta en el layout."""
#     return layout(
#         buscador_page_content()
#     )

# # Esto es opcional si ya tienes la página definida en tu __init__.py o app.py principal
# # buscador = rx.page(route="/buscador", title="TradeSim - Buscador")(buscador_page)

# tradesim/tradesim/pages/buscador.py
import reflex as rx
from ..components.layout import layout # Asegúrate que la ruta a tu layout es correcta
from ..state.search_state import SearchState # Asegúrate que la ruta a tu SearchState es correcta

def buscador_page_content() -> rx.Component:
    """Contenido de la página del buscador de acciones."""
    return rx.vstack(
        rx.heading(
            "Buscador de Acciones",
            size="7",
            margin_bottom="20px",
            margin_top="30px",
            align_self="flex-start",
            padding_x="30px"
        ),
        rx.vstack(
            rx.text("Encuentra Tu", size="8", text_align="center", width="100%"),
            rx.text(
                "Mejor Opción Aquí",
                size="8",
                font_weight="bold",
                color_scheme="blue",
                text_align="center",
                width="100%"
            ),
            align_items="center", width="100%", spacing="1", margin_top="20px", margin_bottom="15px",
        ),
        rx.text(
            "Explora una amplia gama de acciones globales. Encuentra datos en tiempo real y toma decisiones de inversión informadas.",
            size="4", color_scheme="gray", text_align="center", max_width="650px", 
            margin_x="auto", margin_bottom="25px", padding_x="15px"
        ),
        rx.box( 
            rx.hstack(
                rx.icon(tag="search", color_scheme="blue", size=24), 
                rx.divider(orientation="vertical", size="2", margin_x="10px"),
                rx.input(
                    placeholder="Buscar por símbolo o nombre de empresa...",
                    value=SearchState.search_query,
                    on_change=SearchState.set_search_query,
                    on_key_down=SearchState.handle_input_key_down,
                    flex_grow="1", variant="surface", size="3", 
                ),
                rx.button(
                    "Buscar", 
                    on_click=SearchState.search_stock, 
                    is_loading=SearchState.is_searching,
                    size="3", color_scheme="blue"
                ),
                spacing="3", align_items="center", width="100%",
            ),
            max_width="700px", width="90%", background_color="var(--gray-a2)", 
            border_radius="var(--radius-3)", box_shadow="var(--shadow-3)",
            padding="16px", margin_x="auto", margin_bottom="20px",
        ),

        # Mensaje de error de búsqueda
        rx.cond(
            SearchState.search_error != "", 
            rx.callout.root(
                rx.callout.icon(rx.icon(tag="alert_triangle")), 
                rx.callout.text(SearchState.search_error),
                color_scheme="red", variant="soft", margin_top="20px",
                max_width="700px", width="90%", margin_x="auto", 
            )
        ),

        # Resultados de la búsqueda
        rx.cond(
            SearchState.search_result.get("Symbol") & (SearchState.search_error == ""), 
            rx.box(
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            SearchState.search_result.get("PriceString", "N/A"), 
                            weight="bold", size="6", color_scheme="green"
                        ),
                        rx.text(SearchState.search_result.get("Name", "Nombre no disponible"), size="4", margin_top="4px", font_weight="medium"),
                        rx.text(f"Símbolo: {SearchState.search_result.get('Symbol', 'N/A')}", size="2", color_scheme="gray", margin_top="2px"),
                        rx.button(
                            "Ver Detalles", 
                            on_click=lambda: SearchState.go_to_stock_detail(SearchState.search_result.get("Symbol")),
                            color_scheme="blue", variant="solid", size="2", margin_top="16px",
                            is_disabled=(SearchState.search_result.get("Symbol", "N/A") == "N/A")
                        ),
                        align_items="start", spacing="2", flex_grow="1", 
                    ),
                    rx.vstack(
                        rx.image(
                            src=SearchState.search_result.get("Logo", "/default_logo.png"), 
                            alt=f"Logo de {SearchState.search_result.get('Name', 'empresa')}",
                            width="100px", height="auto", min_height="65px", 
                            object_fit="contain", border="1px solid var(--gray-a6)", 
                            border_radius="var(--radius-2)",
                        ),
                        align_items="center", spacing="3",
                    ),
                    spacing="6", align_items="center", width="100%",
                ),
                max_width="500px", width="90%", padding="24px", border_radius="var(--radius-4)",
                box_shadow="var(--shadow-4)", bg="var(--gray-a1)", 
                margin_top="20px", margin_x="auto", 
            )
        ),
        align_items="center", width="100%", min_height="calc(100vh - 160px)", 
        padding_x="15px", 
        padding_bottom="50px", spacing="5", 
    )

def buscador_page() -> rx.Component:
    """Página del buscador de acciones envuelta en el layout."""
    return layout(
        buscador_page_content()
    )

# --- ESTA LÍNEA ES CRUCIAL Y HA SIDO DESCOMENTADA ---
buscador = rx.page(
    route="/buscador", 
    title="TradeSim - Buscador"
)(buscador_page)
