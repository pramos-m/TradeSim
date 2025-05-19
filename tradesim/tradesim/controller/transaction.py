# # crud/transaction.py
# from sqlmodel import Session, select
# from decimal import Decimal
# from datetime import datetime, timezone
# from ..models.transaction import StockTransaction, TransactionType
# from ..models.stock import Stock
# from ..models.user import User
# from typing import List, Optional, Dict, Tuple # Added Dict, Tuple
# from sqlalchemy import func, desc # Added func, desc

# def get_transaction(db: Session, transaction_id: int):
#     return db.query(StockTransaction).filter(StockTransaction.id == transaction_id).first()

# def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 100):
#     return db.query(StockTransaction).filter(StockTransaction.user_id == user_id).order_by(desc(StockTransaction.timestamp)).offset(skip).limit(limit).all()

# def get_stock_transactions(db: Session, stock_id: int, skip: int = 0, limit: int = 100):
#     return db.query(StockTransaction).filter(StockTransaction.stock_id == stock_id).order_by(desc(StockTransaction.timestamp)).offset(skip).limit(limit).all()

# def create_transaction(db: Session, user_id: int, stock_id: int, transaction_type: TransactionType, quantity: int, price_per_share: Decimal) -> StockTransaction:
#     """Create a new transaction."""
#     transaction = StockTransaction(
#         user_id=user_id,
#         stock_id=stock_id,
#         transaction_type=transaction_type,
#         quantity=quantity,
#         price_per_share=price_per_share
#     )
#     db.add(transaction)
#     db.commit()
#     db.refresh(transaction)
#     return transaction

# def get_user_portfolio(db: Session, user_id: int):
#     # Obtener todas las transacciones del usuario
#     transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).all()
    
#     # Calcular la posición por cada acción
#     portfolio = {}
#     for transaction in transactions:
#         stock_id = transaction.stock_id
#         if stock_id not in portfolio:
#             stock = db.query(Stock).filter(Stock.id == stock_id).first()
#             portfolio[stock_id] = {
#                 "stock": stock,
#                 "shares": 0,
#                 "average_price": Decimal("0.0"),
#                 "total_investment": Decimal("0.0")
#             }
        
#         # Actualizar la posición
#         if transaction.quantity > 0:  # Compra
#             current_shares = portfolio[stock_id]["shares"]
#             current_investment = portfolio[stock_id]["total_investment"]
#             new_shares = current_shares + transaction.quantity
#             new_investment = current_investment + (transaction.price_per_share * Decimal(str(transaction.quantity))) # Ensure Decimal multiplication
            
#             # Recalcular precio promedio
#             if new_shares > 0:
#                 portfolio[stock_id]["average_price"] = new_investment / Decimal(str(new_shares))
            
#             portfolio[stock_id]["shares"] = new_shares
#             portfolio[stock_id]["total_investment"] = new_investment
#         else:  # Venta
#             portfolio[stock_id]["shares"] += transaction.quantity # quantity is negative for sells
    
#     # Filtrar solo posiciones activas (shares > 0)
#     active_positions = {k: v for k, v in portfolio.items() if v["shares"] > 0}
#     return active_positions

# # Nuevas funciones para comprar y vender acciones

# def buy_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[StockTransaction, Dict]:
#     """
#     Comprar acciones de un determinado valor
    
#     Args:
#         db: Sesión de base de datos
#         user_id: ID del usuario comprador
#         stock_id: ID de la acción a comprar
#         quantity: Cantidad de acciones a comprar (número positivo)
    
#     Returns:
#         Tupla con (transacción creada, resumen de la operación)
#     """
#     if quantity <= 0:
#         raise ValueError("La cantidad a comprar debe ser un número positivo")
    
#     # Obtener stock y precio actual
#     stock = db.query(Stock).filter(Stock.id == stock_id).first()
#     if not stock:
#         raise ValueError(f"Acción con ID {stock_id} no encontrada")
    
