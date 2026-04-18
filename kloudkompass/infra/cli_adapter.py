# kloudkompass/infra/cli_adapter.py
# -------------------------------
# subprocess execution abstraction so providers never call subprocess
# directly. This gives me a single place to handle errors, timeouts, and
# logging. It also makes the code much easier to test with mocks.

import subprocess
import json
import shutil
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from kloudkompass.core.exceptions import (
    KloudKompassError,
    CLIUnavailableError,
    ParsingError,
)
from kloudkompass.utils.logger import debug
from kloudkompass.utils.subprocess_helpers import redact_command


@dataclass
class CLIResult:
    """
    Result of a CLI command execution.
    
    Wraps raw subprocess result to
    normalize the output and add convenience methods.
    """
    command: List[str]
    returncode: int
    stdout: str
    stderr: str
    
    @property
    def success(self) -> bool:
        """True if command exited with zero."""
        return self.returncode == 0
    
    def json(self) -> Dict[str, Any]:
        """Parse stdout as JSON."""
        try:
            return json.loads(self.stdout)
        except json.JSONDecodeError as e:
            raise ParsingError(
                f"Failed to parse CLI output as JSON: {e}",
                raw_output=self.stdout[:500]
            )


class CLIAdapter:
    """
    Adapter for executing cloud CLI commands.
    
    Providers use this instead of subprocess directly. Handles all the
    common concerns: checking CLI availability, timeouts, error wrapping,
    and JSON parsing.
    """
    
    # Default timeout in seconds
    DEFAULT_TIMEOUT = 120
    
    def __init__(self, cli_name: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Create an adapter for a specific CLI.
        
        Args:
            cli_name: The CLI executable name (aws, az, gcloud)
            timeout: Default timeout for commands
        """
        self.cli_name = cli_name
        self.timeout = timeout
    
    def is_available(self) -> bool:
        """Check if the CLI is installed and in PATH."""
        return shutil.which(self.cli_name) is not None
    
    def require_available(self) -> None:
        """Raise CLIUnavailableError if CLI is not installed."""
        if not self.is_available():
            raise CLIUnavailableError(self.cli_name)
    
    def run(
        self,
        args: List[str],
        timeout: Optional[int] = None,
        check: bool = False,
    ) -> CLIResult:
        """
        Execute a CLI command.
        
        Args:
            args: Command arguments (without the CLI name)
            timeout: Override default timeout
            check: If True, raise on non-zero exit
            
        Returns:
            CLIResult with command output
        """
        command = [self.cli_name] + args
        effective_timeout = timeout or self.timeout
        
        safe_cmd_log = redact_command(command)
        debug(f"Executing: {safe_cmd_log}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
            )
            
            cli_result = CLIResult(
                command=command,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )
            
            if check and not cli_result.success:
                raise KloudKompassError(
                    f"Command failed: {safe_cmd_log}\n{result.stderr}",
                    suggestion="Check the error message above."
                )
            
            return cli_result
            
        except subprocess.TimeoutExpired:
            raise KloudKompassError(
                f"Command timed out after {effective_timeout}s: {safe_cmd_log}",
                suggestion="Try a smaller date range or check your network."
            )
    
    def run_json(
        self,
        args: List[str],
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute command and parse JSON output.
        
        Convenience method that runs the command and parses the result.
        """
        result = self.run(args, timeout, check=True)
        return result.json()


# Pre-configured adapters for each cloud
def get_aws_adapter() -> CLIAdapter:
    """Get adapter for AWS CLI."""
    return CLIAdapter("aws")


def get_azure_adapter() -> CLIAdapter:
    """Get adapter for Azure CLI."""
    return CLIAdapter("az")


def get_gcp_adapter() -> CLIAdapter:
    """Get adapter for Google Cloud SDK."""
    return CLIAdapter("gcloud")
