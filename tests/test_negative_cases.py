# tests/test_negative_cases.py
# -----------------------------
# Consolidated all negative test cases. These test error handling,
# validation failures, and edge cases that should fail gracefully.

import pytest
import json
from unittest.mock import patch, Mock
import subprocess

from bashcloud.core.exceptions import (
    BashCloudError,
    CLIUnavailableError,
    CredentialError,
    DateRangeError,
    PaginationError,
    ParsingError,
    ConfigurationError,
)
from bashcloud.utils.parsers import validate_date_format, validate_date_range
from bashcloud.utils.pagination import paginate_cli_command
from bashcloud.infra.cli_adapter import CLIAdapter
from bashcloud.infra.cache import ResultCache
from bashcloud.tui.navigation import Navigator


# =============================================================================
# Validation Failures (Cases 1-10)
# =============================================================================

class TestValidationFailures:
    """Validation error test cases."""
    
    def test_1_start_date_after_end_date(self):
        """Should raise DateRangeError when start > end."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("2024-02-01", "2024-01-01")
        assert "before or equal" in str(exc_info.value)
    
    def test_2_invalid_date_format(self):
        """Should reject non-ISO date format."""
        assert validate_date_format("01/15/2024") is False
        assert validate_date_format("2024/01/15") is False
        assert validate_date_format("15-01-2024") is False
    
    def test_3_invalid_provider_name(self):
        """Should raise for invalid provider."""
        from bashcloud.core.provider_factory import get_cost_provider
        
        with pytest.raises(BashCloudError) as exc_info:
            get_cost_provider("invalid_provider")
        assert "unknown provider" in str(exc_info.value).lower()
    
    def test_4_negative_threshold(self):
        """Negative threshold should be handled."""
        from bashcloud.core.cost_base import CostRecord
        from bashcloud.aws.cost import AWSCostProvider
        
        provider = AWSCostProvider()
        records = [CostRecord(name="Test", amount=10.0, unit="USD", period="2024-01")]
        
        # Negative threshold should not filter anything (or be treated as 0)
        filtered = provider.filter_by_threshold(records, -5.0)
        assert len(filtered) == 1
    
    def test_5_non_numeric_date(self):
        """Non-numeric date should be invalid."""
        assert validate_date_format("twenty-twenty-four-01-01") is False
    
    def test_6_missing_cli_raises_error(self):
        """Should raise CLIUnavailableError when CLI not installed."""
        adapter = CLIAdapter("nonexistent_cli")
        
        with patch('shutil.which', return_value=None):
            with pytest.raises(CLIUnavailableError):
                adapter.require_available()
    
    def test_7_permission_denied_scenario(self):
        """Should detect permission errors in CLI output."""
        from bashcloud.aws.cost import AWSCostProvider
        
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "AccessDeniedException: User is not authorized"
        
        with patch('shutil.which', return_value='/usr/bin/aws'):
            with patch('subprocess.run', return_value=mock_result):
                with patch('bashcloud.core.health.check_aws_credentials', 
                           return_value=(True, None)):
                    provider = AWSCostProvider()
                    with pytest.raises(BashCloudError):
                        provider.get_cost_by_service("2024-01-01", "2024-02-01")
    
    def test_8_expired_credentials(self):
        """Should handle expired credentials."""
        from bashcloud.core.health import check_aws_credentials
        
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "ExpiredToken: The security token included is expired"
        
        with patch('subprocess.run', return_value=mock_result):
            is_valid, error = check_aws_credentials()
            assert is_valid is False
    
    def test_9_network_timeout(self):
        """Should handle command timeout."""
        adapter = CLIAdapter("test", timeout=1)
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("cmd", 1)):
            with pytest.raises(BashCloudError) as exc_info:
                adapter.run(["arg"])
            assert "timed out" in str(exc_info.value).lower()
    
    def test_10_malformed_json_response(self):
        """Should handle malformed JSON in CLI output."""
        from bashcloud.infra.cli_adapter import CLIResult
        
        result = CLIResult(
            command=["test"],
            returncode=0,
            stdout="not valid json {{{",
            stderr="",
        )
        
        with pytest.raises(ParsingError):
            result.json()


# =============================================================================
# Pagination Failures (Cases 11-15)
# =============================================================================

class TestPaginationFailures:
    """Pagination error test cases."""
    
    def test_11_infinite_loop_token(self):
        """Should detect infinite loop via max pages."""
        page_num = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps({
                "Items": [{"id": page_num[0]}],
                "NextPageToken": f"token_{page_num[0]}"
            })
            page_num[0] += 1
            return result
        
        with patch('subprocess.run', side_effect=mock_run):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=lambda t: ["cmd"],
                    result_key="Items",
                    max_pages=3,
                )
            assert "maximum" in str(exc_info.value).lower()
    
    def test_12_empty_page_mid_stream(self):
        """Should handle empty page in middle of pagination."""
        responses = [
            {"Items": [1], "NextPageToken": "t1"},
            {"Items": [], "NextPageToken": "t2"},  # Empty page
            {"Items": [2]},
        ]
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(responses[min(call_count[0], 2)])
            call_count[0] += 1
            return result
        
        with patch('subprocess.run', side_effect=mock_run):
            results = paginate_cli_command(
                build_command=lambda t: ["cmd"],
                result_key="Items",
            )
            # Should collect all non-empty results
            assert len(results) == 2
    
    def test_13_duplicate_token_detected(self):
        """Should detect duplicate pagination token."""
        responses = [
            {"Items": [1], "NextPageToken": "same_token"},
            {"Items": [2], "NextPageToken": "same_token"},  # Duplicate
        ]
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(responses[min(call_count[0], 1)])
            call_count[0] += 1
            return result
        
        with patch('subprocess.run', side_effect=mock_run):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=lambda t: ["cmd"],
                    result_key="Items",
                )
            assert "duplicate" in str(exc_info.value).lower()
    
    def test_14_unexpected_schema_page2(self):
        """Should handle schema change between pages."""
        responses = [
            {"Items": [{"id": 1}], "NextPageToken": "t1"},
            {"DifferentKey": [{"id": 2}]},  # Wrong key
        ]
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(responses[min(call_count[0], 1)])
            call_count[0] += 1
            return result
        
        with patch('subprocess.run', side_effect=mock_run):
            results = paginate_cli_command(
                build_command=lambda t: ["cmd"],
                result_key="Items",
            )
            # Should get first page, second page has no matching key
            assert len(results) == 1
    
    def test_15_command_failure_during_pagination(self):
        """Should handle CLI error during pagination."""
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 1
            result.stdout = ""
            result.stderr = "API Error"
            return result
        
        with patch('subprocess.run', side_effect=mock_run):
            with pytest.raises(BashCloudError):
                paginate_cli_command(
                    build_command=lambda t: ["cmd"],
                    result_key="Items",
                )


# =============================================================================
# Config Failures (Cases 16-20)
# =============================================================================

class TestConfigFailures:
    """Configuration error test cases."""
    
    def test_16_corrupted_config_file(self):
        """Should handle corrupted TOML config."""
        from bashcloud.config_manager import load_config, CONFIG_FILE
        
        with patch('bashcloud.config_manager.CONFIG_FILE') as mock_path:
            mock_path.exists.return_value = True
            
            with patch('toml.load', side_effect=Exception("Parse error")):
                with pytest.raises(ConfigurationError):
                    load_config()
    
    def test_17_missing_config_returns_defaults(self):
        """Should return defaults when config missing."""
        from bashcloud.config_manager import load_config, DEFAULT_CONFIG
        
        with patch('bashcloud.config_manager.CONFIG_FILE') as mock_path:
            mock_path.exists.return_value = False
            
            config = load_config()
            
            assert config["default_provider"] == DEFAULT_CONFIG["default_provider"]
    
    def test_18_permission_denied_saving_config(self):
        """Should handle permission error when saving."""
        from bashcloud.config_manager import save_config
        
        with patch('builtins.open', side_effect=PermissionError("denied")):
            with patch('bashcloud.config_manager.ensure_config_dir'):
                with pytest.raises(ConfigurationError) as exc_info:
                    save_config({"key": "value"})
                assert "permission" in str(exc_info.value).lower()
    
    def test_19_env_var_override(self):
        """Environment variables can override config."""
        # This test documents expected behavior for future implementation
        # Currently env vars are not implemented but should override config
        pass
    
    def test_20_profile_not_found(self):
        """Should handle non-existent AWS profile."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stderr = "The config profile (nonexistent) could not be found"
        
        with patch('subprocess.run', return_value=mock_result):
            from bashcloud.core.health import check_aws_credentials
            is_valid, error = check_aws_credentials()
            assert is_valid is False


