import subprocess
import json
import shlex
import re
from typing import List, Dict, Any, Optional

from kloudkompass.core.exceptions import KloudKompassError, ParsingError


# Default timeout for CLI commands in seconds
DEFAULT_TIMEOUT = 120


def redact_command(command: List[str]) -> str:
    """
    Sanitize a command list for logging by quoting arguments correctly
    and redacting sensitive profiles or potential tokens.
    """
    if not command:
        return ""
    
    sanitized = []
    skip_next = False
    for arg in command:
        if skip_next:
            sanitized.append("[REDACTED]")
            skip_next = False
            continue
            
        if arg == "--profile":
            sanitized.append(arg)
            skip_next = True
            continue
            
        # Redact potential long hex tokens or keys (simple heuristic)
        if len(arg) >= 32 and re.match(r'^[a-fA-F0-9]+$', arg):
            sanitized.append("[TOKEN_REDACTED]")
            continue
            
        # Redact AKIA... Access Keys
        if re.search(r'AKIA[0-9A-Z]{16}', arg):
            arg = re.sub(r'AKIA[0-9A-Z]{16}', '[AWS_KEY_REDACTED]', arg)
            
        sanitized.append(arg)
        
    # Use shlex.join to create a copy-pasteable safe string (quotes arguments properly)
    return shlex.join(sanitized)


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
    """
    # Use shlex.join for the logged representation to prevent injection if the
    # log is copied/pasted into a terminal.
    safe_cmd_log = redact_command(command)
    
    try:
        # Note: shell=False is the default, which is critical for security.
        # Arguments are passed as a list directly to the OS exec call.
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check,
        )
        return result
    except subprocess.TimeoutExpired:
        raise KloudKompassError(
            f"Command timed out after {timeout} seconds: {safe_cmd_log}",
            suggestion="Try a smaller date range or check your network connection."
        )
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.strip() if e.stderr else "No error output"
        raise KloudKompassError(
            f"Command failed: {safe_cmd_log}\nError: {stderr}",
            suggestion="Check the command output above for details."
        )


def run_cli_json(
    command: List[str],
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Execute a CLI command and parse the JSON output, utilizing a local disk cache
    for read-only operations to achieve instant dashboard booting.
    """
    from kloudkompass.core.cache_manager import get_cache, set_cache
    import hashlib
    
    # Use shlex.join for consistent hashing and redact_command for logging
    cmd_raw = shlex.join(command)
    cmd_log = redact_command(command)
    cmd_lower = cmd_raw.lower()
    
    # Only cache read operations to prevent caching destructive state changes.
    is_read_only = any(read_verb in cmd_lower for read_verb in [
        "describe", "get", "list", "show"
    ])
    
    cache_key = None
    if is_read_only:
        from kloudkompass.config_manager import get_config_value
        ttl = get_config_value("cache_ttl_seconds", 300)
        
        cache_key = "cli_" + hashlib.sha256(cmd_raw.encode()).hexdigest()[:16]  # L2 FIX: sha256 over md5
        cached_data = get_cache(cache_key, max_age_seconds=ttl)
        if cached_data is not None:
            return cached_data

    # Cache miss or write operation - proceed with execution
    try:
        result = run_cli_command(command, timeout, check=True)
    except KloudKompassError as base_err:
        # OFFLINE MODE FALLBACK: If the network or CLI fails, try to load stale cache
        if is_read_only and cache_key:
            import logging
            logging.getLogger('kloudkompass').warning(f"Network error, falling back to offline cache for {cmd_log}")
            
            # Fetch cache ignoring the TTL limit
            stale_data = get_cache(cache_key, max_age_seconds=float('inf'))
            if stale_data is not None:
                return stale_data
                
        # If write operation or no cache exists, we cannot recover
        raise base_err
    
    try:
        parsed_data = json.loads(result.stdout)
        
        # Save to cache if it was a read op and parsing succeeded
        if is_read_only and cache_key:
            set_cache(cache_key, parsed_data)
            
        return parsed_data
    except json.JSONDecodeError as e:
        raise ParsingError(
            f"Failed to parse CLI output as JSON: {e}",
            raw_output=result.stdout[:500] 
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
