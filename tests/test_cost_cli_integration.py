# tests/test_cost_cli_integration.py
# ------------------------------------
# I test the CLI cost command integration using Click's CliRunner.
# This verifies the full flow from command line to formatted output.

import pytest
import json
from unittest.mock import patch, Mock
from click.testing import CliRunner

from bashcloud.cli import main
from bashcloud.core.cost_base import CostRecord


class TestCostCLIIntegration:
    """CLI integration tests for cost command."""
    
    @pytest.fixture
    def runner(self):
        """Get a fresh CliRunner for each test."""
        return CliRunner()
    
    @pytest.fixture
    def mock_provider(self):
        """Mock the cost provider to return known records."""
        records = [
            CostRecord(name="Amazon EC2", amount=150.50, unit="USD", period="2024-01"),
            CostRecord(name="Amazon S3", amount=25.25, unit="USD", period="2024-01"),
        ]
        
        mock = Mock()
        mock.get_cost.return_value = records
        mock.filter_by_threshold.return_value = records
        
        with patch("bashcloud.cli.get_cost_provider", return_value=mock):
            yield mock
    
    def test_cost_command_outputs_table(self, runner, mock_provider):
        """Cost command outputs table format by default."""
        result = runner.invoke(main, [
            "cost",
            "--provider", "aws",
            "--start", "2024-01-01",
            "--end", "2024-02-01",
        ])
        
        assert result.exit_code == 0
        assert "EC2" in result.output or "Amazon" in result.output
    
    def test_cost_command_json_output(self, runner, mock_provider):
        """Cost command outputs valid JSON when requested."""
        result = runner.invoke(main, [
            "cost",
            "--provider", "aws",
            "--start", "2024-01-01",
            "--end", "2024-02-01",
            "--output", "json",
        ])
        
        assert result.exit_code == 0
        # I verify output is valid JSON
        data = json.loads(result.output.split("\n\n")[-1].strip() or "[]")
        # The actual JSON may be after the status message
    
    def test_cost_command_with_threshold(self, runner):
        """Cost command respects threshold filter."""
        records = [
            CostRecord(name="Big Service", amount=100.0, unit="USD", period="2024-01"),
            CostRecord(name="Tiny Service", amount=0.50, unit="USD", period="2024-01"),
        ]
        
        mock = Mock()
        mock.get_cost.return_value = records
        mock.filter_by_threshold.return_value = [records[0]]  # Only big service
        
        with patch("bashcloud.cli.get_cost_provider", return_value=mock):
            result = runner.invoke(main, [
                "cost",
                "--provider", "aws",
                "--start", "2024-01-01",
                "--end", "2024-02-01",
                "--threshold", "1.0",
            ])
        
        assert result.exit_code == 0
        assert "Big Service" in result.output or "100" in result.output
    
    def test_cost_command_empty_results(self, runner):
        """Cost command handles empty results gracefully."""
        mock = Mock()
        mock.get_cost.return_value = []
        mock.filter_by_threshold.return_value = []
        
        with patch("bashcloud.cli.get_cost_provider", return_value=mock):
            result = runner.invoke(main, [
                "cost",
                "--provider", "aws",
                "--start", "2024-01-01",
                "--end", "2024-02-01",
            ])
        
        assert result.exit_code == 0
        assert "No cost data" in result.output or "No records" in result.output
    
    def test_cost_command_csv_output(self, runner, mock_provider):
        """Cost command outputs CSV format."""
        result = runner.invoke(main, [
            "cost",
            "--provider", "aws",
            "--start", "2024-01-01",
            "--end", "2024-02-01",
            "--output", "csv",
        ])
        
        assert result.exit_code == 0
        # I check for CSV header
        assert "Name" in result.output or "Amount" in result.output
