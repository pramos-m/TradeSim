# NOMBRE_DE_TU_APP_MODULO/state/search_state.py

import reflex as rx
import yfinance as yf
import os
import traceback
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.stock import Stock

class SearchState(rx.State):
    company_map = {
        "APPLE": "AAPL", "MICROSOFT": "MSFT", "GOOGLE": "GOOG", "ALPHABET": "GOOG",
        "AMAZON": "AMZN", "META": "META", "FACEBOOK": "META", "TESLA": "TSLA",
        "NVIDIA": "NVDA", "BERKSHIRE HATHAWAY": "BRK.B", "JPMORGAN": "JPM",
        "VISA": "V", "UNITEDHEALTH": "UNH", "HOME DEPOT": "HD",
        "PROCTER & GAMBLE": "PG", "MASTERCARD": "MA", "ELI LILLY": "LLY",
        "BROADCOM": "AVGO", "EXXON MOBIL": "XOM", "COSTCO": "COST",
        "ABBVIE": "ABBV", "PEPSICO": "PEP", "COCA-COLA": "KO", "COCA COLA": "KO",
        "MERCK": "MRK", "WALMART": "WMT", "BANK OF AMERICA": "BAC",
        "DISNEY": "DIS", "ADOBE": "ADBE", "PFIZER": "PFE", "CISCO": "CSCO",
        "ORACLE": "ORCL", "AT&T": "T", "INTEL": "INTC", "NETFLIX": "NFLX",
        "SALESFORCE": "CRM", "ABBOTT": "ABT", "MCDONALD'S": "MCD",
        "NIKE": "NKE", "QUALCOMM": "QCOM", "VERIZON": "VZ",
        "THERMO FISHER": "TMO", "DANAHER": "DHR", "ACCENTURE": "ACN",
    }

    search_query: str = ""
    search_result: dict = {}
    is_searching: bool = False
    search_error: str = ""

    def set_search_query(self, value: str):
        self.search_query = value

    def handle_input_key_down(self, key: str):
        if key == "Enter":
            return self.search_stock()

    @rx.event
    def search_stock(self):
        if not self.search_query:
            self.search_error = "Por favor ingrese un símbolo o nombre de acción"
            return
        
        self.is_searching = True
        self.search_error = ""
        
        db = SessionLocal()
        try:
            # Buscar en la base de datos
            stock = db.query(Stock).filter(
                (Stock.symbol.ilike(f"%{self.search_query}%")) |
                (Stock.name.ilike(f"%{self.search_query}%"))
            ).first()
            
            if stock:
                self.search_result = {
                    "Symbol": stock.symbol,
                    "Name": stock.name,
                    "Price": float(stock.current_price),
                    "Change": 0.0  # TODO: Calcular cambio real
                }
            else:
                self.search_error = f"No se encontró la acción '{self.search_query}'"
                self.search_result = {}
        except Exception as e:
            self.search_error = f"Error al buscar: {str(e)}"
            self.search_result = {}
        finally:
            db.close()
            self.is_searching = False

    @rx.event
    def go_to_stock_detail(self, symbol: str):
        if symbol and symbol != "No encontrado" and not symbol.startswith("Error"):
            return rx.redirect(f"/detalles_accion/{symbol.upper()}")
        return rx.window_alert("No se puede navegar para este resultado.")