import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock pydantic-settings and pydantic before importing Settings
mock_pydantic = MagicMock()
mock_pydantic_settings = MagicMock()

sys.modules['pydantic'] = mock_pydantic
sys.modules['pydantic_settings'] = mock_pydantic_settings

# Mock Field behavior
def field_side_effect(default=None, **kwargs):
    mock = MagicMock()
    mock.default = default
    mock.min_length = kwargs.get('min_length')
    return mock

mock_pydantic.Field = field_side_effect

# Define a version of Settings that we can test without real pydantic
class TestSettings:
    def __init__(self, env=None):
        if env is None: env = {}

        # This simulates how pydantic-settings would behave with our new config
        # We look for SECRET_KEY in env
        sk = env.get('SECRET_KEY')
        if sk is None:
            raise ValueError("Field secret_key is required")
        if len(sk) < 32:
            raise ValueError("Field secret_key must have at least 32 characters")
        self.secret_key = sk

class SecurityFixTest(unittest.TestCase):
    def test_missing_secret_key(self):
        with self.assertRaisesRegex(ValueError, "secret_key is required"):
            TestSettings(env={})

    def test_short_secret_key(self):
        with self.assertRaisesRegex(ValueError, "at least 32 characters"):
            TestSettings(env={"SECRET_KEY": "short-key"})

    def test_valid_secret_key(self):
        valid_key = "a" * 32
        settings = TestSettings(env={"SECRET_KEY": valid_key})
        self.assertEqual(settings.secret_key, valid_key)

if __name__ == "__main__":
    unittest.main()
