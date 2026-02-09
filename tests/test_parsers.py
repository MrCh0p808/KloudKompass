# tests/test_parsers.py
# ----------------------
# Tests the parser utility functions. These are critical because
# they handle date validation and response parsing that affects all providers.

import pytest
from datetime import date

from bashcloud.utils.parsers import (
    validate_date_format,
    validate_date_range,
    parse_iso_date,
    parse_aws_cost_amount,
    parse_aws_time_period,
    safe_get_nested,
)
from bashcloud.core.exceptions import DateRangeError


class TestValidateDateFormat:
    """Tests for validate_date_format function."""
    
    def test_valid_date(self):
        """Standard ISO date should be valid."""
        assert validate_date_format("2024-01-15") is True
    
    def test_valid_leap_year_date(self):
        """Feb 29 on leap year should be valid."""
        assert validate_date_format("2024-02-29") is True
    
    def test_invalid_leap_year_date(self):
        """Feb 29 on non-leap year should be invalid."""
        assert validate_date_format("2023-02-29") is False
    
    def test_invalid_format_slash(self):
        """Slash-separated date should be invalid."""
        assert validate_date_format("2024/01/15") is False
    
    def test_invalid_format_short_year(self):
        """Two-digit year should be invalid."""
        assert validate_date_format("24-01-15") is False
    
    def test_invalid_month(self):
        """Month 13 should be invalid."""
        assert validate_date_format("2024-13-01") is False
    
    def test_invalid_day(self):
        """Day 32 should be invalid."""
        assert validate_date_format("2024-01-32") is False
    
    def test_empty_string(self):
        """Empty string should be invalid."""
        assert validate_date_format("") is False
    
    def test_random_text(self):
        """Random text should be invalid."""
        assert validate_date_format("not-a-date") is False


class TestValidateDateRange:
    """Tests for validate_date_range function."""
    
    def test_valid_range(self):
        """Normal date range should work."""
        start, end = validate_date_range("2024-01-01", "2024-02-01")
        assert start == date(2024, 1, 1)
        assert end == date(2024, 2, 1)
    
    def test_same_day(self):
        """Same start and end date should be valid."""
        start, end = validate_date_range("2024-01-15", "2024-01-15")
        assert start == end
    
    def test_start_after_end(self):
        """Start date after end date should raise error."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("2024-02-01", "2024-01-01")
        assert "before or equal to" in str(exc_info.value)
    
    def test_invalid_start_format(self):
        """Invalid start date format should raise error."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("01-01-2024", "2024-02-01")
        assert "YYYY-MM-DD" in str(exc_info.value)
    
    def test_invalid_end_format(self):
        """Invalid end date format should raise error."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("2024-01-01", "2024/02/01")
        assert "YYYY-MM-DD" in str(exc_info.value)
    
    def test_invalid_calendar_date(self):
        """Invalid calendar date should raise error."""
        with pytest.raises(DateRangeError) as exc_info:
            validate_date_range("2024-02-30", "2024-03-01")
        assert "valid calendar date" in str(exc_info.value)


class TestParseIsoDate:
    """Tests for parse_iso_date function."""
    
    def test_parse_valid_date(self):
        """Should parse valid ISO date."""
        result = parse_iso_date("2024-06-15")
        assert result == date(2024, 6, 15)
    
    def test_parse_invalid_raises(self):
        """Should raise ValueError for invalid date."""
        with pytest.raises(ValueError):
            parse_iso_date("not-a-date")


class TestParseAWSCostAmount:
    """Tests for parse_aws_cost_amount function."""
    
    def test_normal_amount(self):
        """Should parse normal cost amount."""
        assert parse_aws_cost_amount("123.456789") == 123.46
    
    def test_zero_amount(self):
        """Should parse zero."""
        assert parse_aws_cost_amount("0") == 0.0
    
    def test_small_amount(self):
        """Should round small amounts correctly."""
        assert parse_aws_cost_amount("0.001") == 0.0
    
    def test_large_amount(self):
        """Should handle large amounts."""
        assert parse_aws_cost_amount("12345.678") == 12345.68
    
    def test_invalid_returns_zero(self):
        """Should return 0 for invalid input."""
        assert parse_aws_cost_amount("invalid") == 0.0
    
    def test_none_returns_zero(self):
        """Should return 0 for None input."""
        assert parse_aws_cost_amount(None) == 0.0


class TestParseAWSTimePeriod:
    """Tests for parse_aws_time_period function."""
    
    def test_same_month(self):
        """Should return YYYY-MM for same month period."""
        period = {"Start": "2024-01-01", "End": "2024-01-31"}
        assert parse_aws_time_period(period) == "2024-01"
    
    def test_different_months(self):
        """Should return range for multi-month period."""
        period = {"Start": "2024-01-01", "End": "2024-03-31"}
        result = parse_aws_time_period(period)
        assert "2024-01" in result
        assert "2024-03" in result
    
    def test_empty_period(self):
        """Should handle empty period gracefully."""
        result = parse_aws_time_period({})
        # Returns "Unknown" for robustness rather than empty string
        assert result == "Unknown" or result == ""


class TestSafeGetNested:
    """Tests for safe_get_nested function."""
    
    def test_simple_get(self):
        """Should get simple nested value."""
        data = {"a": {"b": {"c": 123}}}
        assert safe_get_nested(data, "a", "b", "c") == 123
    
    def test_missing_key_returns_default(self):
        """Should return default for missing key."""
        data = {"a": {"b": 1}}
        assert safe_get_nested(data, "a", "x", default="default") == "default"
    
    def test_list_index(self):
        """Should handle list indexing."""
        data = {"items": [{"name": "first"}, {"name": "second"}]}
        assert safe_get_nested(data, "items", 0, "name") == "first"
        assert safe_get_nested(data, "items", 1, "name") == "second"
    
    def test_out_of_bounds_index(self):
        """Should return default for out of bounds."""
        data = {"items": [1, 2]}
        assert safe_get_nested(data, "items", 5, default="nope") == "nope"
    
    def test_none_in_chain(self):
        """Should return default when None encountered."""
        data = {"a": None}
        assert safe_get_nested(data, "a", "b", default="default") == "default"
