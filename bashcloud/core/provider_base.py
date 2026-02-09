# bashcloud/core/provider_base.py
# --------------------------------
# the abstract base definition that all cloud providers must implement.
# This is the contract that ensures AWS, Azure, and GCP modules all expose
# the same interface, making the CLI code clean and provider-agnostic.

from abc import ABC, abstractmethod
from typing import Optional


class ProviderBase(ABC):
    """
    Abstract base class for all cloud provider modules.
    
    Every provider (AWS, Azure, GCP) inherits from this and implements the
    required methods. The CLI talks to providers through this interface,
    so it never needs to know which specific provider it is using.
    """
    
    # Each subclass sets this to identify itself
    provider_name: str = "unknown"
    
    # The CLI command name for this provider (aws, az, gcloud)
    cli_command: str = "unknown"
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider's CLI is installed and configured.
        
        Returns True if the CLI is in PATH and credentials are set up.
        This to fail fast with a helpful message before attempting
        any actual API calls.
        """
        pass
    
    @abstractmethod
    def validate_credentials(self) -> bool:
        """
        Verify that credentials are valid and not expired.
        
        This makes a lightweight API call to confirm the credentials work.
        Better to catch expired creds early than halfway through a query.
        """
        pass
    
    def get_provider_name(self) -> str:
        """Return the human-readable provider name."""
        return self.provider_name
    
    def get_cli_command(self) -> str:
        """Return the CLI command for this provider."""
        return self.cli_command
