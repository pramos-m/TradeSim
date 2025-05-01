import reflex as rx
import yfinance as yf
import os

class SearchState(rx.State):
    # User's search input
    search_query: str = ""  # This will store the stock symbol entered by the user

    # Search result to display below the search bar
    search_result: dict = {}  # Store the result as a dictionary for better formatting

    def search_stock(self):
        """Fetch stock data using the yfinance API."""
        # Check if the search query is empty
        if not self.search_query:
            self.search_result = {"Error": "Please enter a valid stock symbol."}
            return

        try:
            # Use yfinance to fetch stock data
            stock = yf.Ticker(self.search_query)
            info = stock.info  # Fetch stock information

            # Construct the logo file path
            logo_file = f"assets/{self.search_query.upper()}.png"
            if os.path.exists(logo_file):
                logo_url = f"/{logo_file}"  # Use the relative path for the logo
            else:
                logo_url = None  # No logo available

            # Store the result as a dictionary
            self.search_result = {
                "Logo": logo_url,  # Use the static logo URL
                "Name": info.get("longName", "N/A"),
                "Symbol": info.get("symbol", "N/A"),
                "Current Price": info.get("currentPrice", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
            }
        except Exception as e:
            # Handle errors (e.g., invalid stock symbol or API issues)
            self.search_result = {"Error": f"Error fetching data: {str(e)}"}