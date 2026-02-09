# tests/test_aws_adapter.py
# --------------------------
# I test the AWS CLI adapter including version parsing, credential checks,
# and pagination handling.

import pytest
import json
from unittest.mock import patch, Mock

from bashcloud.infra.aws_cli_adapter import AWSCLIAdapter, get_aws_cli_adapter
from bashcloud.core.exceptions import PaginationError


class TestAWSCLIAdapterVersion:
    """Tests for AWS CLI version checking."""
    
    def test_get_cli_version_parses_v2(self):
        """Should parse AWS CLI v2 version string."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = "aws-cli/2.15.0 Python/3.11.6 Linux/5.15.0"
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            version = adapter.get_cli_version()
        
        assert version == "2.15.0"
    
    def test_get_cli_version_parses_v1(self):
        """Should parse AWS CLI v1 version string."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = "aws-cli/1.27.0 Python/3.9.0"
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            version = adapter.get_cli_version()
        
        assert version == "1.27.0"
    
    def test_get_cli_version_returns_none_on_failure(self):
        """Should return None if version check fails."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = False
        mock_result.stdout = ""
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            version = adapter.get_cli_version()
        
        assert version is None


class TestAWSCLIAdapterCredentials:
    """Tests for credential checking."""
    
    def test_check_credentials_valid(self):
        """Should return (True, None) for valid credentials."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = '{"UserId": "...", "Account": "123456789012"}'
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            is_valid, error = adapter.check_credentials()
        
        assert is_valid is True
        assert error is None
    
    def test_check_credentials_expired(self):
        """Should detect expired token."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = False
        mock_result.stderr = "ExpiredToken: The security token has expired"
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            is_valid, error = adapter.check_credentials()
        
        assert is_valid is False
        assert "expired" in error.lower()
    
    def test_check_credentials_invalid_key(self):
        """Should detect invalid access key."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = False
        mock_result.stderr = "InvalidClientTokenId: The security token is invalid"
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            is_valid, error = adapter.check_credentials()
        
        assert is_valid is False
        assert "invalid" in error.lower()


class TestAWSCLIAdapterPagination:
    """Tests for Cost Explorer pagination."""
    
    def test_get_cost_explorer_single_page(self):
        """Should handle single page response."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = json.dumps({
            "ResultsByTime": [{"TimePeriod": {"Start": "2024-01-01"}}],
        })
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            result = adapter.get_cost_explorer_data("2024-01-01", "2024-02-01")
        
        assert len(result["ResultsByTime"]) == 1
        assert adapter.page_count == 1
    
    def test_get_cost_explorer_multiple_pages(self):
        """Should merge multiple pages."""
        adapter = AWSCLIAdapter()
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            call_count[0] += 1
            mock_result = Mock()
            mock_result.success = True
            
            if call_count[0] == 1:
                mock_result.stdout = json.dumps({
                    "ResultsByTime": [{"id": 1}],
                    "NextPageToken": "token1",
                })
            else:
                mock_result.stdout = json.dumps({
                    "ResultsByTime": [{"id": 2}],
                })
            return mock_result
        
        with patch.object(adapter, "run_command", side_effect=mock_run):
            result = adapter.get_cost_explorer_data("2024-01-01", "2024-02-01")
        
        assert len(result["ResultsByTime"]) == 2
        assert adapter.page_count == 2
    
    def test_get_cost_explorer_records_duration(self):
        """Should record query duration."""
        adapter = AWSCLIAdapter()
        
        mock_result = Mock()
        mock_result.success = True
        mock_result.stdout = json.dumps({"ResultsByTime": []})
        
        with patch.object(adapter, "run_command", return_value=mock_result):
            adapter.get_cost_explorer_data("2024-01-01", "2024-02-01")
        
        assert adapter.query_duration > 0


class TestGetAWSCLIAdapter:
    """Tests for singleton accessor."""
    
    def test_returns_same_instance(self):
        """Should return singleton instance."""
        adapter1 = get_aws_cli_adapter()
        adapter2 = get_aws_cli_adapter()
        
        assert adapter1 is adapter2