#     # Realizar la transacción
#     # Ensure stock.current_price is Decimal for create_transaction
#     current_price_decimal = Decimal(str(stock.current_price)) if not isinstance(stock.current_price, Decimal) else stock.current_price
#     transaction = create_transaction(db, user_id, stock_id, TransactionType.COMPRA, quantity, current_price_decimal)
    
#     # Crear resumen de la operación
#     summary = {
#         "operation": "compra",
#         "stock_symbol": stock.symbol,
#         "stock_name": stock.name,
#         "quantity": quantity,
#         "price_per_share": float(current_price_decimal),
#         "total_amount": float(current_price_decimal) * quantity,
#         "timestamp": transaction.timestamp.isoformat(),
#     }
    
#     return transaction, summary

# def sell_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[StockTransaction, Dict]:
#     """
#     Vender acciones de un determinado valor
    
#     Args:
#         db: Sesión de base de datos
#         user_id: ID del usuario vendedor
#         stock_id: ID de la acción a vender
#         quantity: Cantidad de acciones a vender (número positivo)
    
#     Returns:
#         Tupla con (transacción creada, resumen de la operación)
#     """
#     if quantity <= 0:
#         raise ValueError("La cantidad a vender debe ser un número positivo")
    
#     # Verificar que el usuario tiene suficientes acciones
#     portfolio = get_user_portfolio(db, user_id) # Recalculate portfolio to ensure latest state
    
#     stock_portfolio_data = None
#     # The portfolio keys might be stock_id or an object depending on implementation, adjust access
#     # Assuming portfolio keys are stock_id as in the provided get_user_portfolio
#     if stock_id in portfolio:
#         stock_portfolio_data = portfolio[stock_id]

#     if not stock_portfolio_data or stock_portfolio_data["shares"] < quantity:
#         raise ValueError("No tienes suficientes acciones para vender")
    
#     # Obtener stock y precio actual
#     stock = db.query(Stock).filter(Stock.id == stock_id).first()
#     if not stock:
#         raise ValueError(f"Acción con ID {stock_id} no encontrada")
    
#     # Crear transacción con cantidad negativa para indicar venta
#     # Ensure stock.current_price is Decimal
#     current_price_decimal = Decimal(str(stock.current_price)) if not isinstance(stock.current_price, Decimal) else stock.current_price
#     transaction = create_transaction(db, user_id, stock_id, TransactionType.VENTA, -quantity, current_price_decimal)
    
#     # Calcular ganancia/pérdida en esta operación
#     avg_buy_price = stock_portfolio_data["average_price"] # This should be Decimal
#     profit_loss = (current_price_decimal - avg_buy_price) * Decimal(str(quantity))
    
#     # Crear resumen de la operación
#     summary = {
#         "operation": "venta",
#         "stock_symbol": stock.symbol,
#         "stock_name": stock.name,
#         "quantity": quantity,
#         "price_per_share": float(current_price_decimal),
#         "total_amount": float(current_price_decimal) * quantity,
#         "avg_buy_price": float(avg_buy_price),
#         "profit_loss": float(profit_loss),
#         "timestamp": transaction.timestamp.isoformat(),
#     }
    
#     return transaction, summary

# def get_transaction_history_with_profit_loss(db: Session, user_id: int, limit: int = 10):
#     transactions = db.query(StockTransaction).filter(
#         StockTransaction.user_id == user_id
#     ).order_by(desc(StockTransaction.timestamp)).limit(limit).all()
    
#     result = []
#     for trans in transactions:
#         stock = db.query(Stock).filter(Stock.id == trans.stock_id).first()
#         if stock:
#             result.append({
#                 "id": trans.id,
#                 "timestamp": trans.timestamp.isoformat(),
#                 "type": trans.transaction_type.value,
#                 "quantity": trans.quantity,
#                 "price": float(trans.price_per_share),
#                 "stock_symbol": stock.symbol,
#                 "total": float(trans.quantity * trans.price_per_share)
#             })
#     return result
# controller/transaction.py
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime, timezone # Asegúrate que timezone esté importado
from ..models.transaction import StockTransaction, TransactionType
from ..models.stock import Stock
from ..models.user import User # Asegúrate que User esté importado
from typing import List, Optional, Dict, Tuple
from sqlalchemy import func, desc

