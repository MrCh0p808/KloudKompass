# kloudkompass/aws/__init__.py
# --------------------------
# Exposes the main AWS classes for convenience.
# Other modules can do: from kloudkompass.aws import AWSCostProvider

from kloudkompass.aws.cost import AWSCostProvider

__all__ = [
    "AWSCostProvider",
]
