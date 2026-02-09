# tests/test_observability.py
# ----------------------------
# I test the observability logging helpers.

import pytest
from unittest.mock import patch, call


class TestQueryLogging:
    """Tests for query logging helpers."""
    
    def test_log_query_start(self):
        """Should log query start details."""
        from bashcloud.utils.logger import log_query_start
        
        with patch("bashcloud.utils.logger.debug") as mock_debug:
            log_query_start("aws", "2024-01-01", "2024-02-01")
        
        mock_debug.assert_called_once()
        call_arg = mock_debug.call_args[0][0]
        assert "aws" in call_arg
        assert "2024-01-01" in call_arg
        assert "2024-02-01" in call_arg
    
    def test_log_query_complete_api_call(self):
        """Should log query completion as API call."""
        from bashcloud.utils.logger import log_query_complete
        
        with patch("bashcloud.utils.logger.debug") as mock_debug:
            log_query_complete(
                duration_seconds=1.5,
                page_count=3,
                record_count=42,
                cache_hit=False,
            )
        
        mock_debug.assert_called_once()
        call_arg = mock_debug.call_args[0][0]
        assert "1.5" in call_arg or "1.50" in call_arg
        assert "3" in call_arg
        assert "42" in call_arg
        assert "API call" in call_arg
    
    def test_log_query_complete_cache_hit(self):
        """Should log query completion as cache hit."""
        from bashcloud.utils.logger import log_query_complete
        
        with patch("bashcloud.utils.logger.debug") as mock_debug:
            log_query_complete(
                duration_seconds=0.01,
                page_count=0,
                record_count=10,
                cache_hit=True,
            )
        
        mock_debug.assert_called_once()
        call_arg = mock_debug.call_args[0][0]
        assert "cache hit" in call_arg


class TestThresholdLogging:
    """Tests for threshold logging."""
    
    def test_log_threshold_applied(self):
        """Should log threshold filtering info."""
        from bashcloud.utils.logger import log_threshold_applied
        
        with patch("bashcloud.utils.logger.debug") as mock_debug:
            log_threshold_applied(threshold=1.0, before_count=100, after_count=25)
        
        mock_debug.assert_called_once()
        call_arg = mock_debug.call_args[0][0]
        assert "1.0" in call_arg
        assert "75" in call_arg  # filtered count


class TestCacheLogging:
    """Tests for cache status logging."""
    
    def test_log_cache_hit(self):
        """Should log cache hit."""
        from bashcloud.utils.logger import log_cache_status
        
        with patch("bashcloud.utils.logger.debug") as mock_debug:
            log_cache_status("test_key", hit=True)
        
        mock_debug.assert_called_once()
        call_arg = mock_debug.call_args[0][0]
        assert "hit" in call_arg
        assert "test_key" in call_arg
    
    def test_log_cache_miss(self):
        """Should log cache miss."""
        from bashcloud.utils.logger import log_cache_status
        
        with patch("bashcloud.utils.logger.debug") as mock_debug:
            log_cache_status("test_key", hit=False)
        
        mock_debug.assert_called_once()
        call_arg = mock_debug.call_args[0][0]
        assert "miss" in call_arg
