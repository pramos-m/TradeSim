import reflex as rx
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random
from typing import List, Dict, Any

# --- Simulated Data (Similar to React Example) ---

def generate_pnl_data(start_value, end_value, points=12):
    """Generates slightly randomized data ending at a specific value."""
    data = [start_value]
    step = (end_value - start_value) / (points - 1)
    for i in range(1, points - 1):
        data.append(data[-1] + step + random.uniform(-abs(step)*0.5, abs(step)*0.5))
    data.append(end_value)
    return data

PNL_DAILY_DATA = generate_pnl_data(5, -40.9)
PNL_MONTHLY_DATA = generate_pnl_data(500, 1391.12)
PNL_YEARLY_DATA = generate_pnl_data(30000, 87090.56)

def generate_chart_data(periods: List[str]) -> Dict[str, pd.DataFrame]:
    """Generates simulated stock price data for different periods."""
    data = {}
    base_prices = {
        "1D": [338, 337, 341, 346, 344, 343, 339, 342, 345, 348, 350, 346, 339, 345, 343, 347, 345],
        "5D": [345, 340, 335, 330, 325, 320, 318, 322, 320, 315, 310, 308, 305, 300, 302],
        "1M": [300, 305, 310, 308, 315, 320, 318, 325, 330, 328, 325, 330, 335, 330, 325],
        "6M": [320, 315, 310, 305, 300, 295, 290, 285, 280, 275, 280, 285, 290, 295],
        "ENG": [290, 300, 295, 305, 310, 305, 320, 330, 325, 335, 345], # Asuming ENG means YTD
        "1A": [250, 275, 290, 285, 300, 320, 310, 335, 345, 340, 355, 345],
        "5A": [150, 180, 210, 195, 230, 260, 250, 280, 300, 290, 325, 345],
        "MAX": [50, 100, 80, 150, 200, 180, 250, 290, 270, 310, 330, 345],
    }
    # Generate simple time labels (replace with actual dates/times later)
    for period, prices in base_prices.items():
        times = [f"T{i+1}" for i in range(len(prices))] # Placeholder times
        data[period] = pd.DataFrame({'time': times, 'price': prices})

    return data

CHART_DATA = generate_chart_data(["1D", "5D", "1M", "6M", "ENG", "1A", "5A", "MAX"])

