# kloudkompass/core/provider_factory.py
# -----------------------------------
# Factory pattern for all provider types. Each domain (cost, compute,
# network, storage, IAM, database, security) has its own registry and
# factory function. Lazy imports keep startup fast.

from typing import Dict

from kloudkompass.core.exceptions import KloudKompassError


# ──────────────────────────────────────────────────────────
# Provider registries — lazy import paths
# ──────────────────────────────────────────────────────────

_COST_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.cost.AWSCostProvider",
    "azure": "kloudkompass.azure.cost.AzureCostProvider",
    "gcp": "kloudkompass.gcp.cost.GCPCostProvider",
}

_COMPUTE_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.compute.AWSComputeProvider",
    "azure": "kloudkompass.azure.compute.AzureComputeProvider",
    "gcp": "kloudkompass.gcp.compute.GCPComputeProvider",
}

_NETWORK_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.networking.AWSNetworkProvider",
    "azure": "kloudkompass.azure.networking.AzureNetworkProvider",
    "gcp": "kloudkompass.gcp.networking.GCPNetworkProvider",
}

_STORAGE_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.storage.AWSStorageProvider",
    "azure": "kloudkompass.azure.storage.AzureStorageProvider",
    "gcp": "kloudkompass.gcp.storage.GCPStorageProvider",
}

_IAM_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.iam.AWSIAMProvider",
    "azure": "kloudkompass.azure.iam.AzureIAMProvider",
    "gcp": "kloudkompass.gcp.iam.GCPIAMProvider",
}

_DATABASE_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.database.AWSDatabaseProvider",
    "azure": "kloudkompass.azure.database.AzureDatabaseProvider",
    "gcp": "kloudkompass.gcp.database.GCPDatabaseProvider",
}

_SECURITY_PROVIDER_REGISTRY: Dict[str, str] = {
    "aws": "kloudkompass.aws.security.AWSSecurityProvider",
    "azure": "kloudkompass.azure.security.AzureSecurityProvider",
    "gcp": "kloudkompass.gcp.security.GCPSecurityProvider",
}


# ──────────────────────────────────────────────────────────
# Implementation status
# ──────────────────────────────────────────────────────────

# Phase 3: Only AWS is fully implemented for all domains.
# Cost was phase 2, compute/network/storage/iam/db/security are phase 3.
# Phase 8: Azure Cost Data Integration natively implemented.
_IMPLEMENTED_PROVIDERS = {"aws", "azure"}


def is_provider_implemented(provider_name: str) -> bool:
    """
    Check if a provider is fully implemented.

    Azure and GCP are registered but not yet implemented.
    Returns True only for providers that can actually execute queries.
    """
    return provider_name.lower().strip() in _IMPLEMENTED_PROVIDERS


def get_available_providers() -> list:
    """Return list of registered provider names."""
    return list(_COST_PROVIDER_REGISTRY.keys())


# ──────────────────────────────────────────────────────────
# Generic factory helper
# ──────────────────────────────────────────────────────────

def _get_provider(provider_name: str, registry: Dict[str, str], domain: str):
    """
    Generic factory that lazy-imports a provider from a registry.

    Args:
        provider_name: "aws", "azure", or "gcp"
        registry: The domain-specific registry dict
        domain: Human-readable domain name for error messages

    Returns:
        An instance of the provider class

    Raises:
        KloudKompassError: If the provider is not recognized or import fails
    """
    name = provider_name.lower().strip()

    if name not in registry:
        valid = ", ".join(registry.keys())
        raise KloudKompassError(
            f"Unknown provider: '{provider_name}'",
            suggestion=f"Valid providers for {domain} are: {valid}"
        )

    module_path = registry[name]
    module_name, class_name = module_path.rsplit(".", 1)

    try:
        import importlib
        module = importlib.import_module(module_name)
        provider_class = getattr(module, class_name)
        return provider_class()
    except ImportError as e:
        raise KloudKompassError(
            f"Failed to load {name} {domain} provider module",
            suggestion=f"Make sure all dependencies are installed: {e}"
        )
    except AttributeError:
        raise KloudKompassError(
            f"Provider class {class_name} not found in {module_name}",
            suggestion="This is a bug in Kloud Kompass. Please report it."
        )


# ──────────────────────────────────────────────────────────
# Domain-specific factory functions
# ──────────────────────────────────────────────────────────

def get_cost_provider(provider_name: str):
    """Get a CostProvider instance by name."""
    return _get_provider(provider_name, _COST_PROVIDER_REGISTRY, "cost")


def get_compute_provider(provider_name: str):
    """Get a ComputeProvider instance by name."""
    return _get_provider(provider_name, _COMPUTE_PROVIDER_REGISTRY, "compute")


def get_network_provider(provider_name: str):
    """Get a NetworkProvider instance by name."""
    return _get_provider(provider_name, _NETWORK_PROVIDER_REGISTRY, "network")


def get_storage_provider(provider_name: str):
    """Get a StorageProvider instance by name."""
    return _get_provider(provider_name, _STORAGE_PROVIDER_REGISTRY, "storage")


def get_iam_provider(provider_name: str):
    """Get an IAMProvider instance by name."""
    return _get_provider(provider_name, _IAM_PROVIDER_REGISTRY, "iam")


def get_database_provider(provider_name: str):
    """Get a DatabaseProvider instance by name."""
    return _get_provider(provider_name, _DATABASE_PROVIDER_REGISTRY, "database")


def get_security_provider(provider_name: str):
    """Get a SecurityProvider instance by name."""
    return _get_provider(provider_name, _SECURITY_PROVIDER_REGISTRY, "security")


def register_provider(name: str, class_path: str, domain: str = "cost") -> None:
    """
    Register a new provider dynamically.

    For plugin support. Third parties can implement their own providers.

    Args:
        name: Short name like "aws" or "oracle"
        class_path: Full dotted path like "myplugin.oracle.OracleCostProvider"
        domain: Which registry to add to (cost, compute, network, etc.)
    """
    registries = {
        "cost": _COST_PROVIDER_REGISTRY,
        "compute": _COMPUTE_PROVIDER_REGISTRY,
        "network": _NETWORK_PROVIDER_REGISTRY,
        "storage": _STORAGE_PROVIDER_REGISTRY,
        "iam": _IAM_PROVIDER_REGISTRY,
        "database": _DATABASE_PROVIDER_REGISTRY,
        "security": _SECURITY_PROVIDER_REGISTRY,
    }
    registry = registries.get(domain.lower())
    if registry is None:
        valid = ", ".join(registries.keys())
        raise ValueError(f"Unknown domain '{domain}'. Valid: {valid}")
    registry[name.lower()] = class_path

def get_provider_list() -> list:
    """Return list of all registered provider keys (aws, azure, gcp)."""
    return list(_COST_PROVIDER_REGISTRY.keys())
