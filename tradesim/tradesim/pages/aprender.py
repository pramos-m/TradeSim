import reflex as rx

def aprender_page() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Aprender", size="6", margin_top="32px", margin_bottom="16px"),
            rx.text(
                "¡Bienvenido a la sección 'Aprender'! Aquí encontrarás los conocimientos fundamentales para convertirte en un inversor informado y exitoso. Antes de adentrarte en el mundo de la inversión, te guiaremos a través de conceptos clave que te ayudarán a tomar decisiones inteligentes y a comprender mejor la dinámica del mercado.",
                font_size="lg",
                margin_bottom="32px"
            ),
            # 1. Cartera Permanente
            rx.box(
                rx.vstack(
                    rx.heading("1. Cartera Permanente (Permanent Portfolio)", size="4"),
                    rx.text(
                        "¿Qué es? La Cartera Permanente es una estrategia de inversión diseñada por el inversor y analista financiero Harry Browne. Se basa en distribuir el capital en cuatro clases de activos principales, cada una con un peso del 25%:"
                    ),
                    rx.unordered_list(
                        rx.list_item("25% Acciones"),
                        rx.list_item("25% Oro"),
                        rx.list_item("25% Bonos"),
                        rx.list_item("25% Efectivo"),
                        margin_left="20px"
                    ),
                    rx.text(
                        "¿Cómo funciona? La clave de esta cartera es su diversificación extrema. La idea es que, independientemente del contexto económico, siempre habrá al menos un activo que tenga un buen desempeño, dos que tengan un desempeño moderado y uno que tenga un desempeño deficiente.",
                        margin_top="8px"
                    ),
                    rx.unordered_list(
                        rx.list_item("Crecimiento económico: Las acciones tienden a subir."),
                        rx.list_item("Inflación: El oro tiende a subir."),
                        rx.list_item("Deflación: Los bonos tienden a subir."),
                        rx.list_item("Incertidumbre: El efectivo mantiene su valor."),
                        margin_left="20px"
                    ),
                    rx.text(
                        "¿Qué puedes aprender sobre esto?",
                        font_weight="bold",
                        margin_top="8px"
                    ),
                    rx.unordered_list(
                        rx.list_item("Esta cartera es un excelente ejemplo de cómo la diversificación puede ayudar a proteger el capital en diferentes condiciones de mercado. Al distribuir las inversiones en activos no correlacionados, se reduce el impacto negativo que puede tener el mal desempeño de un activo en el conjunto de la cartera."),
                        rx.list_item("Analizar el comportamiento histórico de estos cuatro activos nos enseña la importancia de considerar diversos factores económicos al invertir."),
                        margin_left="20px"
                    ),
                    rx.text(
                        "Visualización sugerida:",
                        font_weight="bold",
                        margin_top="8px"
                    ),
                    rx.unordered_list(
                        rx.list_item("Gráfico circular que muestre la distribución 25% - 25% - 25% - 25%."),
                        rx.list_item("Gráfico de líneas comparando el rendimiento de la Cartera Permanente vs. una cartera de solo acciones durante un periodo de tiempo que ilustre la volatilidad."),
                        margin_left="20px"
                    ),
                    margin_bottom="32px"
                ),
                background="#f7f7f7",
                border_radius="xl",
                padding="24px",
                margin_bottom="24px"
            ),
            # 2. Dollar Cost Averaging
            rx.box(
                rx.vstack(
                    rx.heading("2. Dollar Cost Averaging (DCA)", size="4"),
                    rx.text(
                        "¿Qué es? Dollar Cost Averaging (DCA) es una estrategia de inversión en la que inviertes una cantidad fija de dinero a intervalos regulares (por ejemplo, mensualmente o trimestralmente), independientemente del precio del activo."
                    ),
                    rx.text("Beneficios:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Reduce la volatilidad: Al comprar a diferentes precios, compras más unidades del activo cuando los precios están bajos y menos cuando están altos, lo que suaviza el precio promedio de compra."),
                        rx.list_item("Elimina el factor emocional: Evitas el riesgo de intentar 'adivinar' el mejor momento para entrar al mercado."),
                        rx.list_item("Disciplina de ahorro: Fomenta el hábito de invertir regularmente."),
                        margin_left="20px"
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("DCA es una estrategia útil para inversores a largo plazo que buscan reducir el impacto de la volatilidad del mercado."),
                        rx.list_item("Comprender DCA ayuda a tomar decisiones de inversión más racionales y menos impulsivas."),
                        margin_left="20px"
                    ),
                    rx.text("Visualización sugerida:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Tabla que muestre un ejemplo de compras mensuales de 100€ de un activo con precios fluctuantes, calculando el precio promedio y comparándolo con una inversión inicial única."),
                        rx.list_item("Gráfico de barras comparando el resultado de DCA vs. inversión de suma global."),
                        margin_left="20px"
                    ),
                    margin_bottom="32px"
                ),
                background="#f7f7f7",
                border_radius="xl",
                padding="24px",
                margin_bottom="24px"
            ),
            # 3. Interés Compuesto
            rx.box(
                rx.vstack(
                    rx.heading("3. Interés Compuesto y la Importancia del Tiempo", size="4"),
                    rx.text(
                        "¿Qué es? El interés compuesto es el interés que se aplica no solo al capital inicial, sino también a los intereses acumulados de periodos anteriores. Es decir, ¡ganas intereses sobre tus intereses!"
                    ),
                    rx.text(
                        "El poder del tiempo: Cuanto antes empieces a invertir, más tiempo tendrá tu dinero para crecer gracias al interés compuesto. Incluso pequeñas cantidades invertidas a largo plazo pueden generar grandes resultados.",
                        margin_top="8px"
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("El interés compuesto es una fuerza poderosa en las inversiones a largo plazo."),
                        rx.list_item("Este concepto subraya la importancia de la planificación financiera temprana y la paciencia."),
                        margin_left="20px"
                    ),
                    rx.text("Visualización sugerida:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Gráfico de líneas que muestre una curva exponencial del crecimiento del dinero con interés compuesto a lo largo del tiempo, comparado con un crecimiento lineal (interés simple)."),
                        rx.list_item("Calculadora interactiva donde el usuario pueda ingresar un capital inicial, tasa de interés y plazo para ver el resultado del interés compuesto."),
                        margin_left="20px"
                    ),
                    margin_bottom="32px"
                ),
                background="#f7f7f7",
                border_radius="xl",
                padding="24px",
                margin_bottom="24px"
            ),
            # 4. Riesgo vs. Rendimiento
            rx.box(
                rx.vstack(
                    rx.heading("4. Riesgo vs. Rendimiento", size="4"),
                    rx.text(
                        "¿Qué es? En el mundo de las inversiones, generalmente existe una relación directa entre el riesgo y el rendimiento potencial. A mayor rendimiento esperado, mayor es el riesgo de perder dinero, y viceversa."
                    ),
                    rx.text("Ejemplos:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Activos de renta variable (por ejemplo, acciones): Pueden ofrecer mayores rendimientos, pero también conllevan mayor volatilidad y riesgo de pérdidas."),
                        rx.list_item("Activos de renta fija (por ejemplo, bonos): Suelen ser más estables, pero ofrecen rendimientos más modestos."),
                        rx.list_item("Diversificación: Invertir en una variedad de activos puede ayudar a equilibrar el riesgo y el rendimiento de una cartera."),
                        margin_left="20px"
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Es fundamental comprender la tolerancia al riesgo personal antes de tomar decisiones de inversión."),
                        rx.list_item("No existe una inversión 'libre de riesgo', y todo inversor debe ser consciente del equilibrio entre riesgo y recompensa."),
                        margin_left="20px"
                    ),
                    rx.text("Visualización sugerida:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Gráfico de dispersión donde el eje X represente el riesgo (volatilidad) y el eje Y el rendimiento, mostrando diferentes tipos de activos."),
                        rx.list_item("Barras comparativas mostrando el rango de fluctuación de precios (volatilidad) de diferentes activos."),
                        margin_left="20px"
                    ),
                    margin_bottom="32px"
                ),
                background="#f7f7f7",
                border_radius="xl",
                padding="24px",
                margin_bottom="24px"
            ),
            # 5. Errores Psicológicos Comunes al Invertir
            rx.box(
                rx.vstack(
                    rx.heading("5. Errores Psicológicos Comunes al Invertir", size="4"),
                    rx.text(
                        "¿Por qué es importante? Nuestras emociones pueden jugarnos malas pasadas al invertir. Es fundamental reconocer los errores psicológicos más comunes para evitar tomar decisiones impulsivas y perjudiciales."
                    ),
                    rx.text("Errores comunes:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("FOMO (Fear of Missing Out): Miedo a perderse una oportunidad, lo que lleva a comprar activos sobrevalorados."),
                        rx.list_item("Pánico: Vender activos en momentos de caída por miedo a perder más, en lugar de mantener la calma y esperar la recuperación."),
                        rx.list_item("Sesgo de confirmación: Buscar solo información que confirme nuestras creencias y descartar la evidencia en contra."),
                        rx.list_item("Sobreconfianza: Creer que tenemos más conocimientos de los que realmente tenemos, lo que lleva a tomar riesgos excesivos."),
                        margin_left="20px"
                    ),
                    rx.text("¿Qué puedes aprender sobre esto?", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("La psicología juega un papel crucial en las decisiones financieras."),
                        rx.list_item("Desarrollar la disciplina emocional y la objetividad es tan importante como comprender los aspectos financieros."),
                        margin_left="20px"
                    ),
                    rx.text("Visualización sugerida:", font_weight="bold", margin_top="8px"),
                    rx.unordered_list(
                        rx.list_item("Infografía con viñetas y dibujos ilustrativos que representen cada error psicológico."),
                        rx.list_item("Recuadro de 'Consejos' con estrategias para combatir cada sesgo (por ejemplo, 'Antes de comprar por FOMO, investiga el activo y compara su precio con su valor histórico')."),
                        margin_left="20px"
                    ),
                    margin_bottom="32px"
                ),
                background="#f7f7f7",
                border_radius="xl",
                padding="24px",
                margin_bottom="24px"
            ),
            # Consideraciones adicionales
            rx.box(
                rx.vstack(
                    rx.heading("Consideraciones Adicionales", size="4"),
                    rx.unordered_list(
                        rx.list_item("Interactividad: Incorpora elementos interactivos como cuestionarios cortos al final de cada sección para reforzar el aprendizaje."),
                        rx.list_item("Glosario: Incluye un glosario con la definición de términos financieros clave."),
                        rx.list_item("Progresión: Organiza los temas en orden de dificultad creciente."),
                        rx.list_item("Diseño: Utiliza un diseño atractivo y fácil de leer, con suficiente espacio en blanco y elementos visuales claros."),
                        margin_left="20px"
                    ),
                ),
                background="#e3e8f0",
                border_radius="xl",
                padding="24px",
                margin_bottom="32px"
            ),
            width="100%",
            max_width="900px",
            margin_x="auto",
            margin_bottom="64px"
        ),
        width="100%",
        min_height="100vh",
        background="white"
    )

page = aprender_page