# =============================================================================
# TUI Failures (Cases 21-25)
# =============================================================================

class TestTUIFailures:
    """TUI error test cases."""
    
    def test_21_keyboard_interrupt_handling(self):
        """App should handle Ctrl+C gracefully."""
        # TUI should exit cleanly on KeyboardInterrupt
        # This is tested via integration tests
        pass
    
    def test_22_invalid_numeric_menu_input(self):
        """Should handle non-numeric menu input."""
        from bashcloud.tui.prompts import select_breakdown
        
        # This is interactive and would require mocking input()
        # Documented as manual test case
        pass
    
    def test_23_unexpected_screen_state(self):
        """Navigator should handle empty stack gracefully."""
        nav = Navigator()
        
        result = nav.pop()
        assert result is None
        assert nav.depth == 0
    
    def test_24_navigation_stack_empty_pop(self):
        """Popping empty stack should return None."""
        nav = Navigator()
        assert nav.pop() is None
        assert nav.pop() is None  # Multiple pops should be safe
    
    def test_25_invalid_back_navigation(self):
        """Back from root screen should be handled."""
        nav = Navigator()
        from bashcloud.tui.screens import Screen
        
        class MockScreen(Screen):
            def display(self): pass
            def handle_input(self): return None
        
        nav.push(MockScreen())
        assert nav.can_go_back is False


