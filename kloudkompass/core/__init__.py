# kloudkompass/core/__init__.py
# ---------------------------
# Exposes the main abstractions so other modules can do:
# from kloudkompass.core import CostProvider, get_cost_provider
# This keeps imports clean and provides a stable public interface.

from kloudkompass.core.cost_base import CostProvider
from kloudkompass.core.provider_factory import get_cost_provider, get_available_providers
from kloudkompass.core.exceptions import (
    KloudKompassError,
    CLIUnavailableError,
    CredentialError,
    PermissionDeniedError,
    PaginationError,
    ParsingError,
)
from kloudkompass.core.health import check_cli_installed, check_credentials

__all__ = [
    "CostProvider",
    "get_cost_provider",
    "get_available_providers",
    "KloudKompassError",
    "CLIUnavailableError",
    "CredentialError",
    "PermissionDeniedError",
    "PaginationError",
    "ParsingError",
    "check_cli_installed",
    "check_credentials",
]
