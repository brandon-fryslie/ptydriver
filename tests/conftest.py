"""
Pytest configuration for ptydriver tests.
"""

import pytest


def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
