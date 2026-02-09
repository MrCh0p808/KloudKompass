# bashcloud/utils/subprocess_helpers.py
# --------------------------------------
# all subprocess execution handling. This keeps the cloud modules clean
# and gives me one place to handle timeouts, errors, and output parsing.
# Every CLI call goes through these functions.

import subprocess
import json
from typing import List, Dict, Any, Optional

from bashcloud.core.exceptions import BashCloudError, ParsingError


# Default timeout for CLI commands in seconds
DEFAULT_TIMEOUT = 120


def run_cli_command(
    command: List[str],
    timeout: int = DEFAULT_TIMEOUT,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """
    Execute a CLI command and return the result.
    
    subprocess.run with capture_output ensures can access both stdout
    and stderr. The check parameter controls whether to raise on non-zero
    exit codes.
    
    Args:
        command: List of command parts, e.g. ["aws", "ce", "get-cost-and-usage"]
        timeout: How long to wait before killing the process
        check: If True, raise CalledProcessError on non-zero exit
        
    Returns:
        CompletedProcess with stdout, stderr, returncode
        
    Raises:
        subprocess.TimeoutExpired: If command takes too long
        subprocess.CalledProcessError: If check=True and command fails
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
        )
        return result
    except subprocess.TimeoutExpired:
        cmd_str = " ".join(command)
        raise BashCloudError(
            f"Command timed out after {timeout} seconds: {cmd_str}",
            suggestion="Try a smaller date range or check your network connection."
        )
    except subprocess.CalledProcessError as e:
        cmd_str = " ".join(command)
        stderr = e.stderr.strip() if e.stderr else "No error output"
        raise BashCloudError(
            f"Command failed: {cmd_str}\nError: {stderr}",
            suggestion="Check the command output above for details."
        )


def run_cli_json(
    command: List[str],
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Execute a CLI command and parse the JSON output.
    
    Most cloud CLIs support --output json. This for all data queries
    because JSON is easier to parse than tables and does not truncate.
    
    Args:
        command: Command list, should include output format flag if needed
        timeout: How long to wait
        
    Returns:
        Parsed JSON as a dictionary
        
    Raises:
        ParsingError: If output is not valid JSON
    """
    result = run_cli_command(command, timeout, check=True)
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise ParsingError(
            f"Failed to parse CLI output as JSON: {e}",
            raw_output=result.stdout[:500]  # Include first 500 chars for debugging
        )


def build_aws_command(
    service: str,
    operation: str,
    args: Optional[Dict[str, str]] = None,
    profile: Optional[str] = None,
    region: Optional[str] = None,
) -> List[str]:
    """
    Build an AWS CLI command with common options.
    
    Centralizes command building here so all AWS calls are consistent.
    Profile and region are optional overrides.
    
    Args:
        service: AWS service like "ce" or "ec2"  
        operation: API operation like "get-cost-and-usage"
        args: Additional arguments as key-value pairs
        profile: AWS profile name to use
        region: AWS region to use
        
    Returns:
        Complete command list ready for subprocess
    """
    command = ["aws", service, operation, "--output", "json"]
    
    if profile:
        command.extend(["--profile", profile])
    
    if region:
        command.extend(["--region", region])
    
    if args:
        for key, value in args.items():
            command.extend([f"--{key}", value])
    
    return command


def build_azure_command(
    service: str,
    operation: str,
    args: Optional[Dict[str, str]] = None,
) -> List[str]:
    """
    Build an Azure CLI command.
    
    Azure CLI uses 'az' as the base command with service and operation
    as subcommands.
    """
    command = ["az", service, operation, "--output", "json"]
    
    if args:
        for key, value in args.items():
            command.extend([f"--{key}", value])
    
    return command


def build_gcloud_command(
    service: str,
    operation: str,
    args: Optional[Dict[str, str]] = None,
    project: Optional[str] = None,
) -> List[str]:
    """
    Build a gcloud CLI command.
    
    GCP uses 'gcloud' as the base with service groups and operations.
    """
    command = ["gcloud", service, operation, "--format=json"]
    
    if project:
        command.extend(["--project", project])
    
    if args:
        for key, value in args.items():
            command.extend([f"--{key}", value])
    
    return command
