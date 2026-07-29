"""Pytest configuration and fixtures."""
import pytest

from core.settings import settings


# ============================================================================
# Settings
# ============================================================================

@pytest.fixture
def test_settings(monkeypatch):
    """Override settings for tests."""
    monkeypatch.setattr(settings, "DEBUG", True)
    return settings


# ============================================================================
# Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "e2e: mark test as end-to-end test")
