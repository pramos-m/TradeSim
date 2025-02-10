import reflex as rx

class State(rx.State):
    """Estado global de la aplicación."""
    
    # Ejemplo de variable de estado
    count: int = 0
    
    def increment(self):
        """Incrementa el contador."""
        self.count += 1
    
    def decrement(self):
        """Decrementa el contador."""
        self.count -= 1