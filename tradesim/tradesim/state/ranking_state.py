import reflex as rx
from typing import List, Dict, Any
import os
import json
from datetime import datetime

from ..database import SessionLocal
from ..controller.ranking import get_user_ranking, get_user_ranking_by_id, get_top_performing_stocks
from ..state.auth_state import AuthState

class RankingState(AuthState):
    """Estado para la clasificación de usuarios."""
    
    # Datos de clasificación
    top_users: List[Dict] = []
    top_stocks: List[Dict] = []
    user_position: Dict = {}
    ranking_loading: bool = False  # Renamed from loading
    ranking_error_message: str = ""  # Renamed from error_message
    
    @rx.event
    async def load_ranking_data(self):
        """Cargar datos de clasificación y pre-calcular booleanos, incluido is_destacado."""
        self.ranking_loading = True
        self.ranking_error_message = ""

        try:
            db = SessionLocal()
            try:
                # Cargar el top 10 de usuarios
                top_users_raw = get_user_ranking(db, limit=10)
                self.top_users = []
                for i, user in enumerate(top_users_raw):
                    self.top_users.append({
                        **user,
                        "is_roi_positive": user["roi_percentage"] >= 0,
                        "is_profit_positive": user["profit_loss"] >= 0,
                        "is_destacado": i < 3  # True si está en el top 3
                    })

                # Cargar top 5 acciones con mejor rendimiento
                self.top_stocks = get_top_performing_stocks(db, limit=5)

                # Obtener la posición del usuario actual si está autenticado
                if self.is_authenticated:
                    user_id = self._get_user_id()
                    if user_id > 0:
                        user_position_raw = get_user_ranking_by_id(db, user_id)
                        if user_position_raw: # Asegurarse de que no sea None
                            self.user_position = {
                                **user_position_raw,
                                "is_roi_positive": user_position_raw.get("roi_percentage", 0) >= 0,
                                "is_profit_positive": user_position_raw.get("profit_loss", 0) >= 0,
                                # 'is_destacado' no es relevante para la tarjeta de posición del usuario
                            }
                        else:
                            self.user_position = {}
                    else:
                        self.user_position = {}
                else:
                    self.user_position = {}

            finally:
                db.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.ranking_error_message = f"Error al cargar los datos de clasificación: {str(e)}"

        self.ranking_loading = False
    
    def _get_user_id(self) -> int:
        """Obtener el ID del usuario desde el token."""
        try:
            from jose import jwt
            from ..state.auth_state import SECRET_KEY, ALGORITHM
            
            token = str(self.auth_token or "")
            if token:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return int(payload.get("sub", -1))
        except Exception as e:
            print(f"Error obteniendo user_id: {e}")
        return -1