# kloudkompass/infra/__init__.py
# ----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Infrastructure layer: CLI execution, caching, and cloud adapters.

from kloudkompass.infra.cli_adapter import CLIAdapter, CLIResult
from kloudkompass.infra.cache import ResultCache, cache_result
from kloudkompass.infra.base_adapter import BaseCloudAdapter
from kloudkompass.infra.aws_cli_adapter import AWSCLIAdapter, get_aws_cli_adapter

__all__ = [
    "CLIAdapter",
    "CLIResult",
    "ResultCache",
    "cache_result",
    "BaseCloudAdapter",
    "AWSCLIAdapter",
    "get_aws_cli_adapter",
]
