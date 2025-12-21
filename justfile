# ptydriver justfile

# Run tests
test:
    uv run pytest tests/ -v

# Build package
build:
    uv build

# Clean build artifacts
clean:
    ./scripts/clean.sh

# Release to PyPI
release: clean build
    uv publish

# Lint and format check
lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/