# ... (get_transaction, get_user_transactions, get_stock_transactions sin cambios) ...

def create_transaction(db: Session, user_id: int, stock_id: int, transaction_type: TransactionType, quantity: int, price_per_share: Decimal) -> StockTransaction:
    """Crea una nueva transacción. La cantidad (quantity) siempre debe ser positiva."""
    if quantity <= 0:
        # Esto no debería pasar si la lógica de buy/sell es correcta, pero es una salvaguarda.
        raise ValueError("La cantidad de la transacción debe ser positiva.")

    transaction = StockTransaction(
        user_id=user_id,
        stock_id=stock_id,
        transaction_type=transaction_type,
        quantity=quantity, # quantity siempre positiva
        price_per_share=price_per_share,
        timestamp=datetime.now(timezone.utc) # Usar timezone.utc si es posible
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_user_portfolio(db: Session, user_id: int) -> Dict[int, Dict]:
    """Obtiene el portfolio actual del usuario calculando desde las transacciones."""
    transactions = db.query(StockTransaction).filter(StockTransaction.user_id == user_id).order_by(StockTransaction.timestamp).all()

    portfolio: Dict[int, Dict] = {} # stock_id -> {stock_info, shares, total_investment, average_price}

    for trans in transactions:
        stock_id = trans.stock_id
        if stock_id not in portfolio:
            stock_db = db.query(Stock).filter(Stock.id == stock_id).first()
            if not stock_db: # Sanity check
                continue 
            portfolio[stock_id] = {
                "stock": stock_db, # Guardar el objeto StockModel entero
                "shares": 0,
                "total_investment_value": Decimal("0.0"), # Costo total de las acciones poseídas
            }

        current_shares = portfolio[stock_id]["shares"]
        current_total_investment = portfolio[stock_id]["total_investment_value"]

        if trans.transaction_type == TransactionType.COMPRA:
            new_shares = current_shares + trans.quantity
            # Sumar al costo total solo si estamos comprando
            new_total_investment = current_total_investment + (trans.price_per_share * Decimal(trans.quantity))
            portfolio[stock_id]["shares"] = new_shares
            portfolio[stock_id]["total_investment_value"] = new_total_investment
        elif trans.transaction_type == TransactionType.VENTA:
            # Reducir el costo total proporcionalmente a las acciones vendidas
            # Asumimos FIFO o un costo promedio para el P/L real, pero para el valor invertido:
            if current_shares > 0: # Evitar división por cero
                cost_per_share_avg = current_total_investment / Decimal(current_shares)
                reduction_in_investment_value = cost_per_share_avg * Decimal(trans.quantity)
                portfolio[stock_id]["total_investment_value"] = max(Decimal("0.0"), current_total_investment - reduction_in_investment_value)
            else: # Si no hay acciones, el valor invertido debería ser 0
                 portfolio[stock_id]["total_investment_value"] = Decimal("0.0")
            portfolio[stock_id]["shares"] = current_shares - trans.quantity


    # Calcular precio promedio y filtrar posiciones vacías
    final_portfolio: Dict[int, Dict] = {}
    for stock_id, pos_data in portfolio.items():
        if pos_data["shares"] > 0:
            pos_data["average_buy_price"] = pos_data["total_investment_value"] / Decimal(pos_data["shares"])
            final_portfolio[stock_id] = pos_data
        elif pos_data["shares"] < 0: # No debería ocurrir si la lógica es correcta
            # Log error o manejar esta inconsistencia
            print(f"ERROR: Shares negativas para stock_id {stock_id} para user_id {user_id}")

    return final_portfolio


def buy_stock(db: Session, user_id: int, stock_id: int, quantity: int) -> Tuple[StockTransaction, Dict]:
    if quantity <= 0:
        raise ValueError("La cantidad a comprar debe ser un número positivo")

    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise ValueError(f"Acción con ID {stock_id} no encontrada")

    current_price_decimal = Decimal(str(stock.current_price)) # Asegurar Decimal

    # Aquí iría la lógica para verificar el saldo del usuario y deducirlo (no presente en el CRUD)
    # user = db.query(User).filter(User.id == user_id).first()
    # total_cost = current_price_decimal * Decimal(quantity)
    # if user.account_balance < total_cost:
    #     raise ValueError("Saldo insuficiente")
    # user.account_balance -= total_cost

    transaction = create_transaction(db, user_id, stock_id, TransactionType.COMPRA, quantity, current_price_decimal)

    summary = {
        "operation": "compra", "stock_symbol": stock.symbol, "stock_name": stock.name,
        "quantity": quantity, "price_per_share": float(current_price_decimal),
        "total_amount": float(current_price_decimal * Decimal(quantity)),
        "timestamp": transaction.timestamp.isoformat(),
    }
    return transaction, summary

def sell_stock(db: Session, user_id: int, stock_id: int, quantity_to_sell: int) -> Tuple[StockTransaction, Dict]:
    if quantity_to_sell <= 0:
        raise ValueError("La cantidad a vender debe ser un número positivo.")

    # Verificar que el usuario tiene suficientes acciones
    current_portfolio = get_user_portfolio(db, user_id)

    stock_in_portfolio = current_portfolio.get(stock_id)

    if not stock_in_portfolio or stock_in_portfolio["shares"] < quantity_to_sell:
        raise ValueError(f"No tienes suficientes acciones ({stock_in_portfolio['shares'] if stock_in_portfolio else 0}) de {stock_id} para vender {quantity_to_sell}.")

    stock_db_info = stock_in_portfolio["stock"] # Obtenemos el objeto Stock desde el portfolio
    current_price_decimal = Decimal(str(stock_db_info.current_price)) # Usar el precio actual del stock

    # Aquí iría la lógica para añadir el valor de la venta al saldo del usuario
    # user = db.query(User).filter(User.id == user_id).first()
    # total_value = current_price_decimal * Decimal(quantity_to_sell)
    # user.account_balance += total_value

    # La cantidad en create_transaction SIEMPRE es positiva.
    transaction = create_transaction(db, user_id, stock_id, TransactionType.VENTA, quantity_to_sell, current_price_decimal)

    avg_buy_price = stock_in_portfolio.get("average_buy_price", Decimal("0.0"))
    profit_loss_per_share = current_price_decimal - avg_buy_price
    total_profit_loss = profit_loss_per_share * Decimal(quantity_to_sell)

    summary = {
        "operation": "venta", "stock_symbol": stock_db_info.symbol, "stock_name": stock_db_info.name,
        "quantity": quantity_to_sell, "price_per_share": float(current_price_decimal),
        "total_amount": float(current_price_decimal * Decimal(quantity_to_sell)),
        "avg_buy_price_at_sale": float(avg_buy_price), # Costo promedio de las acciones que se tenían
        "profit_loss_on_sale": float(total_profit_loss),
        "timestamp": transaction.timestamp.isoformat(),
    }
    return transaction, summary

def get_transaction_history_with_profit_loss(db: Session, user_id: int, limit: int = 10) -> List[Dict]:
    # Esta función es más compleja si quieres P/L por transacción, ya que requiere el costo base en ese momento.
    # Por ahora, la mantenemos simple como la tenías, mostrando los datos de la transacción.
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
                "type": trans.transaction_type.value, # 'compra' o 'venta'
                "quantity": trans.quantity, # Siempre positivo
                "price": float(trans.price_per_share),
                "stock_symbol": stock.symbol,
                "total": float(Decimal(trans.quantity) * trans.price_per_share) # Recalcular por si acaso
            })
    return result