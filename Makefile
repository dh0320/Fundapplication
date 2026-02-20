.PHONY: up down migrate scrape-jgrants scrape-erad scrape-all test-api

up:
	docker compose -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.dev.yml down

migrate:
	docker compose -f docker-compose.dev.yml exec api alembic -c /alembic.ini upgrade head

scrape-jgrants:
	docker compose -f docker-compose.dev.yml run --rm worker python -m workers.scraper.run --source jgrants

scrape-erad:
	docker compose -f docker-compose.dev.yml run --rm worker python -m workers.scraper.run --source erad

scrape-all:
	docker compose -f docker-compose.dev.yml run --rm worker python -m workers.scraper.run --source all

test-api:
	docker compose -f docker-compose.dev.yml exec api pytest tests/ -v
