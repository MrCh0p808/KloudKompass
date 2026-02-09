# bashcloud/infra/__init__.py
# ----------------------------
# I centralize all infrastructure concerns here. Providers use this layer
# instead of calling subprocess directly. Makes testing easier and keeps
# providers focused on business logic.

from bashcloud.infra.cli_adapter import CLIAdapter, CLIResult
from bashcloud.infra.cache import ResultCache, cache_result
from bashcloud.infra.base_adapter import BaseCloudAdapter
from bashcloud.infra.aws_cli_adapter import AWSCLIAdapter, get_aws_cli_adapter

__all__ = [
    "CLIAdapter",
    "CLIResult",
    "ResultCache",
    "cache_result",
    "BaseCloudAdapter",
    "AWSCLIAdapter",
    "get_aws_cli_adapter",
]
