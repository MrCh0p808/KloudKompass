# kloudkompass/infra/base_adapter.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Abstract interface for cloud-specific adapters.
# Each cloud (AWS, Azure, GCP) implements this to standardize how
# we interact with their respective CLI tools.

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from kloudkompass.infra.cli_adapter import CLIAdapter, CLIResult


class BaseCloudAdapter(ABC):
    """
    Abstract base class for cloud CLI adapters.
    
    Provides a consistent interface for cloud-specific operations.
    Subclasses implement the details for each cloud provider.
    """
    
    # Subclasses should set these
    CLI_NAME: str = ""
    PAGE_TOKEN_KEY: str = "NextPageToken"
    
    def __init__(self, timeout: int = 120):
        """Initialize with a CLI adapter."""
        self._adapter = CLIAdapter(self.CLI_NAME, timeout=timeout)
        self._page_count: int = 0
    
    @property
    def page_count(self) -> int:
        """Number of pages fetched in last paginated call."""
        return self._page_count
    
    def is_available(self) -> bool:
        """Check if the cloud CLI is installed."""
        return self._adapter.is_available()
    
    def require_available(self) -> None:
        """Raise CLIUnavailableError if CLI not installed."""
        self._adapter.require_available()
    
    def run_command(
        self,
        args: List[str],
        check: bool = True,
    ) -> CLIResult:
        """
        Execute a CLI command.
        
        Delegates to the underlying CLIAdapter for subprocess handling.
        """
        return self._adapter.run(args, check=check)
    
    def run_json(self, args: List[str]) -> Dict[str, Any]:
        """Execute command and parse JSON output."""
        return self._adapter.run_json(args)
    
    @abstractmethod
    def get_cli_version(self) -> Optional[str]:
        """
        Get the CLI version string.
        
        Used for compatibility checks in doctor command.
        """
        pass
    
    @abstractmethod
    def check_credentials(self) -> tuple[bool, Optional[str]]:
        """
        Check if credentials are configured and valid.
        
        Returns (is_valid, error_message).
        """
        pass
