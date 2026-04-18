# kloudkompass/utils/exports.py
# ---------------------------
# all file exports handling. The cloud modules return CostRecord lists
# and the CLI calls these functions to write to CSV or JSON files.

import csv
import json
import os
from typing import List, Any
from pathlib import Path

from kloudkompass.core.cost_base import CostRecord
from kloudkompass.core.exceptions import ExportError


def export_to_csv(
    records: List[CostRecord],
    output_path: str,
    include_header: bool = True,
) -> str:
    """
    Export cost records to a CSV file.
    
    the standard csv module used to handle quoting and escaping properly.
    The output path is returned so the caller can display it.
    
    Args:
        records: List of CostRecord objects
        output_path: Where to write the file
        include_header: Whether to write column headers
        
    Returns:
        Absolute path to the written file
        
    Raises:
        ExportError: If writing fails
    """
    try:
        # Expand user home directory if path starts with ~
        full_path = os.path.expanduser(output_path)
        
        # Create parent directories if they do not exist
        parent = Path(full_path).parent
        parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if include_header:
                writer.writerow(["Name", "Amount", "Unit", "Period"])
            
            for record in records:
                writer.writerow([
                    record.name,
                    record.amount,
                    record.unit,
                    record.period,
                ])
        
        return os.path.abspath(full_path)
        
    except PermissionError:
        raise ExportError(
            f"Permission denied writing to {output_path}",
            path=output_path
        )
    except OSError as e:
        raise ExportError(
            f"Failed to write CSV: {e}",
            path=output_path
        )


def export_to_json(
    records: List[CostRecord],
    output_path: str,
    pretty: bool = True,
) -> str:
    """
    Export cost records to a JSON file.
    
    the to_dict method on CostRecord used to get a clean dictionary
    representation. Pretty printing is on by default for readability.
    
    Args:
        records: List of CostRecord objects
        output_path: Where to write the file
        pretty: If True, indent the JSON for readability
        
    Returns:
        Absolute path to the written file
        
    Raises:
        ExportError: If writing fails
    """
    try:
        full_path = os.path.expanduser(output_path)
        
        parent = Path(full_path).parent
        parent.mkdir(parents=True, exist_ok=True)
        
        data = [record.to_dict() for record in records]
        
        with open(full_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2)
            else:
                json.dump(data, f)
        
        return os.path.abspath(full_path)
        
    except PermissionError:
        raise ExportError(
            f"Permission denied writing to {output_path}",
            path=output_path
        )
    except OSError as e:
        raise ExportError(
            f"Failed to write JSON: {e}",
            path=output_path
        )


def export_records(
    records: List[CostRecord],
    output_path: str,
    format: str = "csv",
) -> str:
    """
    Export records in the specified format.
    
    Convenience function that routes to the appropriate exporter
    based on the format argument.
    """
    format = format.lower()
    
    if format == "csv":
        return export_to_csv(records, output_path)
    elif format == "json":
        return export_to_json(records, output_path)
    else:
        raise ValueError(f"Unknown export format: {format}. Use 'csv' or 'json'.")


def generate_default_filename(prefix: str, format: str) -> str:
    """
    Generate a default filename with timestamp.
    
    This when the user does not specify an output path.
    Format: kloudkompass_cost_2024-01-15_143022.csv
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return f"kloudkompass_{prefix}_{timestamp}.{format}"
