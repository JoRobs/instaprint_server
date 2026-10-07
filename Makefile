SHELL=/bin/bash

FRONTEND_APP_NAME=instaprint_frontend
FRONTEND_PORT=8000
BACKEND_APP_NAME=instaprint_backend
BACKEND_PORT=8001

all: stop build local

build: buildfront buildback

buildfront:
	uv lock; docker build -t $(FRONTEND_APP_NAME) -f ./frontend_server/Dockerfile --ssh default .

buildback:
	uv lock; docker build -t $(BACKEND_APP_NAME) -f ./backend_server/Dockerfile --ssh default .

local:
	DUMMY_PRINTER=True docker compose -f docker-compose.yml -f docker-compose.debug.yml up --remove-orphans instaprint_backend instaprint_frontend

localconnect:
	docker compose up --remove-orphans instaprint_backend instaprint_frontend

run:
	docker compose up -d --remove-orphans

stop:
	docker compose down

devback:
	cd backend_server;DUMMY_PRINTER=True uv run fastapi dev ./src/main.py --port $(BACKEND_PORT) --host 127.0.0.1 --reload

devfront:
	cd frontend_server; uv run fastapi dev ./src/main.py --port $(FRONTEND_PORT) --host 127.0.0.1 --reload

lint: check format

check:
	uv tool run ruff check --fix

format:
	uv tool run ruff format
