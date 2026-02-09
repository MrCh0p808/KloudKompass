# tests/test_cost_aws_paged.py
# -----------------------------
# I test the AWS cost provider with mocked paged responses to verify
# it correctly handles multi-page results and returns List[CostRecord].

import pytest
import json
from unittest.mock import patch, Mock

from bashcloud.aws.cost import AWSCostProvider
from bashcloud.core.cost_base import CostRecord


class TestAWSCostProviderPaged:
    """Integration tests for AWS cost provider with pagination."""
    
    @pytest.fixture
    def mock_credentials(self):
        """Mock the credential checks to always pass."""
        with patch("bashcloud.aws.cost.require_cli"):
            with patch("bashcloud.aws.cost.require_credentials"):
                yield
    
    def test_get_cost_by_service_two_pages(self, mock_credentials):
        """Provider merges two pages of service costs correctly."""
        call_count = [0]
        
        def mock_run(command, **kwargs):
            call_count[0] += 1
            result = Mock()
            
            if call_count[0] == 1:
                result.stdout = json.dumps({
                    "ResultsByTime": [{
                        "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
                        "Groups": [
                            {"Keys": ["Amazon EC2"], "Metrics": {"UnblendedCost": {"Amount": "100.50", "Unit": "USD"}}},
                        ],
                    }],
                    "NextPageToken": "page2token",
                })
            else:
                result.stdout = json.dumps({
                    "ResultsByTime": [{
                        "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
                        "Groups": [
                            {"Keys": ["Amazon S3"], "Metrics": {"UnblendedCost": {"Amount": "25.25", "Unit": "USD"}}},
                        ],
                    }],
                })
            return result
        
        with patch("bashcloud.utils.pagination.run_cli_command", side_effect=mock_run):
            provider = AWSCostProvider()
            records = provider.get_cost_by_service("2024-01-01", "2024-02-01")
        
        assert len(records) == 2
        assert all(isinstance(r, CostRecord) for r in records)
        
        names = [r.name for r in records]
        assert "Amazon EC2" in names
        assert "Amazon S3" in names
    
    def test_get_total_cost_returns_cost_record(self, mock_credentials):
        """get_total_cost returns CostRecord instances."""
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "ResultsByTime": [{
                "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
                "Total": {"UnblendedCost": {"Amount": "500.00", "Unit": "USD"}},
            }],
        })
        
        with patch("bashcloud.utils.pagination.run_cli_command", return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_total_cost("2024-01-01", "2024-02-01")
        
        assert len(records) == 1
        assert isinstance(records[0], CostRecord)
        assert records[0].name == "Total"
        assert records[0].amount == 500.00
    
    def test_get_daily_cost_returns_sorted_records(self, mock_credentials):
        """get_daily_cost returns chronologically sorted CostRecords."""
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "ResultsByTime": [
                {"TimePeriod": {"Start": "2024-01-02"}, "Total": {"UnblendedCost": {"Amount": "20.0", "Unit": "USD"}}},
                {"TimePeriod": {"Start": "2024-01-01"}, "Total": {"UnblendedCost": {"Amount": "10.0", "Unit": "USD"}}},
            ],
        })
        
        with patch("bashcloud.utils.pagination.run_cli_command", return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_daily_cost("2024-01-01", "2024-01-03")
        
        assert len(records) == 2
        # I verify sorted by date (name contains date)
        assert records[0].name <= records[1].name


class TestAWSCostProviderEmptyResults:
    """Tests for empty result handling."""
    
    @pytest.fixture
    def mock_credentials(self):
        with patch("bashcloud.aws.cost.require_cli"):
            with patch("bashcloud.aws.cost.require_credentials"):
                yield
    
    def test_empty_results_by_time(self, mock_credentials):
        """Provider handles empty ResultsByTime gracefully."""
        mock_result = Mock()
        mock_result.stdout = json.dumps({
            "ResultsByTime": [],
        })
        
        with patch("bashcloud.utils.pagination.run_cli_command", return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_cost_by_service("2024-01-01", "2024-02-01")
        
        assert records == []
