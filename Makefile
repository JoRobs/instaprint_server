SHELL=/bin/bash

PORT=8000
APP_NAME=instaprint

all: stop build run

build:
	docker build . -t $(APP_NAME)

run:
	docker run --rm -p $(PORT):80 --name $(APP_NAME) $(APP_NAME)

stop:
	if [[ $$(docker ps | grep --count $(APP_NAME)) -gt 0 ]]; then \
		docker stop $(APP_NAME); \
	fi

open:
	xdg-open http://127.0.0.1:$(PORT)