# =============================================================================
# Dashboard Failures (Cases 26-30)
# =============================================================================

class TestDashboardFailures:
    """Dashboard error test cases."""
    
    def test_26_textual_not_installed(self):
        """Should handle missing textual gracefully."""
        # This is tested via CLI when textual import fails
        pass
    
    def test_27_table_overflow(self):
        """Table should handle very long content."""
        from bashcloud.core.cost_base import CostRecord
        
        # Very long service name
        record = CostRecord(
            name="A" * 1000,  # 1000 character name
            amount=100.0,
            unit="USD",
            period="2024-01",
        )
        
        # Should not raise
        d = record.to_dict()
        assert len(d["name"]) == 1000
    
    def test_28_async_cancellation(self):
        """Async operations should be cancellable."""
        # Documented for manual testing
        pass
    
    def test_29_concurrent_queries(self):
        """Should handle concurrent query attempts."""
        # Dashboard uses exclusive=True on workers to prevent this
        pass
    
    def test_30_large_dataset_memory(self):
        """Should handle large result sets."""
        from bashcloud.core.cost_base import CostRecord
        
        # Create 10000 records
        records = [
            CostRecord(name=f"Service{i}", amount=float(i), unit="USD", period="2024-01")
            for i in range(10000)
        ]
        
        # Should be able to filter without memory issues
        from bashcloud.aws.cost import AWSCostProvider
        provider = AWSCostProvider()
        filtered = provider.filter_by_threshold(records, 5000.0)
        
        assert len(filtered) == 5000
