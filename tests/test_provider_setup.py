# tests/test_provider_setup.py
# -----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 provider setup module tests.

import pytest
from unittest.mock import patch, MagicMock


class TestProviderSetupResult:
    """Tests for ProviderSetupResult dataclass."""
    
    def test_result_exists(self):
        """ProviderSetupResult should be importable."""
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        assert ProviderSetupResult is not None
    
    def test_result_success_field(self):
        """ProviderSetupResult should have success field."""
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        result = ProviderSetupResult(success=True, provider="aws")
        assert result.success is True
    
    def test_result_provider_field(self):
        """ProviderSetupResult should have provider field."""
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        result = ProviderSetupResult(success=True, provider="aws")
        assert result.provider == "aws"
    
    def test_result_error_field(self):
        """ProviderSetupResult should have error field."""
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        result = ProviderSetupResult(success=False, provider="aws", error="CLI not found")
        assert result.error == "CLI not found"
    
    def test_result_is_configured_true(self):
        """is_configured should be True when success and no error."""
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        result = ProviderSetupResult(success=True, provider="aws")
        assert result.is_configured is True
    
    def test_result_is_configured_false_on_error(self):
        """is_configured should be False when error present."""
        from kloudkompass.tui.provider_setup import ProviderSetupResult
        result = ProviderSetupResult(success=False, provider="aws", error="CLI not found")
        assert result.is_configured is False


