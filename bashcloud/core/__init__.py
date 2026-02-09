# bashcloud/core/__init__.py
# ---------------------------
# Exposes the main abstractions so other modules can do:
# from bashcloud.core import CostProvider, get_cost_provider
# This keeps imports clean and provides a stable public interface.

from bashcloud.core.cost_base import CostProvider
from bashcloud.core.provider_factory import get_cost_provider, get_available_providers
from bashcloud.core.exceptions import (
    BashCloudError,
    CLIUnavailableError,
    CredentialError,
    PermissionDeniedError,
    PaginationError,
    ParsingError,
)
from bashcloud.core.health import check_cli_installed, check_credentials

__all__ = [
    "CostProvider",
    "get_cost_provider",
    "get_available_providers",
    "BashCloudError",
    "CLIUnavailableError",
    "CredentialError",
    "PermissionDeniedError",
    "PaginationError",
    "ParsingError",
    "check_cli_installed",
    "check_credentials",
]
