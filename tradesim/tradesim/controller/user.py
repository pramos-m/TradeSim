from sqlalchemy.orm import Session
from ..models.user import User
import base64
from sqlalchemy.sql import func
from sqlalchemy import desc
from ..models.stock import Stock
from ..models.transaction import StockTransaction
from decimal import Decimal
from typing import Dict, List, Tuple, Optional

def create_user(db: Session, username: str, email: str, password: str):
    """Create a new user with default balance."""
    user = User(username=username, email=email)
    user.set_password(password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users."""
    return db.query(User).offset(skip).limit(limit).all()

def update_profile_picture(db: Session, user_id: int, picture_data: bytes, picture_type: str) -> User:
    """Update user's profile picture."""
    user = get_user_by_id(db, user_id)
    if user:
        user.profile_picture = picture_data
        user.profile_picture_type = picture_type
        db.commit()
        db.refresh(user)
    return user

def get_user_profile_picture(db: Session, user_id: int):
    """Retrieve user's profile picture."""
    user = get_user_by_id(db, user_id)
    if user and user.profile_picture:
        return user.profile_picture, user.profile_picture_type
    return None, None

# Nuevas funciones de consulta de acciones
def get_user_stocks(db: Session, user_id: int) -> List[Dict]:
    """
    Obtener todas las acciones que posee un usuario con su información completa.
    Retorna una lista con los datos de las acciones y la cantidad que posee.
    """
    # Obtener todas las transacciones del usuario
    portfolio = {}
    transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).all()
    
    for transaction in transactions:
        stock_id = transaction.stock_id
        if stock_id not in portfolio:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            portfolio[stock_id] = {
                "id": stock.id,
                "symbol": stock.symbol,
                "name": stock.name,
                "sector_id": stock.sector_id,
                "sector_name": stock.sector.sector_name,
                "current_price": float(stock.current_price),
                "shares": 0,
                "average_buy_price": 0.0,
                "total_investment": 0.0,
                "market_value": 0.0,
                "profit_loss": 0.0,
                "profit_loss_percentage": 0.0
            }
        
        # Actualizar la posición
        if transaction.quantity > 0:  # Compra
            current_shares = portfolio[stock_id]["shares"]
            current_investment = portfolio[stock_id]["total_investment"]
            new_shares = current_shares + transaction.quantity
            new_investment = current_investment + (float(transaction.price) * transaction.quantity)
            
            # Recalcular precio promedio
            if new_shares > 0:
                portfolio[stock_id]["average_buy_price"] = new_investment / new_shares
            
            portfolio[stock_id]["shares"] = new_shares
            portfolio[stock_id]["total_investment"] = new_investment
        else:  # Venta
            portfolio[stock_id]["shares"] += transaction.quantity
    
    # Filtrar posiciones activas y calcular valores actuales
    active_positions = []
    for stock_id, position in portfolio.items():
        if position["shares"] > 0:
            # Calcular valor de mercado y ganancias/pérdidas
            position["market_value"] = position["current_price"] * position["shares"]
            position["profit_loss"] = position["market_value"] - position["total_investment"]
            
            # Calcular porcentaje de retorno
            if position["total_investment"] > 0:
                position["profit_loss_percentage"] = (position["profit_loss"] / position["total_investment"]) * 100
            else:
                position["profit_loss_percentage"] = 0.0
                
            active_positions.append(position)
    
    return active_positions

def search_stocks_by_name_or_symbol(db: Session, search_term: str, limit: int = 10) -> List[Stock]:
    """
    Buscar acciones por nombre o símbolo que coincidan con el término de búsqueda.
    """
    search_pattern = f"%{search_term}%"
    return db.query(Stock).filter(
        (Stock.name.ilike(search_pattern)) | 
        (Stock.symbol.ilike(search_pattern))
    ).limit(limit).all()

def get_user_account_balance(db: Session, user_id: int) -> float:
    """
    Obtener el saldo actual de la cuenta del usuario.
    """
    user = get_user_by_id(db, user_id)
    if user:
        return float(user.account_balance)
    return 0.0

def get_user_portfolio_summary(db: Session, user_id: int) -> Dict:
    """
    Obtener un resumen del portafolio del usuario incluyendo:
    - Valor total de mercado
    - Total de inversión
    - Ganancia/pérdida total
    - Retorno de inversión (%)
    """
    stocks = get_user_stocks(db, user_id)
    balance = get_user_account_balance(db, user_id)
    
    total_market_value = sum(stock["market_value"] for stock in stocks)
    total_investment = sum(stock["total_investment"] for stock in stocks)
    total_profit_loss = sum(stock["profit_loss"] for stock in stocks)
    
    # Calcular ROI (Return on Investment)
    roi_percentage = 0.0
    if total_investment > 0:
        roi_percentage = (total_profit_loss / total_investment) * 100
    
    return {
        "total_market_value": total_market_value,
        "total_investment": total_investment,
        "total_profit_loss": total_profit_loss,
        "roi_percentage": roi_percentage,
        "account_balance": balance,
        "portfolio_value": total_market_value + balance
    }