class TestCheckProviderReady:
    """Tests for check_provider_ready() function."""
    
    def test_check_provider_ready_exists(self):
        """check_provider_ready should be importable."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        assert check_provider_ready is not None
    
    def test_unimplemented_provider_fails(self):
        """GCP should return failure with helpful message."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        
        result = check_provider_ready("gcp")
        assert result.success is False
        assert "not yet available" in result.error
        assert "AWS" in result.error
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    @patch('kloudkompass.tui.provider_setup.check_credentials')
    def test_aws_ready_when_configured(self, mock_creds, mock_cli):
        """AWS should succeed when CLI installed and creds valid."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        
        mock_cli.return_value = True
        mock_creds.return_value = (True, None)
        
        result = check_provider_ready("aws")
        assert result.success is True
        assert result.provider == "aws"
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    def test_aws_fails_when_cli_missing(self, mock_cli):
        """AWS should fail when CLI not installed."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        
        mock_cli.return_value = False
        
        result = check_provider_ready("aws")
        assert result.success is False
        assert "CLI not found" in result.error
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    @patch('kloudkompass.tui.provider_setup.check_credentials')
    def test_aws_fails_when_creds_invalid(self, mock_creds, mock_cli):
        """AWS should fail when credentials invalid."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        
        mock_cli.return_value = True
        mock_creds.return_value = (False, "No credentials configured")
        
        result = check_provider_ready("aws")
        assert result.success is False
        assert "credentials not configured" in result.error


class TestEnsureProviderConfigured:
    """Tests for ensure_provider_configured() function."""
    
    def test_ensure_exists(self):
        """ensure_provider_configured should be importable."""
        from kloudkompass.tui.provider_setup import ensure_provider_configured
        assert ensure_provider_configured is not None
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    @patch('kloudkompass.tui.provider_setup.check_credentials')
    def test_returns_success_when_ready(self, mock_creds, mock_cli):
        """Should return success immediately when provider ready."""
        from kloudkompass.tui.provider_setup import ensure_provider_configured
        
        mock_cli.return_value = True
        mock_creds.return_value = (True, None)
        
        result = ensure_provider_configured("aws", interactive=False)
        assert result.success is True
    
    def test_non_interactive_returns_failure(self):
        """Non-interactive mode should not run setup flow."""
        from kloudkompass.tui.provider_setup import ensure_provider_configured
        
        result = ensure_provider_configured("azure", interactive=False)
        assert result.success is False
        # Should not block
    
    def test_ensure_is_pure_gate(self):
        """ensure_provider_configured must be pure — no UI side effects."""
        from kloudkompass.tui.provider_setup import ensure_provider_configured
        import inspect
        source = inspect.getsource(ensure_provider_configured)
        assert 'input(' not in source
        assert 'print(' not in source


class TestGetSetupInstructions:
    """Tests for get_setup_instructions() pure function."""
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    @patch('kloudkompass.tui.provider_setup.check_credentials')
    def test_returns_dict(self, mock_creds, mock_cli):
        """Should return a dict with structured data."""
        from kloudkompass.tui.provider_setup import get_setup_instructions
        
        mock_cli.return_value = True
        mock_creds.return_value = (True, None)
        
        result = get_setup_instructions("aws")
        assert isinstance(result, dict)
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    @patch('kloudkompass.tui.provider_setup.check_credentials')
    def test_has_required_keys(self, mock_creds, mock_cli):
        """Should have all required keys."""
        from kloudkompass.tui.provider_setup import get_setup_instructions
        
        mock_cli.return_value = True
        mock_creds.return_value = (True, None)
        
        result = get_setup_instructions("aws")
        assert "provider" in result
        assert "cli_name" in result
        assert "cli_installed" in result
        assert "creds_valid" in result
        assert "config_steps" in result
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    def test_aws_cli_name(self, mock_cli):
        """AWS CLI name should be 'aws'."""
        from kloudkompass.tui.provider_setup import get_setup_instructions
        
        mock_cli.return_value = False
        
        result = get_setup_instructions("aws")
        assert result["cli_name"] == "aws"
    
    @patch('kloudkompass.tui.provider_setup.check_cli_installed')
    def test_config_steps_not_empty(self, mock_cli):
        """Config steps should not be empty."""
        from kloudkompass.tui.provider_setup import get_setup_instructions
        
        mock_cli.return_value = False
        
        result = get_setup_instructions("aws")
        assert len(result["config_steps"]) > 0


class TestPersistProviderChoice:
    """Tests for persist_provider_choice() function."""
    
    def test_persist_exists(self):
        """persist_provider_choice should be importable."""
        from kloudkompass.tui.provider_setup import persist_provider_choice
        assert persist_provider_choice is not None
    
    @patch('kloudkompass.tui.provider_setup.save_config')
    @patch('kloudkompass.tui.provider_setup.load_config')
    def test_persist_returns_true_on_success(self, mock_load, mock_save):
        """Should return True when config saves."""
        from kloudkompass.tui.provider_setup import persist_provider_choice
        
        mock_load.return_value = {}
        
        result = persist_provider_choice("aws")
        assert result is True
    
    @patch('kloudkompass.tui.provider_setup.load_config')
    def test_persist_returns_false_on_failure(self, mock_load):
        """Should return False when config fails."""
        from kloudkompass.tui.provider_setup import persist_provider_choice
        
        mock_load.side_effect = Exception("Disk error")
        
        result = persist_provider_choice("aws")
        assert result is False


class TestModulePurity:
    """Tests that provider_setup.py has zero input/print calls."""
    
    def test_no_input_calls(self):
        """provider_setup.py must not contain input() calls."""
        from kloudkompass.tui import provider_setup
        import inspect
        source = inspect.getsource(provider_setup)
        # Filter out comments and docstrings containing 'input'
        for line in source.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"') or stripped.startswith("'"):
                continue
            assert 'input(' not in stripped, f"Found input() in: {stripped}"
    
    def test_no_print_calls(self):
        """provider_setup.py must not contain print() calls."""
        from kloudkompass.tui import provider_setup
        import inspect
        source = inspect.getsource(provider_setup)
        for line in source.split('\n'):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"') or stripped.startswith("'"):
                continue
            assert 'print(' not in stripped, f"Found print() in: {stripped}"


class TestMulticloudUXHonesty:
    """Tests for multicloud UX messaging."""
    
    def test_azure_message_is_interactive(self):
        """Azure error should provide CLI instructions."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        
        result = check_provider_ready("azure")
        assert "az login" in result.error.lower() or "azure cli" in result.error.lower()
    
    def test_gcp_message_is_helpful(self):
        """GCP error should mention AWS as alternative."""
        from kloudkompass.tui.provider_setup import check_provider_ready
        
        result = check_provider_ready("gcp")
        assert "AWS" in result.error


class TestProviderFactory:
    """Tests for is_provider_implemented()."""
    
    def test_is_provider_implemented_exists(self):
        """is_provider_implemented should be importable."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented is not None
    
    def test_aws_is_implemented(self):
        """AWS should be implemented."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("aws") is True
    
    def test_azure_is_implemented(self):
        """Azure should be implemented."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("azure") is True
    
    def test_gcp_not_implemented(self):
        """GCP should not be implemented yet."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("gcp") is False
    
    def test_case_insensitive(self):
        """is_provider_implemented should be case insensitive."""
        from kloudkompass.core.provider_factory import is_provider_implemented
        assert is_provider_implemented("AWS") is True
        assert is_provider_implemented("Aws") is True
