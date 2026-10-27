PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: setup test lint run

setup:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/pip install -e '.[dev]'

test:
	$(BIN)/pytest -q

lint:
	$(BIN)/ruff check src tests

run:
	$(BIN)/uvicorn code_agent_boilerplate.api:app --reload
