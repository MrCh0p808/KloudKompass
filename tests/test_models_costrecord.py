# tests/test_models_costrecord.py
# --------------------------------
# I test the CostRecord model including from_dict validation and
# to_dict serialization.

import pytest
from bashcloud.core.models import CostRecord


class TestCostRecordToDict:
    """Tests for CostRecord.to_dict method."""
    
    def test_to_dict_returns_primitives(self):
        """to_dict returns dictionary with primitive values."""
        record = CostRecord(
            name="EC2",
            amount=100.50,
            unit="USD",
            period="2024-01",
        )
        result = record.to_dict()
        
        assert result == {
            "name": "EC2",
            "amount": 100.50,
            "unit": "USD",
            "period": "2024-01",
        }
        assert isinstance(result["name"], str)
        assert isinstance(result["amount"], float)
    
    def test_to_dict_serializable_to_json(self):
        """to_dict output can be serialized to JSON."""
        import json
        record = CostRecord(name="S3", amount=5.0, unit="USD", period="2024-02")
        result = record.to_dict()
        
        # I verify no exception on json.dumps
        json_str = json.dumps(result)
        assert "S3" in json_str


class TestCostRecordFromDict:
    """Tests for CostRecord.from_dict class method."""
    
    def test_from_dict_valid_input(self):
        """from_dict creates record from valid dictionary."""
        data = {
            "name": "Lambda",
            "amount": 25.75,
            "unit": "USD",
            "period": "2024-03",
        }
        record = CostRecord.from_dict(data)
        
        assert record.name == "Lambda"
        assert record.amount == 25.75
        assert record.unit == "USD"
        assert record.period == "2024-03"
    
    def test_from_dict_normalizes_string_amount(self):
        """from_dict converts string amount to float."""
        data = {
            "name": "RDS",
            "amount": "150.25",  # String from API
            "unit": "USD",
            "period": "2024-01",
        }
        record = CostRecord.from_dict(data)
        
        assert record.amount == 150.25
        assert isinstance(record.amount, float)
    
    def test_from_dict_missing_name_raises(self):
        """from_dict raises ValueError when name is missing."""
        data = {"amount": 100.0, "unit": "USD", "period": "2024-01"}
        
        with pytest.raises(ValueError) as exc_info:
            CostRecord.from_dict(data)
        
        assert "name" in str(exc_info.value)
    
    def test_from_dict_missing_amount_raises(self):
        """from_dict raises ValueError when amount is missing."""
        data = {"name": "EC2", "unit": "USD", "period": "2024-01"}
        
        with pytest.raises(ValueError) as exc_info:
            CostRecord.from_dict(data)
        
        assert "amount" in str(exc_info.value)
    
    def test_from_dict_missing_unit_raises(self):
        """from_dict raises ValueError when unit is missing."""
        data = {"name": "EC2", "amount": 100.0, "period": "2024-01"}
        
        with pytest.raises(ValueError) as exc_info:
            CostRecord.from_dict(data)
        
        assert "unit" in str(exc_info.value)
    
    def test_from_dict_missing_period_raises(self):
        """from_dict raises ValueError when period is missing."""
        data = {"name": "EC2", "amount": 100.0, "unit": "USD"}
        
        with pytest.raises(ValueError) as exc_info:
            CostRecord.from_dict(data)
        
        assert "period" in str(exc_info.value)
    
    def test_from_dict_invalid_amount_raises(self):
        """from_dict raises ValueError when amount cannot be converted."""
        data = {
            "name": "EC2",
            "amount": "not-a-number",
            "unit": "USD",
            "period": "2024-01",
        }
        
        with pytest.raises(ValueError) as exc_info:
            CostRecord.from_dict(data)
        
        assert "amount" in str(exc_info.value).lower()
    
    def test_from_dict_non_dict_raises(self):
        """from_dict raises ValueError for non-dict input."""
        with pytest.raises(ValueError) as exc_info:
            CostRecord.from_dict(["not", "a", "dict"])
        
        assert "dict" in str(exc_info.value).lower()
    
    def test_from_dict_none_raises(self):
        """from_dict raises ValueError for None input."""
        with pytest.raises(ValueError):
            CostRecord.from_dict(None)


class TestCostRecordRoundTrip:
    """Tests for to_dict/from_dict round trip."""
    
    def test_round_trip_preserves_data(self):
        """Converting to dict and back preserves all data."""
        original = CostRecord(
            name="DynamoDB",
            amount=42.42,
            unit="USD",
            period="2024-06",
        )
        
        as_dict = original.to_dict()
        restored = CostRecord.from_dict(as_dict)
        
        assert restored.name == original.name
        assert restored.amount == original.amount
        assert restored.unit == original.unit
        assert restored.period == original.period
