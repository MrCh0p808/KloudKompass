# tests/test_provider_factory.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 provider factory tests (20 tests).

import pytest
from unittest.mock import patch


class TestGetAvailableProviders:
    """Tests for get_available_providers()."""
    
    def test_returns_list(self):
        from kloudkompass.core.provider_factory import get_available_providers
        result = get_available_providers()
        assert isinstance(result, list)
    
    def test_contains_aws(self):
        from kloudkompass.core.provider_factory import get_available_providers
        assert "aws" in get_available_providers()
    
    def test_contains_azure(self):
        from kloudkompass.core.provider_factory import get_available_providers
        assert "azure" in get_available_providers()
    
    def test_contains_gcp(self):
        from kloudkompass.core.provider_factory import get_available_providers
        assert "gcp" in get_available_providers()
    
    def test_at_least_three_providers(self):
        from kloudkompass.core.provider_factory import get_available_providers
        assert len(get_available_providers()) >= 3


class TestIsProviderImplemented:
    """Tests for is_provider_implemented()."""
    
    def test_aws_is_implemented(self):
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("aws") is True
    
    def test_azure_is_implemented(self):
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("azure") is True
    
    def test_gcp_not_implemented(self):
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("gcp") is False
    
    def test_unknown_not_implemented(self):
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("oracle") is False
    
    def test_case_insensitive(self):
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("AWS") is True
    
    def test_whitespace_stripped(self):
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented(" aws ") is True


class TestGetCostProvider:
    """Tests for get_cost_provider()."""
    
    def test_unknown_provider_raises(self):
        from kloudkompass.core.provider_factory import get_cost_provider
        from kloudkompass.core.exceptions import KloudKompassError
        with pytest.raises(KloudKompassError):
            get_cost_provider("oracle")
    
    def test_error_mentions_valid_providers(self):
        from kloudkompass.core.provider_factory import get_cost_provider
        from kloudkompass.core.exceptions import KloudKompassError
        with pytest.raises(KloudKompassError) as exc_info:
            get_cost_provider("oracle")
        assert "aws" in str(exc_info.value).lower()


class TestRegisterProvider:
    """Tests for register_provider()."""
    
    def test_register_new_provider(self):
        from kloudkompass.core.provider_factory import register_provider, get_available_providers
        register_provider("oracle", "kloudkompass.oracle.OracleProvider")
        assert "oracle" in get_available_providers()
    
    def test_register_lowercase(self):
        from kloudkompass.core.provider_factory import register_provider, get_available_providers
        register_provider("IBM", "kloudkompass.ibm.IBMProvider")
        assert "ibm" in get_available_providers()
    
    def test_register_overwrite(self):
        from kloudkompass.core.provider_factory import register_provider, _COST_PROVIDER_REGISTRY
        register_provider("testprovider", "path.one")
        register_provider("testprovider", "path.two")
        assert _COST_PROVIDER_REGISTRY["testprovider"] == "path.two"


class TestProviderRegistry:
    """Tests for registry structure."""
    
    def test_registry_is_dict(self):
        from kloudkompass.core.provider_factory import _COST_PROVIDER_REGISTRY
        assert isinstance(_COST_PROVIDER_REGISTRY, dict)
    
    def test_aws_registry_path(self):
        from kloudkompass.core.provider_factory import _COST_PROVIDER_REGISTRY
        assert "AWSCostProvider" in _COST_PROVIDER_REGISTRY["aws"]
    
    def test_azure_registry_path(self):
        from kloudkompass.core.provider_factory import _COST_PROVIDER_REGISTRY
        assert "AzureCostProvider" in _COST_PROVIDER_REGISTRY["azure"]
    
    def test_gcp_registry_path(self):
        from kloudkompass.core.provider_factory import _COST_PROVIDER_REGISTRY
        assert "GCPCostProvider" in _COST_PROVIDER_REGISTRY["gcp"]
