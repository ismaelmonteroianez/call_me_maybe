UV_PROJECT_ENVIRONMENT := $(HOME)/sgoinfre/call_me_maybe/.venv
UV_CACHE_DIR := $(HOME)/sgoinfre/uv-cache
HF_HOME := $(HOME)/sgoinfre/huggingface

export UV_PROJECT_ENVIRONMENT
export UV_CACHE_DIR
export HF_HOME

.PHONY: all install run debug clean fclean lint

all: install

install:
	uv sync

run: install
	uv run --no-sync python -m src

debug: install
	uv run --no-sync python -m pdb -m src

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type f -name "*.py[co]" -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache build dist

fclean: clean
	rm -rf "$(UV_PROJECT_ENVIRONMENT)"

lint: install
	uv run --no-sync flake8 .
	uv run --no-sync mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs