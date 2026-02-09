# bashcloud/infra/__init__.py
# ----------------------------
# Centralized all infrastructure concerns. Providers use this layer
# instead of calling subprocess directly. This makes testing easier and
# keeps providers focused on business logic.

from bashcloud.infra.cli_adapter import CLIAdapter, CLIResult
from bashcloud.infra.cache import ResultCache, cache_result

__all__ = [
    "CLIAdapter",
    "CLIResult",
    "ResultCache",
    "cache_result",
]
