# kloudkompass/azure/__init__.py
# ----------------------------
# Azure module exports. Follows the same pattern as AWS.

from kloudkompass.azure.cost import AzureCostProvider

__all__ = [
    "AzureCostProvider",
]
