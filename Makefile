SHELL=/bin/bash

PORT=8000
FRONT_APP_NAME=instaprint_frontend
BACK_APP_NAME=instaprint_backend

all: stop build local

build: buildfront buildback

buildfront:
	cd frontend_server; uv lock; docker build -t $(FRONT_APP_NAME) --ssh default .

buildback:
	cd print_server; uv lock; docker build -t $(BACK_APP_NAME) --ssh default .

local:
	DUMMY_PRINTER=True docker compose up --remove-orphans print_server

localconnect:
	docker compose up --remove-orphans print_server

run:
	docker compose up -d --remove-orphans

stop:
	docker compose down

start-ssh:
	eval $(ssh-agent -s)

open:
	xdg-open http://127.0.0.1:$(PORT)

dev:
	cd print_server;DUMMY_PRINTER=True uv run fastapi dev ./src/main.py --port $(PORT) --host 127.0.0.1 --reload

lint: check format

check:
	cd print_server; uv tool run ruff check --fix

format:
	cd print_server; uv tool run ruff format
