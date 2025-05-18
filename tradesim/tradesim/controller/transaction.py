# crud/transaction.py
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime, timezone
from ..models.transaction import StockTransaction, TransactionType
from ..models.stock import Stock
from ..models.user import User
from typing import List, Optional, Dict, Tuple # Added Dict, Tuple
from sqlalchemy import func, desc # Added func, desc

def get_transaction(db: Session, transaction_id: int):
    return db.query(StockTransaction).filter(StockTransaction.id == transaction_id).first()

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(StockTransaction).filter(StockTransaction.user_id == user_id).order_by(desc(StockTransaction.timestamp)).offset(skip).limit(limit).all()

def get_stock_transactions(db: Session, stock_id: int, skip: int = 0, limit: int = 100):
    return db.query(StockTransaction).filter(StockTransaction.stock_id == stock_id).order_by(desc(StockTransaction.timestamp)).offset(skip).limit(limit).all()

def create_transaction(db: Session, user_id: int, stock_id: int, transaction_type: TransactionType, quantity: int, price_per_share: Decimal) -> StockTransaction:
    """Create a new transaction."""
    transaction = StockTransaction(
        user_id=user_id,
        stock_id=stock_id,
        transaction_type=transaction_type,
        quantity=quantity,
        price_per_share=price_per_share
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_user_portfolio(db: Session, user_id: int):
    # Obtener todas las transacciones del usuario
    transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).all()
    
    # Calcular la posición por cada acción
    portfolio = {}
    for transaction in transactions:
        stock_id = transaction.stock_id
        if stock_id not in portfolio:
            stock = db.query(Stock).filter(Stock.id == stock_id).first()
            portfolio[stock_id] = {
                "stock": stock,
                "shares": 0,
                "average_price": Decimal("0.0"),
                "total_investment": Decimal("0.0")
            }
        
        # Actualizar la posición
        if transaction.quantity > 0:  # Compra
            current_shares = portfolio[stock_id]["shares"]
            current_investment = portfolio[stock_id]["total_investment"]
            new_shares = current_shares + transaction.quantity
            new_investment = current_investment + (transaction.price_per_share * Decimal(str(transaction.quantity))) # Ensure Decimal multiplication
            
            # Recalcular precio promedio
            if new_shares > 0:
                portfolio[stock_id]["average_price"] = new_investment / Decimal(str(new_shares))
            
            portfolio[stock_id]["shares"] = new_shares
            portfolio[stock_id]["total_investment"] = new_investment
        else:  # Venta
            portfolio[stock_id]["shares"] += transaction.quantity # quantity is negative for sells
    
    # Filtrar solo posiciones activas (shares > 0)
    active_positions = {k: v for k, v in portfolio.items() if v["shares"] > 0}
    return active_positions

# Nuevas funciones para comprar y vender acciones

def buy_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[StockTransaction, Dict]:
    """
    Comprar acciones de un determinado valor
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario comprador
        stock_id: ID de la acción a comprar
        quantity: Cantidad de acciones a comprar (número positivo)
    
    Returns:
        Tupla con (transacción creada, resumen de la operación)
    """
    if quantity <= 0:
        raise ValueError("La cantidad a comprar debe ser un número positivo")
    
    # Obtener stock y precio actual
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise ValueError(f"Acción con ID {stock_id} no encontrada")
    
    # Realizar la transacción
    # Ensure stock.current_price is Decimal for create_transaction
    current_price_decimal = Decimal(str(stock.current_price)) if not isinstance(stock.current_price, Decimal) else stock.current_price
    transaction = create_transaction(db, user_id, stock_id, TransactionType.COMPRA, quantity, current_price_decimal)
    
    # Crear resumen de la operación
    summary = {
        "operation": "compra",
        "stock_symbol": stock.symbol,
        "stock_name": stock.name,
        "quantity": quantity,
        "price_per_share": float(current_price_decimal),
        "total_amount": float(current_price_decimal) * quantity,
        "timestamp": transaction.timestamp.isoformat(),
    }
    
    return transaction, summary

def sell_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[StockTransaction, Dict]:
    """
    Vender acciones de un determinado valor
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario vendedor
        stock_id: ID de la acción a vender
        quantity: Cantidad de acciones a vender (número positivo)
    
    Returns:
        Tupla con (transacción creada, resumen de la operación)
    """
    if quantity <= 0:
        raise ValueError("La cantidad a vender debe ser un número positivo")
    
    # Verificar que el usuario tiene suficientes acciones
    portfolio = get_user_portfolio(db, user_id) # Recalculate portfolio to ensure latest state
    
    stock_portfolio_data = None
    # The portfolio keys might be stock_id or an object depending on implementation, adjust access
    # Assuming portfolio keys are stock_id as in the provided get_user_portfolio
    if stock_id in portfolio:
        stock_portfolio_data = portfolio[stock_id]

    if not stock_portfolio_data or stock_portfolio_data["shares"] < quantity:
        raise ValueError("No tienes suficientes acciones para vender")
    
    # Obtener stock y precio actual
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise ValueError(f"Acción con ID {stock_id} no encontrada")
    
    # Crear transacción con cantidad negativa para indicar venta
    # Ensure stock.current_price is Decimal
    current_price_decimal = Decimal(str(stock.current_price)) if not isinstance(stock.current_price, Decimal) else stock.current_price
    transaction = create_transaction(db, user_id, stock_id, TransactionType.VENTA, -quantity, current_price_decimal)
    
    # Calcular ganancia/pérdida en esta operación
    avg_buy_price = stock_portfolio_data["average_price"] # This should be Decimal
    profit_loss = (current_price_decimal - avg_buy_price) * Decimal(str(quantity))
    
    # Crear resumen de la operación
    summary = {
        "operation": "venta",
        "stock_symbol": stock.symbol,
        "stock_name": stock.name,
        "quantity": quantity,
        "price_per_share": float(current_price_decimal),
        "total_amount": float(current_price_decimal) * quantity,
        "avg_buy_price": float(avg_buy_price),
        "profit_loss": float(profit_loss),
        "timestamp": transaction.timestamp.isoformat(),
    }
    
    return transaction, summary

def get_transaction_history_with_profit_loss(db: Session, user_id: int, limit: int = 10):
    transactions = db.query(StockTransaction).filter(
        StockTransaction.user_id == user_id
    ).order_by(desc(StockTransaction.timestamp)).limit(limit).all()
    
    result = []
    for trans in transactions:
        stock = db.query(Stock).filter(Stock.id == trans.stock_id).first()
        if stock:
            result.append({
                "id": trans.id,
                "timestamp": trans.timestamp.isoformat(),
                "type": trans.transaction_type.value,
                "quantity": trans.quantity,
                "price": float(trans.price_per_share),
                "stock_symbol": stock.symbol,
                "total": float(trans.quantity * trans.price_per_share)
            })
    return result