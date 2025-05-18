# crud/ranking.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from ..models.user import User
from ..models.transaction import StockTransaction
from ..models.stock import Stock
from typing import List, Dict
from decimal import Decimal
from .user import get_user_portfolio_summary

def get_user_ranking(db: Session, limit: int = 10) -> List[Dict]:
    """
    Ranking de ejemplo con 10 usuarios inventados para pruebas.
    """
    usuarios_ficticios = [
        {"user_id": 1, "username": "ElonMusk", "roi_percentage": 45.2, "profit_loss": 4520.0},
        {"user_id": 2, "username": "WarrenBuffett", "roi_percentage": 38.7, "profit_loss": 3870.0},
        {"user_id": 3, "username": "CathieWood", "roi_percentage": 32.1, "profit_loss": 3210.0},
        {"user_id": 4, "username": "RayDalio", "roi_percentage": 28.4, "profit_loss": 2840.0},
        {"user_id": 5, "username": "PeterLynch", "roi_percentage": 22.9, "profit_loss": 2290.0},
        {"user_id": 6, "username": "BenjaminGraham", "roi_percentage": 18.3, "profit_loss": 1830.0},
        {"user_id": 7, "username": "GeorgeSoros", "roi_percentage": 12.7, "profit_loss": 1270.0},
        {"user_id": 8, "username": "JohnTempleton", "roi_percentage": 7.5, "profit_loss": 750.0},
        {"user_id": 9, "username": "JesseLivermore", "roi_percentage": 3.2, "profit_loss": 320.0},
        {"user_id": 10, "username": "PaulTudorJones", "roi_percentage": -2.1, "profit_loss": -210.0},
    ]
    # Ordenar por ROI descendente
    usuarios_ficticios.sort(key=lambda x: x["roi_percentage"], reverse=True)
    # Añadir posición y campos extra para compatibilidad
    for i, user in enumerate(usuarios_ficticios):
        user["position"] = i + 1
        user["initial_balance"] = 10000.0
        user["current_balance"] = 10000.0 + user["profit_loss"]
        user["portfolio_value"] = user["profit_loss"]
        user["total_value"] = 10000.0 + user["profit_loss"]
    return usuarios_ficticios[:limit]

def get_top_performing_stocks(db: Session, limit: int = 5) -> List[Dict]:
    """
    Obtener las acciones con mejor rendimiento basado en transacciones
    
    Args:
        db: Sesión de base de datos
        limit: Número máximo de acciones a retornar
        
    Returns:
        Lista de diccionarios con información de las acciones mejor rendimiento
    """
    # Obtener todas las acciones
    stocks = db.query(Stock).all()
    
    stock_performance = []
    for stock in stocks:
        # Obtener la primera transacción para esta acción
        first_tx = db.query(StockTransaction).filter(
            StockTransaction.stock_id == stock.id
        ).order_by(StockTransaction.timestamp).first()
        
        if first_tx:
            # Calcular cambio porcentual desde la primera transacción
            first_price = float(first_tx.price_per_share)
            current_price = float(stock.current_price)
            
            price_change_percentage = 0.0
            if first_price > 0:
                price_change_percentage = ((current_price - first_price) / first_price) * 100
            
            stock_performance.append({
                "stock_id": stock.id,
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector.sector_name,
                "first_price": first_price,
                "current_price": current_price,
                "price_change": current_price - first_price,
                "price_change_percentage": price_change_percentage
            })
    
    # Ordenar por cambio porcentual descendente
    stock_performance.sort(key=lambda x: x["price_change_percentage"], reverse=True)
    
    # Aplicar límite
    return stock_performance[:limit]

def get_user_ranking_by_id(db: Session, user_id: int) -> Dict:
    """
    Obtener la posición en el ranking para un usuario específico
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        
    Returns:
        Diccionario con información de ranking del usuario
    """
    # Primero obtenemos el ranking completo
    ranking = get_user_ranking(db, limit=None)  # Sin límite para obtener todos los usuarios
    
    # Buscamos al usuario específico
    user_ranking = None
    for rank_data in ranking:
        if rank_data["user_id"] == user_id:
            user_ranking = rank_data
            break
    
    if not user_ranking:
        # Si el usuario no está en el ranking, calculamos su información
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")
            
        portfolio_summary = get_user_portfolio_summary(db, user_id)
        total_value = portfolio_summary["portfolio_value"]
        initial_balance = float(user.initial_balance)
        
        roi = 0.0
        if initial_balance > 0:
            roi = ((total_value - initial_balance) / initial_balance) * 100
            
        user_ranking = {
            "user_id": user_id,
            "username": user.username,
            "initial_balance": initial_balance,
            "current_balance": portfolio_summary["account_balance"],
            "portfolio_value": portfolio_summary["total_market_value"],
            "total_value": total_value,
            "roi_percentage": roi,
            "profit_loss": total_value - initial_balance,
            "position": "No clasificado"  # No está en el top
        }
    
    return user_ranking