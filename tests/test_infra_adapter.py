# tests/test_infra_adapter.py
# ----------------------------
# Tests the infrastructure adapter layer. These tests verify that
# CLI execution is properly abstracted.

import pytest
import json
from unittest.mock import patch, Mock

from bashcloud.infra.cli_adapter import CLIAdapter, CLIResult
from bashcloud.core.exceptions import BashCloudError, ParsingError


class TestCLIResult:
    """Tests for CLIResult dataclass."""
    
    def test_success_property(self):
        """success should be True for returncode 0."""
        result = CLIResult(
            command=["test"],
            returncode=0,
            stdout="output",
            stderr="",
        )
        assert result.success is True
    
    def test_failure_property(self):
        """success should be False for non-zero returncode."""
        result = CLIResult(
            command=["test"],
            returncode=1,
            stdout="",
            stderr="error",
        )
        assert result.success is False
    
    def test_json_parsing(self):
        """json() should parse stdout as JSON."""
        result = CLIResult(
            command=["test"],
            returncode=0,
            stdout='{"key": "value"}',
            stderr="",
        )
        data = result.json()
        assert data == {"key": "value"}
    
    def test_json_invalid_raises(self):
        """json() should raise ParsingError for invalid JSON."""
        result = CLIResult(
            command=["test"],
            returncode=0,
            stdout="not json",
            stderr="",
        )
        with pytest.raises(ParsingError):
            result.json()


class TestCLIAdapter:
    """Tests for CLIAdapter class."""
    
    def test_is_available_when_installed(self):
        """is_available should return True when CLI exists."""
        adapter = CLIAdapter("python")
        with patch('shutil.which', return_value='/usr/bin/python'):
            assert adapter.is_available() is True
    
    def test_is_available_when_not_installed(self):
        """is_available should return False when CLI missing."""
        adapter = CLIAdapter("nonexistent")
        with patch('shutil.which', return_value=None):
            assert adapter.is_available() is False
    
    def test_run_returns_cli_result(self):
        """run should return CLIResult."""
        adapter = CLIAdapter("echo")
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "hello"
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            result = adapter.run(["hello"])
        
        assert isinstance(result, CLIResult)
        assert result.success is True
        assert result.stdout == "hello"
    
    def test_run_with_check_raises_on_failure(self):
        """run with check=True should raise on failure."""
        adapter = CLIAdapter("test")
        
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error"
        
        with patch('subprocess.run', return_value=mock_result):
            with pytest.raises(BashCloudError):
                adapter.run(["args"], check=True)
    
    def test_run_json_returns_dict(self):
        """run_json should return parsed dictionary."""
        adapter = CLIAdapter("test")
        
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"result": 123}'
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            data = adapter.run_json(["args"])
        
        assert data == {"result": 123}
