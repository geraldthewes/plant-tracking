# Justfile for plant-tracking-cli

# Install the package in editable mode in the uv environment
install:
	uv pip install -e packages/plant_service
	uv pip install -e .

# Install with test dependencies
install-test:
	uv pip install -e ".[test]"

# Run all tests
test:
	uv run pytest tests/ -v

# Run linter
lint:
	ruff check commands/ tests/

# Format code
format:
	black commands/ tests/

# Check formatting without modifying
format-check:
	black --check commands/ tests/

# Type checking
type-check:
	mypy commands/

# Security scan
security-scan:
	bandit -r commands/ -s B403,B404,B405,B406,B407,B408,B409

# Run all pre-commit checks
check: lint format-check type-check security-scan test

# Local Docker services (Postgres + SeaweedFS)
dev-up:
	docker compose up -d

dev-down:
	docker compose down

dev-setup: dev-up
	@test -f .env || (echo "Create .env manually from .env.local.template first" && exit 1)
	uv run alembic upgrade head

# FastAPI backend service
api-install:
	uv pip install -e backend/fastapi

api-test:
	uv run pytest backend/fastapi/tests/ -v

api-lint:
	ruff check backend/fastapi/src/

api-format:
	black backend/fastapi/src/

api-format-check:
	black --check backend/fastapi/src/

api-type-check:
	mypy backend/fastapi/src/

api-run:
	uv run uvicorn plant_tracking_api.main:app --reload

api-check: api-lint api-format-check api-type-check api-test

# Clean up
clean:
	rm -rf .mypy_cache .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