# --- Reflex State ---
class DashboardState(rx.State):
    """Manages the dashboard's data and interactions."""
    user_name: str = "Elon Musk"
    balance: float = 97717.93
    balance_date: str = datetime.now().strftime("%d/%m/%Y") # Use current date

    # PNL Data
    daily_pnl: float = -40.9
    monthly_pnl: float = 1391.12
    yearly_pnl: float = 87090.56
    pnl_daily_data: List[float] = PNL_DAILY_DATA
    pnl_monthly_data: List[float] = PNL_MONTHLY_DATA
    pnl_yearly_data: List[float] = PNL_YEARLY_DATA

    # Main Chart Data
    selected_period: str = "1D"
    # Store dataframes directly
    chart_data: Dict[str, pd.DataFrame] = CHART_DATA
    # Store hover data from plot event {pointNumber, curveNumber, x, y}
    main_chart_hover_info: Dict | None = None

    # New state variable for toggling display
    show_absolute_change: bool = False # Start showing percentage by default

    @rx.var
    def current_chart_df(self) -> pd.DataFrame:
        """Returns the DataFrame for the selected period."""
        return self.chart_data.get(self.selected_period, pd.DataFrame())

    @rx.var
    def price_change_info(self) -> Dict[str, Any]:
        """Calculates price change details, ensuring float outputs."""
        df = self.current_chart_df
        if df.empty or len(df) < 2:
            # Return explicit floats for default values
            return {"last_price": 0.0, "change": 0.0, "percent_change": 0.0, "is_positive": True}

        last_price = df['price'].iloc[-1]
        first_price = df['price'].iloc[0]
        change = last_price - first_price
        percent_change = (change / first_price * 100) if first_price else 0.0 # Ensure float result
        is_positive = change >= 0

        return {
            # Explicitly cast results to float
            "last_price": float(last_price),
            "change": float(change),
            "percent_change": float(percent_change),
            "is_positive": is_positive
        }

    @rx.var
    def is_change_positive(self) -> bool:
        """Returns the boolean indicating if the change is positive, ensuring Python bool type."""
        # Cast the numpy.bool_ to a standard Python bool
        return bool(self.price_change_info["is_positive"])

    @rx.var
    def formatted_percent_change(self) -> str:
        """Returns the percentage change formatted to two decimal places (no explicit sign)."""
        percent = self.price_change_info["percent_change"]
        # Remove explicit sign formatting, handle zero separately
        return f"{abs(percent):.2f}" # Return absolute value formatted

    @rx.var
    def formatted_change_value(self) -> str:
        """Returns the original change value formatted to two decimal places with sign."""
        change = self.price_change_info["change"]
        # Format with explicit sign using :+.2f
        return f"{change:+.2f}"

    @rx.var
    def chart_color(self) -> str:
        """Determines the chart color based on the positivity flag."""
        return "#22c55e" if self.is_change_positive else "#ef4444"

    @rx.var
    def chart_area_color(self) -> str:
        """Determines the chart area fill color."""
        return "rgba(34, 197, 94, 0.2)" if self.is_change_positive else "rgba(239, 68, 68, 0.2)"

    @rx.var
    def display_price(self) -> float:
        """Shows hover price if available, otherwise last price, ensuring float type."""
        price_to_return = 0.0 # Default value

        if self.main_chart_hover_info and "y" in self.main_chart_hover_info:
            y_value = self.main_chart_hover_info.get("y")
            if isinstance(y_value, (int, float)):
                price_to_return = float(y_value) # Cast to float
            elif isinstance(y_value, list) and y_value:
                 if isinstance(y_value[0], (int, float)):
                    price_to_return = float(y_value[0]) # Cast to float
            elif isinstance(y_value, dict) and 'price' in y_value:
                if isinstance(y_value['price'], (int, float)):
                    price_to_return = float(y_value['price']) # Cast to float
            else:
                 # If hover info exists but 'y' is unusable, fallback to last price
                 price_to_return = float(self.price_change_info.get("last_price", 0.0)) # Cast to float
        else:
            # No hover info, use last price
            price_to_return = float(self.price_change_info.get("last_price", 0.0)) # Cast to float

        return price_to_return

    @rx.var
    def display_time(self) -> str:
        """Shows hover time if available, otherwise empty."""
        if self.main_chart_hover_info and "x" in self.main_chart_hover_info:
            x_value = self.main_chart_hover_info.get("x")
            if isinstance(x_value, str):
                return x_value
            elif isinstance(x_value, list) and x_value and isinstance(x_value[0], str):
                 return x_value[0]
            elif isinstance(x_value, dict) and 'time' in x_value and isinstance(x_value['time'], str):
                return x_value['time']
        return "" # Return empty if no suitable time found

    # --- Computed Variables for Charts ---
    @rx.var
    def main_chart_figure(self) -> go.Figure:
        """Creates the main Plotly chart figure based on current state."""
        df = self.current_chart_df # Access the computed DataFrame Var
        line_color = self.chart_color # Access the computed color Var
        area_color = self.chart_area_color # Access the computed area color Var

        # --- Logic from create_main_chart moved here --- #
        if df.empty: # This check is OK inside the state
            fig = go.Figure()
            fig.update_layout(
                 height=300,
                 paper_bgcolor='white',
                 plot_bgcolor='white',
                 xaxis=dict(visible=False),
                 yaxis=dict(visible=False),
                 annotations=[dict(text="No data available", xref="paper", yref="paper", showarrow=False, font=dict(size=16))]
            )
            return fig

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['price'],
            mode='lines',
            line=dict(width=0),
            fill='tozeroy',
            fillcolor=area_color,
            hoverinfo='skip'
        ))
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['price'],
            mode='lines',
            line=dict(color=line_color, width=2.5, shape='spline'),
            name='Price',
            hovertemplate='<b>Price:</b> %{y:.2f}<br><b>Time:</b> %{x}<extra></extra>'
        ))

        min_price = df['price'].min()
        max_price = df['price'].max()
        padding = (max_price - min_price) * 0.1
        range_min = min_price - padding
        range_max = max_price + padding

        fig.update_layout(
            height=300,
            margin=dict(l=40, r=10, t=10, b=30),
            paper_bgcolor='white',
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=False, zeroline=False, tickmode='auto', nticks=6,
                showline=True, linewidth=1, linecolor='lightgrey',
            ),
            yaxis=dict(
                title=None, showgrid=True, gridcolor='rgba(230, 230, 230, 0.5)', zeroline=False,
                showline=False, side='left', tickformat=".0f", range=[range_min, range_max]
            ),
            hovermode='x unified', showlegend=False, xaxis_tickangle=-30
        )

        num_grid_lines = 4
        y_step = (range_max - range_min) / num_grid_lines
        for i in range(1, num_grid_lines):
             y_val = range_min + i * y_step
             fig.add_shape(
                 type="line", x0=df['time'].iloc[0], x1=df['time'].iloc[-1],
                 y0=y_val, y1=y_val, line=dict(color="rgba(200, 200, 200, 0.8)", width=1)
             )
        return fig
    # --- End Computed Variables --- #

    # --- Event Handlers ---
    def set_period(self, period: str):
        """Updates the selected period and resets hover info."""
        self.selected_period = period
        self.main_chart_hover_info = None

    def handle_hover(self, event_data):
        """Stores the hover event data from the Plotly chart."""
        # Plotly hover events often return a list of points; take the first one
        if event_data and isinstance(event_data, list) and event_data[0]:
            self.main_chart_hover_info = event_data[0]
        else:
             # Clear hover info if event data is not as expected or empty
             self.main_chart_hover_info = None

    def handle_unhover(self, _):
        """Clears hover info when the cursor leaves the plot area."""
        self.main_chart_hover_info = None

    # New event handler to toggle the display mode
    def toggle_change_display(self):
        """Toggles between showing absolute and percentage change."""
        self.show_absolute_change = not self.show_absolute_change


