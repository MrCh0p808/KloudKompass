# tests/conftest.py
# ------------------
# up pytest fixtures set here that provide mocked AWS CLI responses.
# This lets tests run without needing real AWS credentials.

import pytest
import json
from unittest.mock import Mock, patch


# Sample AWS Cost Explorer response with multiple services
SAMPLE_AWS_COST_BY_SERVICE = {
    "ResultsByTime": [
        {
            "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
            "Groups": [
                {
                    "Keys": ["Amazon Elastic Compute Cloud - Compute"],
                    "Metrics": {
                        "UnblendedCost": {"Amount": "123.45", "Unit": "USD"}
                    }
                },
                {
                    "Keys": ["Amazon Simple Storage Service"],
                    "Metrics": {
                        "UnblendedCost": {"Amount": "45.67", "Unit": "USD"}
                    }
                },
                {
                    "Keys": ["AWS Lambda"],
                    "Metrics": {
                        "UnblendedCost": {"Amount": "12.34", "Unit": "USD"}
                    }
                },
            ]
        }
    ]
}

# Sample total cost response
SAMPLE_AWS_COST_TOTAL = {
    "ResultsByTime": [
        {
            "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
            "Total": {
                "UnblendedCost": {"Amount": "181.46", "Unit": "USD"}
            }
        }
    ]
}

# Sample daily cost response
SAMPLE_AWS_COST_DAILY = {
    "ResultsByTime": [
        {
            "TimePeriod": {"Start": "2024-01-01", "End": "2024-01-02"},
            "Total": {"UnblendedCost": {"Amount": "5.50", "Unit": "USD"}}
        },
        {
            "TimePeriod": {"Start": "2024-01-02", "End": "2024-01-03"},
            "Total": {"UnblendedCost": {"Amount": "6.75", "Unit": "USD"}}
        },
        {
            "TimePeriod": {"Start": "2024-01-03", "End": "2024-01-04"},
            "Total": {"UnblendedCost": {"Amount": "4.25", "Unit": "USD"}}
        },
    ]
}

# Empty response (free tier or no usage)
SAMPLE_AWS_COST_EMPTY = {
    "ResultsByTime": []
}

# Paginated response (page 1)
SAMPLE_AWS_COST_PAGE1 = {
    "ResultsByTime": [
        {
            "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
            "Groups": [
                {
                    "Keys": ["Service1"],
                    "Metrics": {"UnblendedCost": {"Amount": "10.00", "Unit": "USD"}}
                },
            ]
        }
    ],
    "NextPageToken": "token123"
}

# Paginated response (page 2, last)
SAMPLE_AWS_COST_PAGE2 = {
    "ResultsByTime": [
        {
            "TimePeriod": {"Start": "2024-01-01", "End": "2024-02-01"},
            "Groups": [
                {
                    "Keys": ["Service2"],
                    "Metrics": {"UnblendedCost": {"Amount": "20.00", "Unit": "USD"}}
                },
            ]
        }
    ]
}


@pytest.fixture
def mock_subprocess_success():
    """
    Fixture that mocks subprocess.run to return successful AWS CLI response.
    
    Usage:
        def test_something(mock_subprocess_success):
            mock_subprocess_success(SAMPLE_AWS_COST_BY_SERVICE)
            # now any subprocess.run call returns this response
    """
    def _mock(response_data):
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(response_data)
        mock_result.stderr = ""
        
        patcher = patch('subprocess.run', return_value=mock_result)
        mock_run = patcher.start()
        return mock_run, patcher
    
    return _mock


@pytest.fixture
def mock_cli_installed():
    """
    Fixture that mocks shutil.which to indicate CLI is installed.
    """
    with patch('shutil.which', return_value='/usr/bin/aws'):
        yield


@pytest.fixture
def mock_cli_not_installed():
    """
    Fixture that mocks shutil.which to indicate CLI is NOT installed.
    """
    with patch('shutil.which', return_value=None):
        yield


@pytest.fixture
def mock_aws_credentials_valid():
    """
    Fixture that mocks AWS credentials as valid.
    """
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = '{"UserId": "AIDAEXAMPLE", "Account": "123456789012"}'
    mock_result.stderr = ""
    
    with patch('subprocess.run', return_value=mock_result):
        yield


@pytest.fixture
def mock_aws_credentials_invalid():
    """
    Fixture that mocks AWS credentials as invalid.
    """
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = ""
    mock_result.stderr = "Unable to locate credentials"
    
    with patch('subprocess.run', return_value=mock_result):
        yield
