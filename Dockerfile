# Dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y curl unzip && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/data && chmod 777 /app/data
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG CACHEBUST=1

# --- CORRECCIÓN AQUÍ: Comentario en línea separada ---
# Copia el código de la aplicación
COPY . .
# ----------------------------------------------------

EXPOSE 3000
EXPOSE 8000
ENV DATABASE_URL=sqlite:////app/data/tradesim.db
ENV PYTHONUNBUFFERED=1
CMD ["reflex", "run", "--env", "prod", "--backend-port", "8000", "--frontend-port", "3000"]