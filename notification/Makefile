BASE_COMMAND = docker-compose run --rm ${SERVICE_NAME}
COMMAND = ${BASE_COMMAND}  /bin/bash -c
COMPOSE = docker-compose
MANAGE_PY = python3 manage.py

build:
	${COMPOSE} build

start:
	${COMPOSE} start

stop:
	${COMPOSE} stop

up:
	${COMPOSE} up

bash:
	docker-compose run --rm admin /bin/bash

down:
	${COMPOSE} down

superuser:
	docker-compose run --rm admin /bin/bash -c './manage.py createsuperuser'

shell:
	docker-compose run --rm admin /bin/bash -c  './manage.py shell -i python'

migrations:
	docker-compose run --rm admin /bin/bash -c './manage.py makemigrations'

migrate:
	docker-compose run --rm admin /bin/bash -c './manage.py migrate'