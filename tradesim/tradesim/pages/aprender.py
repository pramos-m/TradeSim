import reflex as rx
from ..components.layout import layout
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- ESTADO Y LÓGICA PARA LA CALCULADORA DE INTERÉS COMPUESTO ---
class CalculadoraInteresState(rx.State):
    inversion_inicial_str: str = "1000"
    aportacion_mensual_str: str = "300"
    tasa_interes_anual_str: str = "7"
    periodo_anyos_str: str = "25"
    
    resultado: str = ""
    mostrar_resultado: bool = False

    @rx.var
    def inversion_inicial(self) -> float:
        try:
            return float(self.inversion_inicial_str)
        except ValueError:
            return 0.0

    @rx.var
    def aportacion_mensual(self) -> float:
        try:
            return float(self.aportacion_mensual_str)
        except ValueError:
            return 0.0

    @rx.var
    def tasa_interes_anual(self) -> float:
        try:
            return float(self.tasa_interes_anual_str)
        except ValueError:
            return 0.0

    @rx.var
    def periodo_anyos(self) -> int:
        try:
            val = int(self.periodo_anyos_str)
            return val if val > 0 else 0
        except ValueError:
            return 0

    def calcular_interes_compuesto(self):
        self.mostrar_resultado = False
        
        current_inversion_inicial = self.inversion_inicial
        current_aportacion_mensual = self.aportacion_mensual
        current_tasa_interes_anual = self.tasa_interes_anual
        current_periodo_anyos = self.periodo_anyos

        if current_periodo_anyos <= 0:
            self.resultado = "El período en años debe ser un número positivo."
            self.mostrar_resultado = True
            return
        if current_tasa_interes_anual < 0:
            self.resultado = "La tasa de interés anual no puede ser negativa."
            self.mostrar_resultado = True
            return
        if current_inversion_inicial < 0 or current_aportacion_mensual < 0:
            self.resultado = "La inversión inicial y la aportación mensual no pueden ser negativas."
            self.mostrar_resultado = True
            return

        tasa_decimal_anual = current_tasa_interes_anual / 100.0
        capital_final_total: float
        
        if tasa_decimal_anual == 0:
            capital_final_total = current_inversion_inicial + (current_aportacion_mensual * current_periodo_anyos * 12)
        else:
            tasa_mensual = tasa_decimal_anual / 12
            num_meses = current_periodo_anyos * 12
            capital_final_total = 0.0

            if current_inversion_inicial > 0:
                capital_final_total += current_inversion_inicial * ((1 + tasa_mensual) ** num_meses)
            
            if current_aportacion_mensual > 0 and num_meses > 0:
                # Fórmula para el valor futuro de una serie de aportaciones (anualidad)
                capital_final_total += current_aportacion_mensual * ((((1 + tasa_mensual) ** num_meses) - 1) / tasa_mensual) * (1 + tasa_mensual) # Si las aportaciones son al inicio del periodo
                # Si las aportaciones son al final del periodo (más común):
                # capital_final_total += current_aportacion_mensual * ((((1 + tasa_mensual) ** num_meses) - 1) / tasa_mensual)


        total_aportado = current_inversion_inicial + (current_aportacion_mensual * current_periodo_anyos * 12)
        intereses_ganados = capital_final_total - total_aportado

        formato_numero = "{:,.2f} €"
        self.resultado = (
            f"Capital final estimado: {formato_numero.format(capital_final_total)}\n\n"
            f"Total aportado (inicial + aportaciones): {formato_numero.format(total_aportado)}\n\n"
            f"Intereses ganados: {formato_numero.format(intereses_ganados)}"
        )
        self.mostrar_resultado = True

