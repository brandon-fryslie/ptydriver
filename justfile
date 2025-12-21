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
    uv run twine upload dist/*

# Lint and format check
lint:
    uv run ruff check src/ tests/
    uv run ruff format --check src/ tests/

# Generate changelog
changelog:
    git cliff -o CHANGELOG.md

# Generate changelog for unreleased changes
changelog-unreleased:
    git cliff --unreleased
