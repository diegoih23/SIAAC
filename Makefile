.PHONY: help install backend-install frontend-install migrate run frontend docker-up docker-down seed test

help:
	@echo "SIAAC - comandos disponibles"
	@echo "  make install           Instala backend y frontend"
	@echo "  make migrate           Aplica migraciones de Django"
	@echo "  make run               Levanta Django en :8000"
	@echo "  make frontend          Levanta React en :5173"
	@echo "  make docker-up         Levanta MariaDB, Redis, backend y frontend"
	@echo "  make docker-down       Detiene los contenedores"
	@echo "  make seed              Carga datos de ejemplo"
	@echo "  make test              Ejecuta pruebas del backend"

install: backend-install frontend-install

backend-install:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

frontend-install:
	cd frontend && npm install

migrate:
	cd backend && . .venv/bin/activate && python manage.py makemigrations && python manage.py migrate

run:
	cd backend && . .venv/bin/activate && python manage.py runserver 0.0.0.0:8000

frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

seed:
	mysql -u siaac_user -p siaac_db < database/seed.sql

test:
	cd backend && . .venv/bin/activate && pytest