# --- COMPONENTE DE LA CALCULADORA ---
def calculadora_interes_compuesto_component() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Calculadora de Interés Compuesto", size="7", margin_bottom="16px", text_align="center"),
            rx.text(
                "Descubre el poder del interés compuesto. Introduce tus datos y visualiza el crecimiento potencial de tu inversión a lo largo del tiempo.",
                margin_bottom="24px", text_align="center", size="3"
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Inversión Inicial (€):", size="2", margin_bottom="2px"),
                    rx.input(
                        value=CalculadoraInteresState.inversion_inicial_str,
                        on_change=CalculadoraInteresState.set_inversion_inicial_str,
                        placeholder="Ej: 1000", type="number", width="100%"
                    ),
                    align_items="start", width="100%"
                ),
                rx.vstack(
                    rx.text("Aportación Mensual (€):", size="2", margin_bottom="2px"),
                    rx.input(
                        value=CalculadoraInteresState.aportacion_mensual_str,
                        on_change=CalculadoraInteresState.set_aportacion_mensual_str,
                        placeholder="Ej: 100", type="number", width="100%"
                    ),
                    align_items="start", width="100%"
                ),
                rx.vstack(
                    rx.text("Tasa Interés Anual (%):", size="2", margin_bottom="2px"),
                    rx.input(
                        value=CalculadoraInteresState.tasa_interes_anual_str,
                        on_change=CalculadoraInteresState.set_tasa_interes_anual_str,
                        placeholder="Ej: 7", type="number", width="100%"
                    ),
                    align_items="start", width="100%"
                ),
                rx.vstack(
                    rx.text("Período (Años):", size="2", margin_bottom="2px"),
                    rx.input(
                        value=CalculadoraInteresState.periodo_anyos_str,
                        on_change=CalculadoraInteresState.set_periodo_anyos_str,
                        placeholder="Ej: 10", type="number", width="100%"
                    ),
                    align_items="start", width="100%"
                ),
                columns="2", spacing="4", width="100%", max_width="600px", margin_x="auto"
            ),
            rx.button(
                "Calcular",
                on_click=CalculadoraInteresState.calcular_interes_compuesto,
                margin_top="24px", size="3", # Radix Button size
                bg="green.500", color="white",
                _hover={"bg": "green.600"}
            ),
            rx.cond(
                CalculadoraInteresState.mostrar_resultado,
                rx.box(
                    rx.markdown(CalculadoraInteresState.resultado),
                    margin_top="24px", width="100%", max_width="500px", margin_x="auto",
                    padding="16px",
                    border="1px solid #4CAF50",
                    background_color="#E8F5E9",
                    border_radius="6px",
                )
            ),
            rx.box(
                rx.heading("Entendiendo el Interés Compuesto", size="6", margin_top="32px", margin_bottom="16px", text_align="center"),
                rx.text("El interés compuesto es el proceso donde los intereses generados por una inversión se reinvierten, generando a su vez nuevos intereses. Con el tiempo, esto puede llevar a un crecimiento exponencial de tu capital.", margin_bottom="12px", size="2"),
                rx.text("Esta calculadora te ayuda a estimar el valor futuro de tus ahorros considerando una inversión inicial y aportaciones mensuales regulares.", margin_bottom="12px", size="2"),
                rx.text("La fórmula básica para el interés compuesto (sin aportaciones periódicas) es:", margin_top="16px", font_weight="bold", size="2"),
                rx.box(
                    rx.code_block(
                        "Capital Final = Capital Inicial * (1 + Tasa de Interés)^Número de Períodos"
                    ),
                    margin_y="12px",
                    padding="10px",
                    border_radius="6px",
                    border="1px solid #dddddd",
                    background_color="#f9f9f9",
                    width="100%"
                ),
                rx.text("Cuando se incluyen aportaciones periódicas, el cálculo se vuelve más complejo ya que considera el crecimiento de cada aportación a lo largo del tiempo, además del capital inicial.", font_style="italic", size="2"),
                padding_x="16px", width="100%"
            ),
            spacing="5", align_items="center", width="100%",
        ),
        background_color="#f0f4f8",
        border_radius="12px",
        padding_y="32px", padding_x="24px",
        margin_top="32px", margin_bottom="48px", width="100%"
    )


