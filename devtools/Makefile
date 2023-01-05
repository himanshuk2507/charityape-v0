all: clean build up logs

build:
	docker build --no-cache -t skraggle-backend ..

# DEPLOY
up:
	docker-compose -f docker-compose.yaml up -d

# DEBUG
logs:
	docker logs -f skraggle-backend

attach:
	docker attach skraggle-backend

shell:
	docker exec -it skraggle-backend bash

up-verbose:
	docker-compose -f docker-compose.yaml --verbose up

# CLEAN
down:
	docker-compose -f docker-compose.yaml down

clean:
	docker stop skraggle-backend
	docker rm skraggle-backend