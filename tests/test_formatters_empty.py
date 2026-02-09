# tests/test_formatters_empty.py
# -------------------------------
# I test that all formatters handle empty record lists without crashing
# and return appropriate output for each format type.

import pytest
from io import StringIO
import sys

from bashcloud.utils.formatters import (
    format_as_table,
    format_as_plain,
    format_as_json,
    format_as_csv,
    format_records,
    OutputFormat,
)
from bashcloud.core.cost_base import CostRecord


class TestFormattersEmptyList:
    """Tests for empty list handling in formatters."""
    
    def test_format_as_table_empty_no_crash(self, capsys):
        """Table formatter handles empty list without exception."""
        # I verify no exception raised
        format_as_table([])
        captured = capsys.readouterr()
        # I expect some output (the table with "No records" row)
        assert "No records" in captured.out or captured.out != ""
    
    def test_format_as_table_empty_with_title(self, capsys):
        """Table formatter handles empty list with title."""
        format_as_table([], title="Empty Results")
        captured = capsys.readouterr()
        assert "Empty Results" in captured.out or captured.out != ""
    
    def test_format_as_plain_empty_no_crash(self, capsys):
        """Plain formatter handles empty list without exception."""
        format_as_plain([])
        captured = capsys.readouterr()
        assert "No records" in captured.out
    
    def test_format_as_plain_empty_with_title(self, capsys):
        """Plain formatter handles empty list with title."""
        format_as_plain([], title="Empty Results")
        captured = capsys.readouterr()
        assert "Empty Results" in captured.out
        assert "No records" in captured.out
    
    def test_format_as_json_empty(self, capsys):
        """JSON formatter outputs empty array for empty list."""
        format_as_json([])
        captured = capsys.readouterr()
        assert captured.out.strip() == "[]"
    
    def test_format_as_csv_empty_with_header(self, capsys):
        """CSV formatter outputs header for empty list."""
        format_as_csv([], include_header=True)
        captured = capsys.readouterr()
        assert "Name,Amount,Unit,Period" in captured.out
    
    def test_format_as_csv_empty_no_header(self, capsys):
        """CSV formatter outputs nothing for empty list without header."""
        format_as_csv([], include_header=False)
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_format_records_table_empty(self, capsys):
        """format_records routes empty list to table correctly."""
        format_records([], OutputFormat.TABLE)
        # I just check no exception raised
        captured = capsys.readouterr()
        assert captured.err == ""
    
    def test_format_records_plain_empty(self, capsys):
        """format_records routes empty list to plain correctly."""
        format_records([], OutputFormat.PLAIN)
        captured = capsys.readouterr()
        assert "No records" in captured.out
    
    def test_format_records_json_empty(self, capsys):
        """format_records routes empty list to json correctly."""
        format_records([], OutputFormat.JSON)
        captured = capsys.readouterr()
        assert "[]" in captured.out


class TestFormattersNonEmpty:
    """Sanity tests for non-empty list handling."""
    
    def test_format_as_plain_single_record(self, capsys):
        """Plain formatter handles single record correctly."""
        records = [CostRecord(name="EC2", amount=100.50, unit="USD", period="2024-01")]
        format_as_plain(records)
        captured = capsys.readouterr()
        assert "EC2" in captured.out
        assert "100.50" in captured.out
    
    def test_format_as_json_single_record(self, capsys):
        """JSON formatter outputs valid JSON for single record."""
        import json
        records = [CostRecord(name="S3", amount=5.25, unit="USD", period="2024-01")]
        format_as_json(records)
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert data[0]["name"] == "S3"
        assert data[0]["amount"] == 5.25
    
    def test_format_as_csv_multiple_records(self, capsys):
        """CSV formatter outputs all records."""
        records = [
            CostRecord(name="EC2", amount=100.0, unit="USD", period="2024-01"),
            CostRecord(name="S3", amount=10.0, unit="USD", period="2024-01"),
        ]
        format_as_csv(records)
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert len(lines) == 3  # Header + 2 records
