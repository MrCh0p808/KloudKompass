# tests/test_multicloud_ux.py
# ---------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 multicloud UX honesty tests.

import pytest
from unittest.mock import patch, MagicMock
import inspect


class TestProviderImplementationStatus:
    """Tests for provider implementation status."""
    
    def test_aws_available(self):
        """AWS should be available for use."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("aws") is True
    
    def test_azure_coming_soon(self):
        """Azure should be marked as coming soon."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("azure") is False
    
    def test_gcp_coming_soon(self):
        """GCP should be marked as coming soon."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("gcp") is False


class TestProviderSelectionBlocking:
    """Tests that unimplemented providers are blocked."""
    
    def test_azure_selection_blocked_in_prompts(self):
        """Azure selection should be blocked with helpful message."""
        from kloudkompass.tui import prompts
        source = inspect.getsource(prompts.select_provider)
        assert 'is_provider_implemented' in source
    
    def test_coming_soon_message_shown(self):
        """Coming soon message should be shown in provider list."""
        from kloudkompass.tui import prompts
        source = inspect.getsource(prompts.select_provider)
        assert 'Coming soon' in source


class TestMulticloudMessaging:
    """Tests for multicloud messaging quality."""
    
    def test_azure_message_not_generic(self):
        """Azure error should not be generic 'not implemented'."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("azure")
        assert "not implemented" not in result.error.lower()
        assert "not yet available" in result.error.lower()
    
    def test_azure_message_mentions_alternative(self):
        """Azure error should mention AWS as alternative."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("azure")
        assert "AWS" in result.error
    
    def test_gcp_message_not_generic(self):
        """GCP error should not be generic 'not implemented'."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("gcp")
        assert "not implemented" not in result.error.lower()
    
    def test_gcp_message_mentions_alternative(self):
        """GCP error should mention AWS as alternative."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        result = check_provider_ready("gcp")
        assert "AWS" in result.error


class TestProviderListShowsStatus:
    """Tests that provider list shows implementation status."""
    
    def test_prompt_shows_coming_soon_for_azure(self):
        """Provider prompt should show Coming soon for Azure."""
        from kloudkompass.tui import prompts
        source = inspect.getsource(prompts.select_provider)
        assert 'Coming soon' in source
    
    def test_prompt_checks_implementation(self):
        """Provider prompt should check is_provider_implemented."""
        from kloudkompass.tui import prompts
        source = inspect.getsource(prompts.select_provider)
        assert 'is_provider_implemented' in source


class TestConsistentBehavior:
    """Tests for consistent behavior across TUI and CLI."""
    
    def test_is_provider_implemented_used_in_prompts(self):
        """prompts.py should use is_provider_implemented."""
        from kloudkompass.tui import prompts
        source = inspect.getsource(prompts)
        assert 'from kloudkompass.core.provider_factory import' in source
        assert 'is_provider_implemented' in source
    
    def test_is_provider_implemented_used_in_provider_setup(self):
        """provider_setup.py should use is_provider_implemented."""
        from kloudkompass.tui import provider_setup
        source = inspect.getsource(provider_setup)
        assert 'is_provider_implemented' in source


class TestProviderListOrder:
    """Tests for provider list ordering."""
    
    def test_aws_first_in_list(self):
        """AWS should be first or prominently placed."""
        from kloudkompass.core.provider_factory import get_available_providers
        providers = get_available_providers()
        # AWS should be in the list
        assert "aws" in providers
    
    def test_all_providers_listed(self):
        """All registered providers should be listed."""
        from kloudkompass.core.provider_factory import get_available_providers
        providers = get_available_providers()
        assert "aws" in providers
        assert "azure" in providers
        assert "gcp" in providers