# --- Plotting Functions ---
def create_pnl_chart(data: List[float], color: str = "rgba(255,255,255,0.7)") -> go.Figure:
    """Creates a minimal Plotly figure for PNL cards."""
    fig = go.Figure(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor="rgba(255,255,255,0.1)",
        hoverinfo='none' # Disable hover info for small charts
    ))
    fig.update_layout(
        height=64, # Match height in card
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)', # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


# --- UI Components ---

def pnl_card(title: str, value: rx.Var[float], figure: go.Figure, color: str = "white") -> rx.Component:
    """Creates a UI card for displaying PNL metrics with a pre-rendered chart."""
    # Format value with commas and sign using rx.cond and Python f-string formatting
    formatted_value_str = rx.cond(
        value >= 0,
        f"${value:.2f}",
        f"-${(-value):.2f}"
    )

    return rx.card(
        rx.vstack(
            rx.text(title, size="2", weight="medium", color="rgba(255,255,255,0.9)"),
            rx.text(formatted_value_str, size="6", weight="bold"),
            rx.box(
                rx.plotly(
                    data=figure, # Pass the figure object directly
                    layout={}, # Layout is already set in the figure
                    config={"displayModeBar": False},
                ),
                height="64px",
                width="100%",
            ),
            spacing="1",
            align="start",
        ),
        background_color="var(--accent-9)",
        color="white",
        size="2",
    )

def balance_card(balance: rx.Var[float], date: str) -> rx.Component:
    """Creates a UI card for displaying the balance."""
    return rx.vstack(
        rx.text("Balance", size="3", weight="medium", color="gray"),
        rx.text(f"$ {balance:,.2f}", size="6", weight="bold", color="var(--accent-9)"),
        rx.text("En", size="2", color="gray", margin_top="10px"),
        rx.text(date, size="4", color="var(--accent-9)"),
        align="start",
        padding="16px",
        height="100%",
    )

def period_selector(selected: rx.Var[str], handler: rx.EventHandler) -> rx.Component:
    """Creates the row of buttons for time period selection."""
    periods = ["1D", "5D", "1M", "6M", "ENG", "1A", "5A", "MAX"]
    buttons = []
    for i, period in enumerate(periods):
        is_selected = (selected == period)
        if i > 0:
            buttons.append(rx.text("|", color="lightgray", margin_x="2px", align_self="center"))
        buttons.append(
            rx.button(
                period,
                on_click=lambda p=period: handler(p),
                variant="ghost",
                size="1",
                color_scheme=rx.cond(is_selected, "accent", "gray"),
                font_weight=rx.cond(is_selected, "bold", "normal"),
                padding_x="8px",
                padding_y="4px",
                 _hover={
                     "background_color": rx.cond(is_selected, "var(--accent-4)", "var(--accent-3)")
                 }
            )
        )
    return rx.hstack(*buttons, spacing="1", align="center")


