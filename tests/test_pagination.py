# tests/test_pagination.py
# -------------------------
# Tests the pagination utility. Pagination is tricky because we need
# to handle multi-page responses, detect infinite loops, and merge results.

import pytest
import json
from unittest.mock import patch, Mock, call

from kloudkompass.utils.pagination import (
    paginate_cli_command,
    paginate_aws_cost_explorer,
)
from kloudkompass.core.exceptions import PaginationError


class TestPaginateCLICommand:
    """Tests for the generic pagination function."""
    
    def test_single_page_response(self):
        """Should handle single page (no pagination needed)."""
        response = {
            "Items": [{"id": 1}, {"id": 2}],
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        
        def build_cmd(token):
            cmd = ["test", "command"]
            if token:
                cmd.extend(["--token", token])
            return cmd
        
        with patch('subprocess.run', return_value=mock_result):
            results = paginate_cli_command(
                build_command=build_cmd,
                result_key="Items",
            )
        
        assert len(results) == 2
    
    def test_multi_page_response(self):
        """Should collect results from multiple pages."""
        page1 = {
            "Items": [{"id": 1}],
            "NextPageToken": "token1"
        }
        page2 = {
            "Items": [{"id": 2}],
            "NextPageToken": "token2"
        }
        page3 = {
            "Items": [{"id": 3}],
            # No NextPageToken = last page
        }
        
        # Mock returns different pages on each call
        responses = [page1, page2, page3]
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(responses[call_count[0]])
            call_count[0] += 1
            return result
        
        def build_cmd(token):
            return ["test", "command"]
        
        with patch('subprocess.run', side_effect=mock_run):
            results = paginate_cli_command(
                build_command=build_cmd,
                result_key="Items",
            )
        
        assert len(results) == 3
        assert call_count[0] == 3
    
    def test_max_pages_exceeded(self):
        """Should raise PaginationError when max pages exceeded."""
        # Response always has a next token = infinite loop
        response = {
            "Items": [{"id": 1}],
            "NextPageToken": "infinite"
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        
        # But we change the token each time to avoid duplicate detection
        page_num = [0]
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            data = {"Items": [{"id": 1}], "NextPageToken": f"token{page_num[0]}"}
            page_num[0] += 1
            result.stdout = json.dumps(data)
            return result
        
        def build_cmd(token):
            return ["test", "command"]
        
        with patch('subprocess.run', side_effect=mock_run):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=build_cmd,
                    result_key="Items",
                    max_pages=5,
                )
            
            assert "maximum page count" in str(exc_info.value).lower()
    
    def test_duplicate_token_detected(self):
        """Should raise PaginationError on duplicate token (infinite loop)."""
        # Same token returned twice = loop detected
        responses = [
            {"Items": [{"id": 1}], "NextPageToken": "same_token"},
            {"Items": [{"id": 2}], "NextPageToken": "same_token"},  # Duplicate!
        ]
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(responses[min(call_count[0], 1)])
            call_count[0] += 1
            return result
        
        def build_cmd(token):
            return ["test", "command"]
        
        with patch('subprocess.run', side_effect=mock_run):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=build_cmd,
                    result_key="Items",
                )
            
            assert "duplicate" in str(exc_info.value).lower()


class TestPaginateAWSCostExplorer:
    """Tests specific to AWS Cost Explorer pagination."""
    
    def test_single_page(self):
        """Should handle single page CE response."""
        response = {
            "ResultsByTime": [
                {"TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"}}
            ]
        }
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response)
        
        with patch('subprocess.run', return_value=mock_result):
            result = paginate_aws_cost_explorer(["aws", "ce", "get-cost-and-usage"])
        
        assert "ResultsByTime" in result
        assert len(result["ResultsByTime"]) == 1
    
    def test_merges_results_by_time(self):
        """Should merge ResultsByTime from all pages."""
        page1 = {
            "ResultsByTime": [{"TimePeriod": {"Start": "2024-01-01"}}],
            "NextPageToken": "next"
        }
        page2 = {
            "ResultsByTime": [{"TimePeriod": {"Start": "2024-02-01"}}],
        }
        
        responses = [page1, page2]
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            result = Mock()
            result.returncode = 0
            result.stdout = json.dumps(responses[call_count[0]])
            call_count[0] += 1
            return result
        
        with patch('subprocess.run', side_effect=mock_run):
            result = paginate_aws_cost_explorer(["aws", "ce", "get-cost-and-usage"])
        
        # Both time periods should be merged
        assert len(result["ResultsByTime"]) == 2
