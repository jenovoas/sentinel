"""
Unit Tests for Configuration Module

Tests settings instantiation, singleton pattern, and CORS origin parsing.
"""

import os
import pytest
from unittest.mock import patch
from app import config
from app.config import get_settings, get_allowed_origins, Settings

@pytest.fixture
def restore_settings_singleton():
    """Fixture to backup and restore the global _settings singleton."""
    original_settings = config._settings
    yield
    config._settings = original_settings

def test_get_settings_returns_settings_instance(restore_settings_singleton):
    """Verify that get_settings() returns a valid Settings object with default values."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.app_name == "Sentinel"
    assert settings.environment in ("development", "production")

def test_get_settings_singleton_pattern(restore_settings_singleton):
    """Verify that multiple calls to get_settings() return the exact same instance (singleton pattern)."""
    settings_1 = get_settings()
    settings_2 = get_settings()
    assert settings_1 is settings_2

def test_get_settings_recreation_after_reset(restore_settings_singleton):
    """Verify that if the global settings variable is reset to None, get_settings() recreates it."""
    settings_1 = get_settings()

    # Reset singleton to None
    config._settings = None

    settings_2 = get_settings()
    assert settings_1 is not settings_2
    assert isinstance(settings_2, Settings)

def test_get_allowed_origins_default():
    """Verify that get_allowed_origins() returns correct default list when environment variable is not set."""
    # We use patch.dict with clear=True to emulate clean environment.
    with patch.dict(os.environ, {}, clear=True):
        origins = get_allowed_origins()
        assert isinstance(origins, list)
        assert len(origins) == 3
        assert "http://localhost:3000" in origins
        assert "http://localhost:8000" in origins
        assert "http://frontend:3000" in origins

def test_get_allowed_origins_custom():
    """Verify that get_allowed_origins() correctly parses and strips a custom ALLOWED_ORIGINS string."""
    custom_origins = "https://app.secure.com , http://localhost:3000,   https://api.secure.com   "
    with patch.dict(os.environ, {"ALLOWED_ORIGINS": custom_origins}):
        origins = get_allowed_origins()
        assert isinstance(origins, list)
        assert len(origins) == 3
        assert origins == ["https://app.secure.com", "http://localhost:3000", "https://api.secure.com"]
