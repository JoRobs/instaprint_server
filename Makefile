SHELL=/bin/bash

PORT=8000
APP_NAME=instaprint

all: stop build run

build:
	docker build print_server -t $(APP_NAME)

run:
	docker compose up --remove-orphans print_server

stop:
	docker compose down

open:
	xdg-open http://127.0.0.1:$(PORT)

dev:
	cd print_server; uv run fastapi dev ./src/main.py --port $(PORT) --host 127.0.0.1 --reload
