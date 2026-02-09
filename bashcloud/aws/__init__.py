# bashcloud/aws/__init__.py
# --------------------------
# Exposes the main AWS classes for convenience.
# Other modules can do: from bashcloud.aws import AWSCostProvider

from bashcloud.aws.cost import AWSCostProvider

__all__ = [
    "AWSCostProvider",
]
