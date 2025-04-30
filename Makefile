IMAGE_NAME=dashboard-web # <-- Define el nombre de la imagen (ajusta si Docker la llama diferente)

# Variables
COMPOSE = docker-compose.yaml
COMPOSE_CMD = docker compose -f ${COMPOSE}

# Targets principales
all: build up

build:
	# Construye forzando --no-cache y pasando CACHEBUST
	$(COMPOSE_CMD) build --no-cache --build-arg CACHEBUST=$(date +%s)

up:
	$(COMPOSE_CMD) up --detach

stop:
	# Detiene contenedores solo si existen
	@if [ -n "$$($(COMPOSE_CMD) ps -q)" ]; then \
		$(COMPOSE_CMD) stop; \
	fi

down: stop
	$(COMPOSE_CMD) down

ps:
	$(COMPOSE_CMD) ps

clean: down
	# Limpieza más agresiva (opcional)
	@echo "Ejecutando limpieza agresiva (contenedores, imágenes no usadas, volúmenes no usados)..."
	docker container prune -f || true
	docker image prune -a -f || true
	docker volume prune -f || true
	docker network prune -f || true
	@echo "Limpieza agresiva completada."

fclean:
	# Detiene contenedores y ELIMINA VOLÚMENES (-v)
	$(COMPOSE_CMD) down -v
	# Elimina la imagen específica de la aplicación
	@echo "Intentando eliminar imagen $(IMAGE_NAME)..."
	docker rmi $(IMAGE_NAME) 2>/dev/null || echo "Imagen $(IMAGE_NAME) no encontrada o no se pudo eliminar."

logs:
	$(COMPOSE_CMD) logs -f

re: fclean all

.PHONY: all build up stop down ps clean fclean logs re