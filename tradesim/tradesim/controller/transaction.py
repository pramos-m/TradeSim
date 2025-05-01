# crud/transaction.py
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.stock import Stock
from decimal import Decimal
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from sqlalchemy import func, desc

def get_transaction(db: Session, transaction_id: int):
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()

def get_stock_transactions(db: Session, stock_id: int, skip: int = 0, limit: int = 100):
    return db.query(Transaction).filter(Transaction.stock_id == stock_id).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()

def create_transaction(db: Session, user_id: int, stock_id: int, quantity: int, price: Decimal):
    # Verificar que el usuario existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"Usuario con id {user_id} no encontrado")
        
    # Verificar que la acción existe
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise ValueError(f"Acción con id {stock_id} no encontrada")
    
    # Calcular el monto total de la transacción
    total_amount = price * abs(quantity)
    
    # Si es una compra, verificar que el usuario tiene saldo suficiente
    if quantity > 0 and user.account_balance < total_amount:
        raise ValueError("Saldo insuficiente para realizar la compra")
    
    # Ejecutar la transacción
    db_transaction = Transaction(
        user_id=user_id,
        stock_id=stock_id,
        quantity=quantity,
        price=price,
        timestamp=datetime.utcnow()
    )
    
    # Actualizar el saldo del usuario
    if quantity > 0:  # Compra
        user.account_balance -= total_amount
    else:  # Venta
        user.account_balance += total_amount
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_user_portfolio(db: Session, user_id: int):
    # Obtener todas las transacciones del usuario
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    
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
            new_investment = current_investment + (transaction.price * transaction.quantity)
            
            # Recalcular precio promedio
            if new_shares > 0:
                portfolio[stock_id]["average_price"] = new_investment / new_shares
            
            portfolio[stock_id]["shares"] = new_shares
            portfolio[stock_id]["total_investment"] = new_investment
        else:  # Venta
            portfolio[stock_id]["shares"] += transaction.quantity
    
    # Filtrar solo posiciones activas (shares > 0)
    active_positions = {k: v for k, v in portfolio.items() if v["shares"] > 0}
    return active_positions

# Nuevas funciones para comprar y vender acciones

def buy_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[Transaction, Dict]:
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
    transaction = create_transaction(db, user_id, stock_id, quantity, stock.current_price)
    
    # Crear resumen de la operación
    summary = {
        "operation": "compra",
        "stock_symbol": stock.symbol,
        "stock_name": stock.name,
        "quantity": quantity,
        "price_per_share": float(stock.current_price),
        "total_amount": float(stock.current_price) * quantity,
        "timestamp": transaction.timestamp.isoformat(),
    }
    
    return transaction, summary

def sell_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[Transaction, Dict]:
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
    portfolio = get_user_portfolio(db, user_id)
    if stock_id not in portfolio or portfolio[stock_id]["shares"] < quantity:
        raise ValueError("No tienes suficientes acciones para vender")
    
    # Obtener stock y precio actual
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise ValueError(f"Acción con ID {stock_id} no encontrada")
    
    # Crear transacción con cantidad negativa para indicar venta
    transaction = create_transaction(db, user_id, stock_id, -quantity, stock.current_price)
    
    # Calcular ganancia/pérdida en esta operación
    avg_buy_price = portfolio[stock_id]["average_price"]
    profit_loss = (stock.current_price - avg_buy_price) * quantity
    
    # Crear resumen de la operación
    summary = {
        "operation": "venta",
        "stock_symbol": stock.symbol,
        "stock_name": stock.name,
        "quantity": quantity,
        "price_per_share": float(stock.current_price),
        "total_amount": float(stock.current_price) * quantity,
        "avg_buy_price": float(avg_buy_price),
        "profit_loss": float(profit_loss),
        "timestamp": transaction.timestamp.isoformat(),
    }
    
    return transaction, summary

def get_transaction_history_with_profit_loss(db: Session, user_id: int, limit: int = 50) -> List[Dict]:
    """
    Obtener historial de transacciones con cálculo de ganancia/pérdida para cada venta
    
    Args:
        db: Sesión de base de datos
        user_id: ID del usuario
        limit: Número máximo de transacciones a retornar
    
    Returns:
        Lista de transacciones con detalles adicionales
    """
    # Obtener transacciones ordenadas por fecha
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(desc(Transaction.timestamp)).limit(limit).all()
    
    # Para calcular ganancias/pérdidas necesitamos precios de compra promedio
    # Este diccionario llevará el registro de los precios de compra por acción
    avg_buy_prices = {}
    total_shares = {}
    total_investment = {}
    
    # Primero calculamos los precios promedio de compra para cada acción
    # Ordenamos de más antiguas a más recientes para el cálculo
    all_transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.timestamp).all()
    
    for tx in all_transactions:
        stock_id = tx.stock_id
        
        # Inicializar si es la primera transacción para este stock
        if stock_id not in avg_buy_prices:
            avg_buy_prices[stock_id] = 0
            total_shares[stock_id] = 0
            total_investment[stock_id] = 0
        
        if tx.quantity > 0:  # Compra
            # Actualizar total de acciones y monto invertido
            total_investment[stock_id] += float(tx.price) * tx.quantity
            total_shares[stock_id] += tx.quantity
            
            # Recalcular precio promedio
            if total_shares[stock_id] > 0:
                avg_buy_prices[stock_id] = total_investment[stock_id] / total_shares[stock_id]
        else:  # Venta
            # Solo actualizamos las acciones disponibles, el precio promedio no cambia
            total_shares[stock_id] += tx.quantity
    
    # Procesar las transacciones para el resultado
    result = []
    for tx in transactions:
        stock = db.query(Stock).filter(Stock.id == tx.stock_id).first()
        
        transaction_data = {
            "id": tx.id,
            "stock_symbol": stock.symbol,
            "stock_name": stock.name,
            "quantity": abs(tx.quantity),
            "price": float(tx.price),
            "timestamp": tx.timestamp.isoformat(),
            "type": "compra" if tx.quantity > 0 else "venta",
            "total_amount": float(tx.price) * abs(tx.quantity)
        }
        
        # Si es venta, calcular ganancia/pérdida
        if tx.quantity < 0:
            avg_price = avg_buy_prices.get(tx.stock_id, 0)
            profit_loss = (float(tx.price) - avg_price) * abs(tx.quantity)
            profit_loss_percentage = 0
            if avg_price > 0:
                profit_loss_percentage = (profit_loss / (avg_price * abs(tx.quantity))) * 100
            
            transaction_data["avg_buy_price"] = avg_price
            transaction_data["profit_loss"] = profit_loss
            transaction_data["profit_loss_percentage"] = profit_loss_percentage
        
        result.append(transaction_data)
    
    return result