# --- Main Page Function ---
@rx.page(route="/dashboard") # Define route for the page
def dashboard_page() -> rx.Component:
    """Builds the dashboard UI."""

    # --- Pre-generate PNL Figures using the constants --- #
    daily_pnl_figure = create_pnl_chart(PNL_DAILY_DATA)       # Use the constant list
    monthly_pnl_figure = create_pnl_chart(PNL_MONTHLY_DATA)   # Use the constant list
    yearly_pnl_figure = create_pnl_chart(PNL_YEARLY_DATA)    # Use the constant list
    # --- End Pre-generation ---

    return rx.container(
        rx.vstack(
            # Header Section (Optional - Adapt as needed)
            rx.hstack(
                rx.hstack(
                    rx.avatar(fallback="EM", size="3"), # Placeholder avatar
                    rx.text(DashboardState.user_name, weight="bold", size="4"),
                    align="center",
                ),
                rx.spacer(),
                rx.hstack(
                    # Placeholder for "tradesim" logo/text
                    rx.image(src="/logo.png", height="30px", width="auto"), # Add a placeholder logo image to your assets
                    rx.text("tradesim", weight="bold", color="var(--accent-9)"),
                    align="center",
                    spacing="2"
                ),
                justify="between",
                width="100%",
                padding_bottom="16px",
                border_bottom="1px solid var(--gray-a6)",
                margin_bottom="24px",
            ),

            # Main Content Area
            rx.vstack(
                 rx.heading("Dashboard", size="7", weight="bold", margin_bottom="20px"),

                 # Top Cards Row - Pass pre-generated figures
                 rx.grid(
                     pnl_card("Ultimo dia PNL", DashboardState.daily_pnl, daily_pnl_figure),
                     pnl_card("Ultimo mes PNL", DashboardState.monthly_pnl, monthly_pnl_figure),
                     pnl_card("Ultimo año PNL", DashboardState.yearly_pnl, yearly_pnl_figure),
                     balance_card(DashboardState.balance, DashboardState.balance_date),
                     columns="4",
                     spacing="4",
                     width="100%",
                     margin_bottom="24px",
                 ),

                 # Main Chart Section
                 rx.card(
                     rx.vstack(
                         # Price and Change Display
                         rx.vstack(
                             rx.heading(
                                 rx.cond(
                                      DashboardState.main_chart_hover_info,
                                      # Use a single f-string to combine hover info
                                      f"{DashboardState.display_price:.2f} USD @ {DashboardState.display_time}",
                                      # Show last price otherwise, handle initial zero case
                                      rx.cond(
                                          DashboardState.price_change_info['last_price'] != 0,
                                          f"{DashboardState.price_change_info['last_price']:.2f} USD",
                                          "- USD" # Show dash if initial price is 0
                                      )
                                 ),
                                 size="6",
                                 weight="bold"
                             ),
                             # Final adjustments to the change display text
                             rx.hstack( # Use HStack for better alignment of icon and text
                                 # Use rx.match to conditionally render the icon component
                                 rx.match(
                                     DashboardState.is_change_positive, # Condition Var
                                     # Case True: Up triangle
                                     (True, rx.text(
                                                "▲",
                                                font_size="sm",
                                                margin_right="1px",
                                                color=DashboardState.chart_color
                                            )
                                     ),
                                     # Case False: Down triangle
                                     (False, rx.text(
                                                "▼",
                                                font_size="sm",
                                                margin_right="1px",
                                                color=DashboardState.chart_color
                                            )
                                     ),
                                     # Default case (optional but safe)
                                     rx.text("?", font_size="sm") # Fallback if boolean is somehow neither
                                 ),
                                 # Main text component for the value/percentage
                                 rx.text(
                                     # Display formatted original value or formatted percentage
                                     rx.cond(
                                         DashboardState.show_absolute_change,
                                         # Show formatted original value (includes sign)
                                         DashboardState.formatted_change_value,
                                         # Show formatted absolute percentage in brackets
                                         f"({DashboardState.formatted_percent_change} %)"
                                     ),
                                     # Common props
                                     color=DashboardState.chart_color,
                                     size="4",
                                     weight="medium",
                                 ),
                                 # Click handler applied to the container
                                 on_click=DashboardState.toggle_change_display,
                                 cursor="pointer",
                                 align="center", # Align icon and text vertically
                                 spacing="1", # Adjust spacing as needed
                             ),
                             align="start",
                             spacing="1",
                             margin_bottom="10px",
                         ),

                         # Time Period Selector
                         period_selector(DashboardState.selected_period, DashboardState.set_period),

                         # Plotly Chart - Use the computed variable from state
                         rx.plotly(
                             data=DashboardState.main_chart_figure, # <-- Use the computed Var
                             layout={}, # Layout is handled in the computed figure
                             config={"displayModeBar": False, "scrollZoom": False},
                             on_hover=DashboardState.handle_hover,
                             on_unhover=DashboardState.handle_unhover,
                             width="100%",
                             height="300px",
                         ),
                         spacing="3",
                         align="stretch",
                         width="100%",
                     ),
                     width="100%",
                     size="2"
                 ),
                 spacing="5",
                 align="stretch",
                 width="100%",
            ),
            width="100%",
            padding="16px", # Add padding around the whole vstack content
        ),
        maxWidth="1200px", # Limit max width for better readability
        padding="16px",
        # Background color for the whole container if needed
        # background_color="var(--gray-2)"
    )

# Note: You might need to install pandas: pip install pandas
# Make sure you have a placeholder logo image at `assets/tradesim_logo_placeholder.png`
# or remove/change the rx.image component in the header. 