# --- DEFINICIÓN DE LA PÁGINA ---
def aprender_page() -> rx.Component:
    """Define la página de aprender, utilizando el componente layout importado."""
    return layout(
        rx.box(
            aprender_content(),
            width="100%",
        )
    )

# --- ESTADO Y LÓGICA PARA EL CONVERSOR DE MONEDAS ---
class ConversorMonedasState(rx.State):
    cantidad_str: str = "100"
    moneda_origen: str = "EUR"
    moneda_destino: str = "USD"
    resultado: str = ""
    mostrar_resultado: bool = False
    
    # Tasas de cambio fijas (en la vida real deberías usar una API)
    TASAS = {
        "EUR": {"USD": 1.08, "CNY": 7.82, "GBP": 0.86, "JPY": 162.5},
        "USD": {"EUR": 0.93, "CNY": 7.24, "GBP": 0.79, "JPY": 150.5},
        "CNY": {"EUR": 0.13, "USD": 0.14, "GBP": 0.11, "JPY": 20.78},
        "GBP": {"EUR": 1.16, "USD": 1.26, "CNY": 9.09, "JPY": 188.95},
        "JPY": {"EUR": 0.0062, "USD": 0.0066, "CNY": 0.048, "GBP": 0.0053}
    }

    @rx.var
    def cantidad(self) -> float:
        try:
            return float(self.cantidad_str)
        except ValueError:
            return 0.0

    def convertir(self):
        self.mostrar_resultado = False
        
        if self.moneda_origen == self.moneda_destino:
            self.resultado = f"{self.cantidad_str} {self.moneda_origen}"
            self.mostrar_resultado = True
            return

        try:
            cantidad = float(self.cantidad_str)
            if cantidad < 0:
                self.resultado = "La cantidad no puede ser negativa."
                self.mostrar_resultado = True
                return

            tasa = self.TASAS[self.moneda_origen][self.moneda_destino]
            resultado = cantidad * tasa
            self.resultado = f"{cantidad:,.2f} {self.moneda_origen} = {resultado:,.2f} {self.moneda_destino}"
            self.mostrar_resultado = True
        except ValueError:
            self.resultado = "Por favor, introduce una cantidad válida."
            self.mostrar_resultado = True

    def intercambiar_monedas(self):
        origen = self.moneda_origen
        self.moneda_origen = self.moneda_destino
        self.moneda_destino = origen

