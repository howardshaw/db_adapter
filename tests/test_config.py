import os
from unittest.mock import patch

import pytest

from config import get_settings, Settings


class TestSettings:
    """Test cases for Settings configuration."""

    def test_settings_defaults(self):
        """Test Settings with default values."""
        settings = Settings()

        assert settings.USE_ASYNC_DB is True
        assert settings.REPO_DRIVER == "async_db"
        assert settings.USE_ASYNC_ROUTER is True
        assert settings.DB_URL_SYNC == "sqlite:///./example.db"
        assert settings.DB_URL_ASYNC == "sqlite+aiosqlite:///./example.db"
        assert settings.ECHO is False
        assert settings.POOL_SIZE == 20
        assert settings.MAX_OVERFLOW == 10
        assert settings.POOL_RECYCLE == 10
        assert settings.POOL_TIMEOUT == 5

    def test_settings_from_environment(self):
        """Test Settings with environment variables."""
        with patch.dict(os.environ, {
            "USE_ASYNC_DB": "false",
            "REPO_DRIVER": "sync_db",
            "USE_ASYNC_ROUTER": "false",
            "DB_URL_SYNC": "sqlite:///test.db",
            "DB_URL_ASYNC": "sqlite+aiosqlite:///test.db",
            "ECHO": "true",
            "POOL_SIZE": "10",
            "MAX_OVERFLOW": "5",
            "POOL_RECYCLE": "3600",
            "POOL_TIMEOUT": "10"
        }):
            settings = Settings()

            assert settings.USE_ASYNC_DB is False
            assert settings.REPO_DRIVER == "sync_db"
            assert settings.USE_ASYNC_ROUTER is False
            assert settings.DB_URL_SYNC == "sqlite:///test.db"
            assert settings.DB_URL_ASYNC == "sqlite+aiosqlite:///test.db"
            assert settings.ECHO is True
            assert settings.POOL_SIZE == 10
            assert settings.MAX_OVERFLOW == 5
            assert settings.POOL_RECYCLE == 3600
            assert settings.POOL_TIMEOUT == 10

    def test_settings_validation(self):
        """Test Settings validation."""
        # Test valid pool size
        settings = Settings(POOL_SIZE=1)
        assert settings.POOL_SIZE == 1

        # Test invalid pool size (should raise validation error)
        with pytest.raises(ValueError):
            Settings(POOL_SIZE=0)

        # Test valid max overflow
        settings = Settings(MAX_OVERFLOW=0)
        assert settings.MAX_OVERFLOW == 0

        # Test invalid max overflow (should raise validation error)
        with pytest.raises(ValueError):
            Settings(MAX_OVERFLOW=-1)

    def test_settings_model_dump(self):
        """Test Settings model_dump method."""
        settings = Settings()
        settings_dict = settings.model_dump()

        assert "USE_ASYNC_DB" in settings_dict
        assert "REPO_DRIVER" in settings_dict
        assert "USE_ASYNC_ROUTER" in settings_dict
        assert "DB_URL_SYNC" in settings_dict
        assert "DB_URL_ASYNC" in settings_dict
        assert "ECHO" in settings_dict
        assert "POOL_SIZE" in settings_dict
        assert "MAX_OVERFLOW" in settings_dict
        assert "POOL_RECYCLE" in settings_dict
        assert "POOL_TIMEOUT" in settings_dict

    def test_settings_repr(self):
        """Test Settings string representation."""
        settings = Settings()
        repr_str = repr(settings)

        assert "Settings" in repr_str
        assert "USE_ASYNC_DB" in repr_str
        assert "REPO_DRIVER" in repr_str


class TestGetSettings:
    """Test cases for get_settings function."""

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_get_settings_with_environment(self):
        """Test get_settings with environment variables."""
        with patch.dict(os.environ, {
            "USE_ASYNC_DB": "false",
            "REPO_DRIVER": "sync_db"
        }):
            settings = get_settings()

            assert settings.USE_ASYNC_DB is False
            assert settings.REPO_DRIVER == "sync_db"

    @patch('config.logging.getLogger')
    def test_get_settings_logging(self, mock_get_logger):
        """Test that get_settings logs configuration."""
        mock_logger = mock_get_logger.return_value

        # Clear the cache to force a new settings instance
        get_settings.cache_clear()

        get_settings()

        # Verify that logging was called
        assert mock_logger.info.call_count >= 1

    def test_get_settings_error_handling(self):
        """Test get_settings error handling."""
        with patch('config.Settings') as mock_settings:
            mock_settings.side_effect = Exception("Configuration error")

            with pytest.raises(Exception, match="Configuration error"):
                get_settings.cache_clear()
                get_settings()


class TestSettingsIntegration:
    """Integration tests for Settings."""

    def test_settings_with_real_environment(self):
        """Test Settings with real environment variables."""
        # Save original environment
        original_env = os.environ.copy()

        try:
            # Set test environment variables
            os.environ.update({
                "USE_ASYNC_DB": "false",
                "REPO_DRIVER": "uniform_sync_db",
                "USE_ASYNC_ROUTER": "false",
                "DB_URL_SYNC": "sqlite:///integration_test.db",
                "DB_URL_ASYNC": "sqlite+aiosqlite:///integration_test.db",
                "ECHO": "true",
                "POOL_SIZE": "5",
                "MAX_OVERFLOW": "2",
                "POOL_RECYCLE": "1800",
                "POOL_TIMEOUT": "5"
            })

            # Clear cache to force new settings
            get_settings.cache_clear()

            settings = get_settings()

            assert settings.USE_ASYNC_DB is False
            assert settings.REPO_DRIVER == "uniform_sync_db"
            assert settings.USE_ASYNC_ROUTER is False
            assert settings.DB_URL_SYNC == "sqlite:///integration_test.db"
            assert settings.DB_URL_ASYNC == "sqlite+aiosqlite:///integration_test.db"
            assert settings.ECHO is True
            assert settings.POOL_SIZE == 5
            assert settings.MAX_OVERFLOW == 2
            assert settings.POOL_RECYCLE == 1800
            assert settings.POOL_TIMEOUT == 5

        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
            get_settings.cache_clear()
