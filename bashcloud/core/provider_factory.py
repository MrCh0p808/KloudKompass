# bashcloud/core/provider_factory.py
# -----------------------------------
# the factory pattern here used to get the right provider implementation
# without the CLI needing to import cloud-specific modules directly.
# Adding a new cloud provider is just: implement CostProvider, register here.

from typing import Dict, Type

from bashcloud.core.cost_base import CostProvider
from bashcloud.core.exceptions import BashCloudError


# Maintains a registry of available providers. Lazy imports happen when
# get_cost_provider is called, not at module load time. This keeps startup
# fast and avoids import errors if one provider's deps are missing.
_COST_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "bashcloud.aws.cost.AWSCostProvider",
    "azure": "bashcloud.azure.cost.AzureCostProvider",
    "gcp": "bashcloud.gcp.cost.GCPCostProvider",
}


def get_available_providers() -> list:
    """
    Return list of registered provider names.
    
    This to show valid options in help text and validation messages.
    """
    return list(_COST_PROVIDER_REGISTRY.keys())


def get_cost_provider(provider_name: str) -> CostProvider:
    """
    Factory function to get a cost provider by name.
    
    Lazy imports done here so that if someone only uses AWS, they do not
    need Azure SDK installed. The import only happens when you actually
    request that provider.
    
    Args:
        provider_name: One of "aws", "azure", "gcp" (case insensitive)
        
    Returns:
        An instance of the appropriate CostProvider subclass
        
    Raises:
        BashCloudError: If the provider is not recognized
    """
    name = provider_name.lower().strip()
    
    if name not in _COST_PROVIDER_REGISTRY:
        valid = ", ".join(get_available_providers())
        raise BashCloudError(
            f"Unknown provider: '{provider_name}'",
            suggestion=f"Valid providers are: {valid}"
        )
    
    # Lazy import the provider class
    module_path = _COST_PROVIDER_REGISTRY[name]
    module_name, class_name = module_path.rsplit(".", 1)
    
    try:
        import importlib
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class()
    except ImportError as e:
        raise BashCloudError(
            f"Failed to load {name} provider module",
            suggestion=f"Make sure all dependencies are installed: {e}"
        )
    except AttributeError:
        raise BashCloudError(
            f"Provider class {class_name} not found in {module_name}",
            suggestion="This is a bug in BashCloud. Please report it."
        )


def register_provider(name: str, class_path: str) -> None:
    """
    Register a new provider dynamically.
    
    Exposes this for plugin support. Third parties can implement their
    own CostProvider and register it at runtime.
    
    Args:
        name: Short name like "aws" or "oracle"
        class_path: Full dotted path like "myplugin.oracle.OracleCostProvider"
    """
    _COST_PROVIDER_REGISTRY[name.lower()] = class_path
