# crud/transaction.py
from sqlalchemy.orm import Session
from ..models.transaction import Transaction
from ..models.user import User
from ..models.stock import Stock
from decimal import Decimal
from typing import List, Optional, Dict, Tuple # Added Dict, Tuple
from datetime import datetime
from sqlalchemy import func, desc # Added func, desc

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
            new_investment = current_investment + (transaction.price * Decimal(str(transaction.quantity))) # Ensure Decimal multiplication
            
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
    # Ensure stock.current_price is Decimal for create_transaction
    current_price_decimal = Decimal(str(stock.current_price)) if not isinstance(stock.current_price, Decimal) else stock.current_price
    transaction = create_transaction(db, user_id, stock_id, quantity, current_price_decimal)
    
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
    transaction = create_transaction(db, user_id, stock_id, -quantity, current_price_decimal)
    
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
    # Obtener transacciones ordenadas por fecha para el resultado final (más recientes primero)
    transactions_for_display = db.query(Transaction).join(Stock).filter(
        Transaction.user_id == user_id
    ).order_by(desc(Transaction.timestamp)).limit(limit).all()
    
    # Para calcular ganancias/pérdidas necesitamos precios de compra promedio.
    # Este cálculo se hace procesando TODAS las transacciones del usuario en orden cronológico.
    all_user_transactions_chronological = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).order_by(Transaction.timestamp).all()
    
    # Diccionarios para rastrear el estado del portafolio para cálculo de P/L
    # stock_id -> average_buy_price
    avg_buy_prices_at_sale_time: Dict[int, Decimal] = {}
    # stock_id -> current_total_shares
    current_shares_for_avg_calc: Dict[int, int] = {}
    # stock_id -> current_total_investment_cost
    current_investment_for_avg_calc: Dict[int, Decimal] = {}

    # Pre-calcular los precios promedio de compra históricos para cada venta
    # Este es un paso complejo: para cada venta, necesitamos saber cuál era el precio promedio de compra
    # de las acciones vendidas EN ESE MOMENTO.
    # Una forma simplificada es mantener un precio promedio ponderado (FIFO/LIFO no implementado aquí)
    
    # Primero, construir el estado del portafolio (avg_price) hasta cada transacción de venta
    # Este es un enfoque simplificado que usa el precio promedio general hasta el punto de la venta.
    # Para una contabilidad precisa de lotes específicos, se necesitaría un seguimiento más detallado.
    
    # Calcular el precio promedio de compra para cada acción a lo largo del tiempo
    # Este diccionario almacenará el precio promedio de compra de un stock en el momento de una venta específica (transaction.id)
    historical_avg_buy_price_for_sales: Dict[int, Decimal] = {}

    temp_portfolio_state: Dict[int, Dict[str, Decimal | int]] = {}

    for tx_chronological in all_user_transactions_chronological:
        stock_id = tx_chronological.stock_id
        tx_price = Decimal(str(tx_chronological.price))
        tx_quantity = tx_chronological.quantity

        if stock_id not in temp_portfolio_state:
            temp_portfolio_state[stock_id] = {"shares": 0, "total_cost": Decimal("0.0"), "avg_price": Decimal("0.0")}

        current_stock_state = temp_portfolio_state[stock_id]

        if tx_quantity > 0: # Compra
            new_total_cost = current_stock_state["total_cost"] + (tx_price * Decimal(tx_quantity))
            new_shares = current_stock_state["shares"] + tx_quantity
            current_stock_state["total_cost"] = new_total_cost
            current_stock_state["shares"] = new_shares
            if new_shares > 0:
                current_stock_state["avg_price"] = new_total_cost / Decimal(new_shares)
        elif tx_quantity < 0: # Venta
            # Guardar el precio promedio de compra en el momento de esta venta
            historical_avg_buy_price_for_sales[tx_chronological.id] = current_stock_state["avg_price"]
            # Actualizar acciones, el costo y precio promedio no cambian por una venta (para futuras compras)
            current_stock_state["shares"] += tx_quantity # tx_quantity es negativo
            # Opcional: Reducir el costo total proporcionalmente si se desea rastrear el costo base restante
            # current_stock_state["total_cost"] -= current_stock_state["avg_price"] * Decimal(abs(tx_quantity))


    # Procesar las transacciones para el resultado (las 'limit' más recientes)
    result = []
    for tx_display in transactions_for_display:
        # La unión ya debería haber cargado el stock, pero por si acaso o si se cambia la query:
        stock = tx_display.stock if tx_display.stock else db.query(Stock).filter(Stock.id == tx_display.stock_id).first()
        
        transaction_data = {
            "id": tx_display.id,
            "stock_symbol": stock.symbol if stock else "N/A",
            "stock_name": stock.name if stock else "Desconocido",
            "quantity": abs(tx_display.quantity),
            "price": float(tx_display.price),
            "timestamp": tx_display.timestamp.isoformat(),
            "type": "compra" if tx_display.quantity > 0 else "venta",
            "total_amount": float(tx_display.price) * abs(tx_display.quantity)
        }
        
        # Si es venta, calcular ganancia/pérdida usando el precio promedio histórico
        if tx_display.quantity < 0:
            avg_price_at_sale = historical_avg_buy_price_for_sales.get(tx_display.id, Decimal("0.0"))
            
            profit_loss = (Decimal(str(tx_display.price)) - avg_price_at_sale) * Decimal(abs(tx_display.quantity))
            profit_loss_percentage = Decimal("0.0")
            if avg_price_at_sale > 0 and (avg_price_at_sale * Decimal(abs(tx_display.quantity))) != 0: # Evitar división por cero
                cost_basis_of_sale = avg_price_at_sale * Decimal(abs(tx_display.quantity))
                profit_loss_percentage = (profit_loss / cost_basis_of_sale) * Decimal("100.0")
            
            transaction_data["avg_buy_price"] = float(avg_price_at_sale)
            transaction_data["profit_loss"] = float(profit_loss)
            transaction_data["profit_loss_percentage"] = float(profit_loss_percentage)
        
        result.append(transaction_data)
    
    return result