# tests/test_cost_aws.py
# -----------------------
# Tests the AWS cost provider. These tests mock subprocess to avoid
# needing real AWS credentials. They cover positive cases and error handling.

import pytest
import json
from unittest.mock import patch, Mock

from bashcloud.aws.cost import AWSCostProvider
from bashcloud.core.cost_base import CostRecord
from bashcloud.core.exceptions import (
    CLIUnavailableError,
    CredentialError,
    DateRangeError,
)

# Import sample data from conftest
from conftest import (
    SAMPLE_AWS_COST_BY_SERVICE,
    SAMPLE_AWS_COST_TOTAL,
    SAMPLE_AWS_COST_DAILY,
    SAMPLE_AWS_COST_EMPTY,
)


class TestAWSCostProviderBasics:
    """Basic tests for AWSCostProvider."""
    
    def test_provider_name(self):
        """Provider should identify as AWS."""
        provider = AWSCostProvider()
        assert provider.provider_name == "AWS"
        assert provider.cli_command == "aws"
    
    def test_is_available_when_installed(self):
        """is_available should return True when aws CLI exists."""
        provider = AWSCostProvider()
        with patch('shutil.which', return_value='/usr/bin/aws'):
            assert provider.is_available() is True
    
    def test_is_available_when_not_installed(self):
        """is_available should return False when aws CLI missing."""
        provider = AWSCostProvider()
        with patch('shutil.which', return_value=None):
            assert provider.is_available() is False


class TestAWSCostByService:
    """Tests for get_cost_by_service method."""
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_returns_cost_records(self, mock_creds, mock_which):
        """Should return list of CostRecord objects."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_AWS_COST_BY_SERVICE)
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_cost_by_service(
                start_date="2024-01-01",
                end_date="2024-02-01"
            )
        
        assert len(records) == 3
        assert all(isinstance(r, CostRecord) for r in records)
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_sorted_by_cost_descending(self, mock_creds, mock_which):
        """Results should be sorted by amount, highest first."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_AWS_COST_BY_SERVICE)
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_cost_by_service(
                start_date="2024-01-01",
                end_date="2024-02-01"
            )
        
        # First should be EC2 (123.45), last should be Lambda (12.34)
        assert records[0].amount > records[-1].amount
        assert records[0].amount == 123.45
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_records_have_correct_fields(self, mock_creds, mock_which):
        """CostRecord objects should have all required fields."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_AWS_COST_BY_SERVICE)
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_cost_by_service(
                start_date="2024-01-01",
                end_date="2024-02-01"
            )
        
        record = records[0]
        assert hasattr(record, 'name')
        assert hasattr(record, 'amount')
        assert hasattr(record, 'unit')
        assert hasattr(record, 'period')
        assert record.unit == "USD"


class TestAWSCostTotal:
    """Tests for get_total_cost method."""
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_returns_single_record(self, mock_creds, mock_which):
        """Total should return single CostRecord."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_AWS_COST_TOTAL)
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_total_cost(
                start_date="2024-01-01",
                end_date="2024-02-01"
            )
        
        assert len(records) == 1
        assert records[0].name == "Total"
        assert records[0].amount == 181.46


class TestAWSCostDaily:
    """Tests for get_daily_cost method."""
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_returns_daily_records(self, mock_creds, mock_which):
        """Should return one record per day."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_AWS_COST_DAILY)
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_daily_cost(
                start_date="2024-01-01",
                end_date="2024-01-04"
            )
        
        assert len(records) == 3
        # Check they are chronological
        assert records[0].name == "2024-01-01"
        assert records[1].name == "2024-01-02"
        assert records[2].name == "2024-01-03"


class TestAWSCostEmptyResults:
    """Tests for empty result handling."""
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_empty_results_handled(self, mock_creds, mock_which):
        """Should handle empty results gracefully."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(SAMPLE_AWS_COST_EMPTY)
        mock_result.stderr = ""
        
        with patch('subprocess.run', return_value=mock_result):
            provider = AWSCostProvider()
            records = provider.get_total_cost(
                start_date="2024-01-01",
                end_date="2024-02-01"
            )
        
        # Should return a zero-cost record, not crash
        assert len(records) == 1
        assert records[0].amount == 0.0


class TestAWSCostValidation:
    """Tests for input validation."""
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_invalid_date_format_raises(self, mock_creds, mock_which):
        """Should raise DateRangeError for invalid date format."""
        provider = AWSCostProvider()
        
        with pytest.raises(DateRangeError):
            provider.get_cost_by_service(
                start_date="01-01-2024",  # Wrong format
                end_date="2024-02-01"
            )
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    @patch('bashcloud.core.health.check_aws_credentials', return_value=(True, None))
    def test_start_after_end_raises(self, mock_creds, mock_which):
        """Should raise DateRangeError when start > end."""
        provider = AWSCostProvider()
        
        with pytest.raises(DateRangeError):
            provider.get_cost_by_service(
                start_date="2024-02-01",
                end_date="2024-01-01"
            )


class TestAWSCostCLINotInstalled:
    """Tests for CLI not installed scenario."""
    
    def test_raises_cli_unavailable(self):
        """Should raise CLIUnavailableError when aws CLI missing."""
        provider = AWSCostProvider()
        
        with patch('shutil.which', return_value=None):
            with pytest.raises(CLIUnavailableError) as exc_info:
                provider.get_cost_by_service(
                    start_date="2024-01-01",
                    end_date="2024-02-01"
                )
            
            assert "aws" in str(exc_info.value).lower()


class TestAWSCostCredentialsInvalid:
    """Tests for credential error handling."""
    
    @patch('shutil.which', return_value='/usr/bin/aws')
    def test_raises_credential_error(self, mock_which):
        """Should raise CredentialError when credentials invalid."""
        provider = AWSCostProvider()
        
        with patch('bashcloud.core.health.check_aws_credentials', 
                   return_value=(False, "No credentials configured")):
            with pytest.raises(CredentialError) as exc_info:
                provider.get_cost_by_service(
                    start_date="2024-01-01",
                    end_date="2024-02-01"
                )
            
            assert "aws" in str(exc_info.value).lower()


class TestAWSCostThresholdFilter:
    """Tests for threshold filtering."""
    
    def test_filter_removes_small_costs(self):
        """filter_by_threshold should remove records below threshold."""
        provider = AWSCostProvider()
        
        records = [
            CostRecord(name="Big", amount=100.0, unit="USD", period="2024-01"),
            CostRecord(name="Medium", amount=5.0, unit="USD", period="2024-01"),
            CostRecord(name="Small", amount=0.5, unit="USD", period="2024-01"),
        ]
        
        filtered = provider.filter_by_threshold(records, threshold=1.0)
        
        assert len(filtered) == 2
        assert filtered[0].name == "Big"
        assert filtered[1].name == "Medium"
    
    def test_filter_with_zero_threshold(self):
        """Zero threshold should keep all records."""
        provider = AWSCostProvider()
        
        records = [
            CostRecord(name="A", amount=0.01, unit="USD", period="2024-01"),
        ]
        
        filtered = provider.filter_by_threshold(records, threshold=0.0)
        
        assert len(filtered) == 1
