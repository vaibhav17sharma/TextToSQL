.PHONY: help build dev prod clean logs status

help: ## Show this help message
	@echo "Text to SQL - Available Commands:"
	@echo "================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Start development environment
	docker-compose up --build

prod: ## Deploy production environment with Docker
	docker-compose -f docker-compose.prod.yml up --build -d

build: ## Build production images
	docker-compose -f docker-compose.prod.yml build

stop: ## Stop all services
	docker-compose down
	docker-compose -f docker-compose.prod.yml down

clean: ## Clean up containers and images
	docker-compose down -v --rmi all
	docker-compose -f docker-compose.prod.yml down -v --rmi all

logs: ## View logs
	docker-compose -f docker-compose.prod.yml logs -f

status: ## Check service status
	docker-compose -f docker-compose.prod.yml ps

pm2-start: ## Start with PM2
	pm2 start ecosystem.config.js

pm2-stop: ## Stop PM2 services
	pm2 delete ecosystem.config.js

pm2-logs: ## View PM2 logs
	pm2 logs

pm2-status: ## Check PM2 status
	pm2 status

