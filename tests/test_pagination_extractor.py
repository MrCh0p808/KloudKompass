# tests/test_pagination_extractor.py
# ------------------------------------
# I test the pagination logic including the new result_extractor feature
# that supports both callable and dotted path string extraction.

import pytest
import json
from unittest.mock import patch, Mock

from bashcloud.utils.pagination import (
    paginate_cli_command,
    resolve_dotted_path,
    MAX_PAGES,
)
from bashcloud.core.exceptions import PaginationError


class TestResolveDottedPath:
    """Tests for the dotted path resolution helper."""
    
    def test_simple_key(self):
        """Resolves single key to list."""
        data = {"Items": [1, 2, 3]}
        result = resolve_dotted_path(data, "Items")
        assert result == [1, 2, 3]
    
    def test_nested_keys(self):
        """Resolves nested keys like 'Response.Data.Items'."""
        data = {"Response": {"Data": {"Items": ["a", "b"]}}}
        result = resolve_dotted_path(data, "Response.Data.Items")
        assert result == ["a", "b"]
    
    def test_numeric_index(self):
        """Resolves numeric array index like 'Results.0.Groups'."""
        data = {
            "Results": [
                {"Groups": [{"id": 1}, {"id": 2}]},
                {"Groups": [{"id": 3}]},
            ]
        }
        result = resolve_dotted_path(data, "Results.0.Groups")
        assert result == [{"id": 1}, {"id": 2}]
    
    def test_missing_key_returns_empty(self):
        """Missing key returns empty list."""
        data = {"foo": "bar"}
        result = resolve_dotted_path(data, "missing")
        assert result == []
    
    def test_out_of_bounds_index_returns_empty(self):
        """Out of bounds index returns empty list."""
        data = {"items": [1, 2]}
        result = resolve_dotted_path(data, "items.5")
        assert result == []
    
    def test_empty_path_returns_data_if_list(self):
        """Empty path returns data if already a list."""
        data = [1, 2, 3]
        result = resolve_dotted_path(data, "")
        assert result == [1, 2, 3]
    
    def test_empty_path_non_list_returns_empty(self):
        """Empty path on non-list returns empty."""
        data = {"key": "value"}
        result = resolve_dotted_path(data, "")
        assert result == []


class TestPaginateCliCommandWithExtractor:
    """Tests for paginate_cli_command with result_extractor."""
    
    def test_callable_extractor_single_page(self):
        """Callable extractor works for single page."""
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "Items": [{"id": 1}, {"id": 2}],
        })
        
        with patch("bashcloud.utils.pagination.run_cli_command", return_value=mock_result):
            results = paginate_cli_command(
                build_command=lambda t: ["cmd"],
                result_extractor=lambda d: d.get("Items", []),
            )
        
        assert len(results) == 2
        assert results[0]["id"] == 1
    
    def test_dotted_path_extractor_single_page(self):
        """Dotted path string extractor works for single page."""
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "Response": {"Data": [{"name": "test"}]},
        })
        
        with patch("bashcloud.utils.pagination.run_cli_command", return_value=mock_result):
            results = paginate_cli_command(
                build_command=lambda t: ["cmd"],
                result_extractor="Response.Data",
            )
        
        assert len(results) == 1
        assert results[0]["name"] == "test"
    
    def test_two_pages_merged(self):
        """Results from two pages are merged correctly."""
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            call_count[0] += 1
            result = Mock()
            if call_count[0] == 1:
                result.stdout = json.dumps({
                    "Items": [{"id": 1}],
                    "NextPageToken": "token1",
                })
            else:
                result.stdout = json.dumps({
                    "Items": [{"id": 2}],
                })
            return result
        
        with patch("bashcloud.utils.pagination.run_cli_command", side_effect=mock_run):
            results = paginate_cli_command(
                build_command=lambda t: ["cmd"] + (["--next-token", t] if t else []),
                result_extractor="Items",
            )
        
        assert len(results) == 2
        assert results[0]["id"] == 1
        assert results[1]["id"] == 2
    
    def test_custom_page_token_key(self):
        """Custom page_token_key is respected."""
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            call_count[0] += 1
            result = Mock()
            if call_count[0] == 1:
                result.stdout = json.dumps({
                    "data": [1],
                    "cursor": "next",  # Custom token key
                })
            else:
                result.stdout = json.dumps({
                    "data": [2],
                })
            return result
        
        with patch("bashcloud.utils.pagination.run_cli_command", side_effect=mock_run):
            results = paginate_cli_command(
                build_command=lambda t: ["cmd"],
                result_extractor="data",
                page_token_key="cursor",
            )
        
        assert results == [1, 2]
    
    def test_duplicate_token_raises_error(self):
        """Duplicate pagination token raises PaginationError."""
        call_count = [0]
        
        def mock_run(*args, **kwargs):
            call_count[0] += 1
            result = Mock()
            # I return the same token every time to trigger duplicate detection
            result.stdout = json.dumps({
                "Items": [call_count[0]],
                "NextPageToken": "same_token",
            })
            return result
        
        with patch("bashcloud.utils.pagination.run_cli_command", side_effect=mock_run):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=lambda t: ["cmd"],
                    result_extractor="Items",
                )
            
            assert "Duplicate" in str(exc_info.value)
    
    def test_max_pages_exceeded_raises_error(self):
        """Exceeding max pages raises PaginationError."""
        page_num = [0]
        
        def mock_run(*args, **kwargs):
            page_num[0] += 1
            result = Mock()
            result.stdout = json.dumps({
                "Items": [page_num[0]],
                "NextPageToken": f"token{page_num[0]}",
            })
            return result
        
        with patch("bashcloud.utils.pagination.run_cli_command", side_effect=mock_run):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=lambda t: ["cmd"],
                    result_extractor="Items",
                    max_pages=3,
                )
            
            assert "maximum" in str(exc_info.value).lower()
    
    def test_invalid_json_raises_error(self):
        """Invalid JSON response raises PaginationError."""
        mock_result = Mock()
        mock_result.stdout = "not valid json"
        
        with patch("bashcloud.utils.pagination.run_cli_command", return_value=mock_result):
            with pytest.raises(PaginationError) as exc_info:
                paginate_cli_command(
                    build_command=lambda t: ["cmd"],
                    result_extractor="Items",
                )
            
            assert "parse" in str(exc_info.value).lower()
