# Variables
NETWORK_NAME := mlops_network
API_COMPOSE := compose.yaml

.PHONY: create-req-file
create-req-file: ## Create requirements.txt file
	@uv --version >/dev/null 2>&1
	@uv export --no-dev --no-hashes > requirements.txt
	
.PHONY: create-dev-req-file
create-dev-req-file: ## Create dev requirements.txt file
	@uv --version >/dev/null 2>&1
	@uv export --no-hashes > dev-requirements.txt


# Start all services
.PHONY: start
start: ## Start all services
	docker compose -f $(API_COMPOSE) up -d

# Stop all services
.PHONY: stop
stop: ## Stop all services
	docker compose -f $(API_COMPOSE) down

.PHONY: clean-file
clean-file: ## Remove cached Python files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: format
format: ## Format the project using ruff
	uvx ruff format .

.PHONY: lint	
lint: ## Lint the project using ruff
	uvx ruff check .

# Show logs
.PHONY: logs
logs: ## Show all services logs
	docker compose -f $(API_COMPOSE) logs -f

# Clean everything
.PHONY: clean-everything
clean-everything: stop ## Clean everything
	docker network rm $(NETWORK_NAME) 2>/dev/null || true
	docker volume prune -f

# Create shared network
.PHONY: network
network: ## Create shared network
	docker network create $(NETWORK_NAME) 2>/dev/null || true

# Help command
.PHONY: help
help: ## Display this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Set default goal
.DEFAULT_GOAL := help