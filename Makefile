help:
	more README.md

build:
	docker-compose build

rebuild:
	docker-compose build --no-cache

network:
	@docker network create ai-dev-network 2>/dev/null || true

up: network
	docker-compose up -d mongodb
	@sleep 3
	docker-compose exec mongodb sh -c '/mnt/migration.sh -d ujcatapi_dev'
	docker-compose up

down:
	docker-compose down

rm:
	docker-compose rm -sfv
	docker volume rm ujcatapi_db_data

migrate: network
	docker-compose up -d mongodb
	@sleep 3
	docker-compose exec mongodb sh -c '/mnt/migration.sh -d ujcatapi_dev'

delete_collections:
	-echo 'db.getCollectionNames().forEach(function(element) {db[element].drop();});' \
	| docker-compose exec -T mongodb mongo ujcatapi_dev

bash: network
	docker-compose run --rm api bash

bash-mongodb: network
	docker-compose run --rm mongodb bash

test: network
	docker-compose up -d mongodb
	@sleep 3
	docker-compose exec mongodb sh -c '/mnt/migration.sh -d ujcatapi_test'
	docker-compose run -e MONGODB_URL=mongodb://mongodb:27017/ujcatapi_test --rm api ./tasks.sh

ci: network
	docker-compose up -d mongodb
	@sleep 3
	docker-compose exec -T mongodb sh -c '/mnt/migration.sh -d ujcatapi_test'
	docker-compose run -T -e MONGODB_URL=mongodb://mongodb:27017/ujcatapi_test --rm api ./tasks.sh

tdd: network
	docker-compose up -d mongodb
	@sleep 3
	docker-compose exec mongodb sh -c '/mnt/migration.sh -d ujcatapi_test'
	docker-compose run -e MONGODB_URL=mongodb://mongodb:27017/ujcatapi_test --rm api poetry run ptw -p .

test-unit: network
	docker-compose up -d mongodb
	@sleep 3
	docker-compose exec mongodb sh -c '/mnt/migration.sh -d ujcatapi_test'
	docker-compose run -e MONGODB_URL=mongodb://mongodb:27017/ujcatapi_test --rm api ./tasks.sh -u

test-type: network
	docker-compose run --rm api ./tasks.sh -t

test-style: network
	docker-compose run --rm api ./tasks.sh -s

test-format: network
	docker-compose run --rm api ./tasks.sh -f

test-coverage: network
	docker-compose run --rm api ./tasks.sh -c

format: network
	docker-compose run --rm api ./tasks.sh -fx

.PHONY: build rebuild network up down migrate delete_collections bash bash-mongodb test test-unit test-type test-style test-format format
