.PHONY: install up down test lint typecheck eval
install: ; pip install -e ".[dev]"
up: ; docker compose up --build
down: ; docker compose down
test: ; pytest
lint: ; ruff check . && ruff format --check .
typecheck: ; mypy app eval
eval: ; python -m eval.run_eval
