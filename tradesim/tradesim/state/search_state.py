import reflex as rx
import yfinance as yf
import os

class SearchState(rx.State):
    # Mapping of company names to symbols (add more as needed)
    company_map = {
        "APPLE": "AAPL",
        "MICROSOFT": "MSFT",
        "GOOGLE": "GOOGL",
        "ALPHABET": "GOOGL",
        "AMAZON": "AMZN",
        "META": "META",
        "FACEBOOK": "META",
        "TESLA": "TSLA",
        "NVIDIA": "NVDA",
        "BERKSHIRE HATHAWAY": "BRK.B",
        "JPMORGAN": "JPM",
        "VISA": "V",
        "UNITEDHEALTH": "UNH",
        "HOME DEPOT": "HD",
        "PROCTER & GAMBLE": "PG",
        "MASTERCARD": "MA",
        "ELI LILLY": "LLY",
        "BROADCOM": "AVGO",
        "EXXON MOBIL": "XOM",
        "COSTCO": "COST",
        "ABBVIE": "ABBV",
        "PEPSICO": "PEP",
        "COCA-COLA": "KO",
        "COCA COLA": "KO",
        "MERCK": "MRK",
        "WALMART": "WMT",
        "BANK OF AMERICA": "BAC",
        "DISNEY": "DIS",
        "ADOBE": "ADBE",
        "PFIZER": "PFE",
        "CISCO": "CSCO",
        "ORACLE": "ORCL",
        "AT&T": "T",
        "INTEL": "INTC",
        "NETFLIX": "NFLX",
        "SALESFORCE": "CRM",
        "ABBOTT": "ABT",
        "MCDONALD'S": "MCD",
        "NIKE": "NKE",
        "QUALCOMM": "QCOM",
        "VERIZON": "VZ",
        "THERMO FISHER": "TMO",
        "DANAHER": "DHR",
        "ACCENTURE": "ACN",
    }

    search_query: str = ""
    search_result: dict = {}

    def search_stock(self):
        """Fetch stock data using the yfinance API."""
        if not self.search_query:
            self.search_result = {"Error": "Please enter a valid stock symbol or company name."}
            return

        try:
            query = self.search_query.strip().upper()
            # Check if query is a symbol or a company name
            symbol = query
            if query not in self.company_map and not os.path.exists(os.path.join("assets", f"{query}.png")):
                # Try to match by company name
                symbol = self.company_map.get(query)
                if not symbol:
                    self.search_result = {"Error": "Company not found."}
                    return

            if query in self.company_map:
                symbol = self.company_map[query]

            stock = yf.Ticker(symbol)
            info = stock.info

            logo_file = os.path.join("assets", f"{symbol.upper()}.png")
            if os.path.exists(logo_file):
                logo_url = f"/assets/{symbol.upper()}.png"
            else:
                logo_url = None

            self.search_result = {
                "Logo": logo_url,
                "Name": info.get("longName", "N/A"),
                "Symbol": info.get("symbol", "N/A"),
                "Current Price": info.get("currentPrice", "N/A"),
                "Market Cap": info.get("marketCap", "N/A"),
            }
        except Exception as e:
            self.search_result = {"Error": f"Error fetching data: {str(e)}"}