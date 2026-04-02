include .env
export

DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env

.PHONY: start db-start db-down db-logs db-connect db-shell

# подключение app
start:
	uv run uvicorn app.main:app --reload --host $(HOST) --port $(PORT)

db-start:
	@echo "Создание контейнера $(DB_CONTAINER)..."
	$(DC) -f $(STORAGES_FILE) $(ENV) up -d --build

db-down:
	@echo "Отключение контейнера $(DB_CONTAINER)..."
	$(DC) -f $(STORAGES_FILE) $(ENV) down

db-logs:
	$(LOGS) -f $(DB_CONTAINER) -f

db-connect:
	@echo "Подключение к БД как $(POSTGRES_USER)..."
	$(EXEC) $(DB_CONTAINER) psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

db-shell:
	$(EXEC) $(DB_CONTAINER) sh
