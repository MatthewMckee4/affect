dev:
	uv sync --all-extras
	uv pip install -e .

test:
	uv run karva test src

pre-commit:
	uv run pre-commit run --all-files

build:
	uv run python -m build

docs:
	uv run zensical build

docs-serve:
	uv run zensical serve

.PHONY: dev test pre-commit build clean docs