# --- COMPONENTE DEL CONVERSOR DE MONEDAS ---
def conversor_monedas_component() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Conversor de Monedas", size="7", margin_bottom="16px", text_align="center"),
            rx.text(
                "Convierte entre las principales monedas mundiales.",
                margin_bottom="24px", text_align="center", size="3"
            ),
            rx.grid(
                rx.vstack(
                    rx.text("Cantidad:", size="2", margin_bottom="2px"),
                    rx.input(
                        value=ConversorMonedasState.cantidad_str,
                        on_change=ConversorMonedasState.set_cantidad_str,
                        placeholder="Ej: 100",
                        type="number",
                        width="100%"
                    ),
                    align_items="start",
                    width="100%"
                ),
                rx.hstack(  # Usamos hstack para alinear los selectores y el botón
                    rx.vstack(
                        rx.text("De:", size="2", margin_bottom="2px"),
                        rx.select(
                            ["EUR", "USD", "CNY", "GBP", "JPY"],
                            value=ConversorMonedasState.moneda_origen,
                            on_change=ConversorMonedasState.set_moneda_origen,
                            width="100%"
                        ),
                        align_items="start",
                        width="100%"
                    ),
                    rx.center(  # Centramos el botón de swap verticalmente
                        rx.button(
                            rx.icon(tag="arrow_right_left", color="black"),  # Icono de intercambio
                            on_click=ConversorMonedasState.intercambiar_monedas,
                            bg="white",  # Color de fondo negro
                            _hover={"bg": "gray.800"},  # Cambio de color al pasar el ratón
                            width="auto",  # Ancho automático para ajustarse al contenido
                            height="auto",  # Alto automático para ajustarse al contenido
                            border_radius="6px",  # Bordes redondeados
                            margin_top="35px" #Bajar el boton
                        )
                    ),
                    rx.vstack(
                        rx.text("A:", size="2", margin_bottom="2px"),
                        rx.select(
                            ["EUR", "USD", "CNY", "GBP", "JPY"],
                            value=ConversorMonedasState.moneda_destino,
                            on_change=ConversorMonedasState.set_moneda_destino,
                            width="100%"
                        ),
                        align_items="start",
                        width="100%"
                    ),
                    align="center",  # Alineamos los elementos al centro verticalmente
                    spacing="4",  # Espacio entre los selectores y el botón
                ),
                columns="1",  # Una columna para la cantidad y otra para la fila de monedas
                spacing="4",
                width="100%",
                max_width="600px",
                margin_x="auto"
            ),
            rx.button(
                "Convertir",
                on_click=ConversorMonedasState.convertir,
                margin_top="24px",
                size="3",
                bg="blue.500",
                color="white",
                _hover={"bg": "blue.600"}
            ),
            rx.cond(
                ConversorMonedasState.mostrar_resultado,
                rx.box(
                    rx.text(
                        ConversorMonedasState.resultado,
                        size="3",
                        font_weight="bold"
                    ),
                    margin_top="24px",
                    padding="16px",
                    border="1px solid #3182CE",
                    background_color="#EBF8FF",
                    border_radius="6px",
                    text_align="center"
                )
            ),
            rx.box(
                rx.text(
                    "Nota: Las tasas de cambio son aproximadas y pueden variar. Para transacciones reales, consulta las tasas actuales.",
                    size="2",
                    color="gray.600",
                    font_style="italic"
                ),
                margin_top="16px"
            ),
            spacing="5",
            align_items="center",
            width="100%",
        ),
        background_color="#f0f4f8",
        border_radius="12px",
        padding_y="32px",
        padding_x="24px",
        margin_top="32px",
        margin_bottom="48px",
        width="100%"
    )

def aprender_content() -> rx.Component:
    """Contenido principal de la página 'Aprender'."""
    section_style = {
        "background_color": "#f8f9fa",
        "border_radius": "12px",
        "padding": "24px",
        "margin_bottom": "32px",
        "width": "100%"
    }
    list_item_spacing = "4px"
    text_size = "3"
    bold_text_margin_top = "12px"
    bold_text_margin_bottom = "4px"

    calculadora_style = {
        "background_color": "#f0f4f8",
        "border_radius": "12px",
        "padding_y": "32px",
        "padding_x": "24px",
        "margin_top": "32px",
        "margin_bottom": "48px",
        "width": "100%"
    }

    return rx.box(
        rx.vstack(
            # Encabezado
            rx.heading("Aprender sobre Inversión", size="8", margin_top="20px", margin_bottom="16px", text_align="center", font_weight="bold"),
            rx.text(
                "¡Bienvenido a la sección 'Aprender'! Aquí encontrarás los conocimientos fundamentales para convertirte en un inversor informado y exitoso. Antes de adentrarte en el mundo de la inversión, te guiaremos a través de conceptos clave que te ayudarán a tomar decisiones inteligentes y a comprender mejor la dinámica del mercado.",
                size="4", margin_bottom="40px", text_align="center", max_width="800px", margin_x="auto"
            ),

            # Herramientas Financieras (Nueva sección)
            rx.heading("Herramientas Financieras", size="7", margin_top="32px", margin_bottom="24px", text_align="center"),

            # Calculadora de Interés Compuesto
            calculadora_interes_compuesto_component(),

            # Conversor de Monedas
            rx.box(conversor_monedas_component(), **calculadora_style),

            # Resto de las secciones educativas
            # 1. Cartera Permanente
            rx.box(
                rx.vstack(
                    rx.heading("1. Cartera Permanente (Permanent Portfolio)", size="6", margin_bottom="12px"),
                    rx.text(
                        "¿Qué es? La Cartera Permanente es una estrategia de inversión diseñada por el inversor y analista financiero Harry Browne. Se basa en distribuir el capital en cuatro clases de activos principales, cada una con un peso del 25%:",
                        size=text_size
                    ),
                    rx.unordered_list(
                        rx.list_item("25% Acciones", size=text_size),
                        rx.list_item("25% Oro", size=text_size),
                        rx.list_item("25% Bonos", size=text_size),
                        rx.list_item("25% Efectivo", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.text(
                        "¿Cómo funciona? La clave de esta cartera es su diversificación extrema. La idea es que, independientemente del contexto económico, siempre habrá al menos un activo que tenga un buen desempeño, dos que tengan un desempeño moderado y uno que tenga un desempeño deficiente.",
                        margin_top="15px", size=text_size
                    ),
                    rx.unordered_list(
                        rx.list_item(
                            rx.text(
                                rx.text("Crecimiento económico: ", as_="span", font_weight="bold"),
                                rx.text("Las acciones tienden a subir.", as_="span"),
                                as_="span",
                                size=text_size
                            )
                        ),
                        rx.list_item(
                            rx.text(
                                rx.text("Deflación: ", as_="span", font_weight="bold"),
                                rx.text("Los bonos tienden a subir.", as_="span"),
                                size=text_size
                            )
                        ),
                        rx.list_item(
                            rx.text(
                                rx.text("Incertidumbre: ", as_="span", font_weight="bold"),
                                rx.text("El efectivo mantiene su valor.", as_="span"),
                                size=text_size
                            )
                        ),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom, size=text_size),
                    rx.unordered_list(
                        rx.list_item("Esta cartera es un excelente ejemplo de cómo la diversificación puede ayudar a proteger el capital en diferentes condiciones de mercado. Al distribuir las inversiones en activos no correlacionados, se reduce el impacto negativo que puede tener el mal desempeño de un activo en el conjunto de la cartera.", size=text_size),
                        rx.list_item("Analizar el comportamiento histórico de estos cuatro activos nos enseña la importancia de considerar diversos factores económicos al invertir.", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.heading("Distribución y Rendimiento de la Cartera Permanente", size="5", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom),
                    # Visualización Cartera Permanente
                    rx.center(rx.html(render_cartera_permanente_plot())),
                    spacing="3", align_items="stretch"
                ),
                **section_style
            ),

            # 2. Dollar Cost Averaging
            rx.box(
                rx.vstack(
                    rx.heading("2. Dollar Cost Averaging (DCA)", size="6", margin_bottom="12px"),
                    rx.text(
                        "¿Qué es? Dollar Cost Averaging (DCA) es una estrategia de inversión en la que inviertes una cantidad fija de dinero a intervalos regulares (por ejemplo, mensualmente o trimestralmente), independientemente del precio del activo.",
                        size=text_size
                    ),
                    rx.text("Beneficios:", font_weight="bold", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom, size=text_size),
                    rx.unordered_list(
                        rx.list_item("Reduce la volatilidad: Al comprar a diferentes precios, compras más unidades del activo cuando los precios están bajos y menos cuando están altos, lo que suaviza el precio promedio de compra.", size=text_size),
                        rx.list_item("Elimina el factor emocional: Evitas el riesgo de intentar 'adivinar' el mejor momento para entrar al mercado.", size=text_size),
                        rx.list_item("Disciplina de ahorro: Fomenta el hábito de invertir regularmente.", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom, size=text_size),
                    rx.unordered_list(
                        rx.list_item("DCA es una estrategia útil para inversores a largo plazo que buscan reducir el impacto de la volatilidad del mercado.", size=text_size),
                        rx.list_item("Comprender DCA ayuda a tomar decisiones de inversión más racionales y menos impulsivas.", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.heading("Comparación de DCA vs. Inversión de Suma Global", size="5", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom),
                    # Visualización DCA
                    rx.center(rx.html(render_dca_plot())),
                    spacing="3", align_items="stretch"
                ),
                **section_style
            ),

            # 3. Interés Compuesto
            rx.box(
                rx.vstack(
                    rx.heading("3. Interés Compuesto y la Importancia del Tiempo", size="6", margin_bottom="12px"),
                    rx.text(
                        "¿Qué es? El interés compuesto es el interés que se aplica no solo al capital inicial, sino también a los intereses acumulados de periodos anteriores. Es decir, ¡ganas intereses sobre tus intereses!",
                        size=text_size
                    ),
                    rx.text(
                        "El poder del tiempo: Cuanto antes empieces a invertir, más tiempo tendrá tu dinero para crecer gracias al interés compuesto. Incluso pequeñas cantidades invertidas a largo plazo pueden generar grandes resultados.",
                        margin_top="8px", size=text_size
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom, size=text_size),
                    rx.unordered_list(
                        rx.list_item("El interés compuesto es una fuerza poderosa en las inversiones a largo plazo.", size=text_size),
                        rx.list_item("Este concepto subraya la importancia de la planificación financiera temprana y la paciencia.", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.heading("Crecimiento con Interés Compuesto vs. Interés Simple", size="5", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom),
                    # Visualización Interés Compuesto
                    rx.center(rx.html(render_interes_compuesto_plot())),
                    spacing="3", align_items="stretch"
                ),
                **section_style
            ),

            # 4. Riesgo vs. Rendimiento
            rx.box(
                rx.vstack(
                    rx.heading("4. Riesgo vs. Rendimiento", size="6", margin_bottom="12px"),
                    rx.text(
                        "¿Qué es? En el mundo de las inversiones, generalmente existe una relación directa entre el riesgo y el rendimiento potencial. A mayor rendimiento esperado, mayor es el riesgo de perder dinero, y viceversa.",
                        size=text_size
                    ),
                    rx.text("Ejemplos:", font_weight="bold", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom, size=text_size),
                    rx.unordered_list(
                        rx.list_item("Activos de renta variable (por ejemplo, acciones): Pueden ofrecer mayores rendimientos, pero también conllevan mayor volatilidad y riesgo de pérdidas.", size=text_size),
                        rx.list_item("Activos de renta fija (por ejemplo, bonos): Suelen ser más estables, pero ofrecen rendimientos más modestos.", size=text_size),
                        rx.list_item("Diversificación: Invertir en una variedad de activos puede ayudar a equilibrar el riesgo y el rendimiento de una cartera.", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.heading("Relación entre Riesgo y Rendimiento", size="5", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom),
                    # Visualización Riesgo vs Rendimiento
                    rx.center(rx.html(render_riesgo_rendimiento_plot())),
                    spacing="3", align_items="stretch"
                ),
                **section_style
            ),

            # 5. Errores Psicológicos Comunes al Invertir
            rx.box(
                rx.vstack(
                    rx.heading("5. Errores Psicológicos Comunes al Invertir", size="6", margin_bottom="12px"),
                    rx.text(
                        "¿Por qué es importante? Nuestras emociones pueden jugarnos malas pasadas al invertir. Es fundamental reconocer los errores psicológicos más comunes para evitar tomar decisiones impulsivas y perjudiciales.",
                        size=text_size
                    ),
                    rx.text("Errores comunes:", font_weight="bold", margin_top=bold_text_margin_top, margin_bottom=bold_text_margin_bottom, size=text_size),
                    rx.unordered_list(
                        rx.list_item("FOMO (Fear of Missing Out): Miedo a perderse una oportunidad, lo que lleva a comprar activos sobrevalorados.", size=text_size),
                        rx.list_item("Pánico: Vender activos en momentos de caída por miedo a perder más, en lugar de mantener la calma y esperar la recuperación.", size=text_size),
                        rx.list_item("Sesgo de confirmación: Buscar solo información que confirme nuestras creencias y descartar la evidencia en contra.", size=text_size),
                        rx.list_item("Sobreconfianza: Creer que tenemos más conocimientos de los que realmente tenemos, lo que lleva a tomar riesgos excesivos.", size=text_size),
                        margin_left="20px", margin_y="8px", spacing=list_item_spacing
                    ),
                    rx.text("Consejo: Antes de comprar por FOMO, investiga el activo y compara su precio con su valor histórico.", size=text_size),
                    spacing="3", align_items="stretch"
                ),
                **section_style
            ),

            width="100%", max_width="960px", spacing="6",
            align_items="stretch",
            margin_x="auto",
            margin_bottom="64px"
        ),
        width="100%", min_height="100vh",
        padding_y="32px", padding_x="24px",
        display="flex", flex_direction="column", align_items="center",
        background_color="#ffffff"
    )


# --- FUNCIONES PARA GENERAR LOS GRÁFICOS ---
def render_cartera_permanente_plot():
    # Datos para el gráfico circular
    labels = ['Acciones', 'Bonos', 'Oro', 'Efectivo']
    values = [25, 25, 25, 25]
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']

    # Crear el gráfico circular
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, showlegend=False)
    
    # Convertir a HTML
    return fig.to_html(full_html=False, include_plotlyjs="cdn")

def render_dca_plot():
    # Datos para el gráfico de barras
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
    dca_values = [100, 200, 300, 400]
    suma_global_values = [120, 220, 280, 450]

    # Crear el gráfico de barras
    fig = go.Figure(data=[
        go.Bar(name='DCA', x=meses, y=dca_values),
        go.Bar(name='Suma Global', x=meses, y=suma_global_values)
    ])
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, showlegend=False)

    # Convertir a HTML
    return fig.to_html(full_html=False, include_plotlyjs="cdn")

def render_interes_compuesto_plot():
    # Datos para el gráfico de líneas
    anios = [str(i) for i in range(0, 41, 10)]  # Años de 0 a 40 de 10 en 10
    compuesto_values = [100, 179, 320, 573, 1028] # Ejemplo de valores, AJUSTAR
    simple_values = [100, 150, 200, 250, 300] # Ejemplo de valores, AJUSTAR

    # Crear el gráfico de líneas
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anios, y=compuesto_values, mode='lines+markers', name='Interés Compuesto'))
    fig.add_trace(go.Scatter(x=anios, y=simple_values, mode='lines+markers', name='Interés Simple'))
    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=300, showlegend=False)

    # Convertir a HTML
    return fig.to_html(full_html=False, include_plotlyjs="cdn")

def render_riesgo_rendimiento_plot():
    # Datos para el gráfico de dispersión
    activos = ['Acciones', 'Bonos', 'Oro']
    riesgo = [15, 5, 8]
    rendimiento = [30, 10, 15]

    # Crear el gráfico de dispersión
    fig = go.Figure(data=go.Scatter(x=riesgo, y=rendimiento, mode='markers', text=activos))
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Riesgo (Volatilidad)",
        yaxis_title="Rendimiento Esperado",
        height=300
    )

    # Convertir a HTML
    return fig.to_html(full_html=False, include_plotlyjs="cdn")

# --- REGISTRO DE LA PÁGINA ---
aprender = rx.page(
    route="/aprender",
    title="TradeSim - Aprender"
)(aprender_page)