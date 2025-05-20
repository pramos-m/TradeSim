# tradesim/tradesim/models/__init__.py
from .base import BaseModel # Asumiendo que tienes un base.py con BaseModel = SQLModel
from .user import User, UserCreate, UserRead, UserUpdate
from .sector import Sector, SectorCreate, SectorRead, SectorUpdate
from .stock import Stock, StockCreate, StockRead, StockUpdate # Stock ya no define StockTransaction
from .portfolio_item import PortfolioItemDB, PortfolioItemCreate, PortfolioItemRead, PortfolioItemUpdate # Asegúrate que estos esquemas existen
from .transaction import StockTransaction, TransactionCreate, TransactionRead, TransactionType # TransactionType también se exporta
from .stock_price_history import StockPriceHistory, StockPriceHistoryCreate, StockPriceHistoryRead

__all__ = [
    'BaseModel',
    'User', 'UserCreate', 'UserRead', 'UserUpdate',
    'Sector', 'SectorCreate', 'SectorRead', 'SectorUpdate',
    'Stock', 'StockCreate', 'StockRead', 'StockUpdate',
    'StockPriceHistory', 'StockPriceHistoryCreate', 'StockPriceHistoryRead',
    'StockTransaction', 'TransactionCreate', 'TransactionRead', 'TransactionType',
    'PortfolioItemDB', 'PortfolioItemCreate', 'PortfolioItemRead', 'PortfolioItemUpdate',
]
