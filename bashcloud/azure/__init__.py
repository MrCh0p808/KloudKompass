# bashcloud/azure/__init__.py
# ----------------------------
# Azure module exports. Follows the same pattern as AWS.

from bashcloud.azure.cost import AzureCostProvider

__all__ = [
    "AzureCostProvider",
]
