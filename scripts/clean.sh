#!/usr/bin/env bash
# Clean build artifacts and caches

set -e

echo "Cleaning build artifacts and caches..."

# Remove build directories
rm -rf dist/ build/ *.egg-info src/*.egg-info

# Remove cache directories
rm -rf .pytest_cache .mypy_cache .ruff_cache

# Remove __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo "Clean complete!"
