# tests/test_health_module.py
# ----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 health module tests (25 tests).

import pytest
from unittest.mock import patch, MagicMock


class TestCheckCliInstalled:
    """Tests for check_cli_installed()."""
    
    def test_function_exists(self):
        from kloudkompass.core.health import check_cli_installed
        assert check_cli_installed is not None
    
    @patch('kloudkompass.core.health.shutil.which')
    def test_returns_true_when_found(self, mock_which):
        from kloudkompass.core.health import check_cli_installed
        mock_which.return_value = "/usr/bin/aws"
        assert check_cli_installed("aws") is True
    
    @patch('kloudkompass.core.health.shutil.which')
    def test_returns_false_when_not_found(self, mock_which):
        from kloudkompass.core.health import check_cli_installed
        mock_which.return_value = None
        assert check_cli_installed("nonexistent") is False
    
    @patch('kloudkompass.core.health.shutil.which')
    def test_calls_which_with_cli_name(self, mock_which):
        from kloudkompass.core.health import check_cli_installed
        mock_which.return_value = None
        check_cli_installed("az")
        mock_which.assert_called_once_with("az")


class TestRequireCli:
    """Tests for require_cli()."""
    
    @patch('kloudkompass.core.health.check_cli_installed')
    def test_does_not_raise_when_installed(self, mock_check):
        from kloudkompass.core.health import require_cli
        mock_check.return_value = True
        require_cli("aws")  # Should not raise
    
    @patch('kloudkompass.core.health.check_cli_installed')
    def test_raises_when_missing(self, mock_check):
        from kloudkompass.core.health import require_cli
        from kloudkompass.core.exceptions import CLIUnavailableError
        mock_check.return_value = False
        with pytest.raises(CLIUnavailableError):
            require_cli("aws")


class TestGetInstallInstructions:
    """Tests for get_install_instructions()."""
    
    def test_aws_instructions(self):
        from kloudkompass.core.health import get_install_instructions
        result = get_install_instructions("aws")
        assert "aws configure" in result
    
    def test_az_instructions(self):
        from kloudkompass.core.health import get_install_instructions
        result = get_install_instructions("az")
        assert "az login" in result
    
    def test_gcloud_instructions(self):
        from kloudkompass.core.health import get_install_instructions
        result = get_install_instructions("gcloud")
        assert "gcloud" in result
    
    def test_unknown_cli_fallback(self):
        from kloudkompass.core.health import get_install_instructions
        result = get_install_instructions("kubectl")
        assert "kubectl" in result


class TestCheckCredentials:
    """Tests for check_credentials() dispatcher."""
    
    def test_unknown_provider_returns_error(self):
        from kloudkompass.core.health import check_credentials
        valid, error = check_credentials("oracle")
        assert valid is False
        assert "Unknown provider" in error
    
    @patch('kloudkompass.core.health.check_aws_credentials')
    def test_routes_to_aws(self, mock_aws):
        from kloudkompass.core.health import check_credentials
        mock_aws.return_value = (True, None)
        valid, error = check_credentials("aws")
        mock_aws.assert_called_once()
        assert valid is True
    
    @patch('kloudkompass.core.health.check_azure_credentials')
    def test_routes_to_azure(self, mock_azure):
        from kloudkompass.core.health import check_credentials
        mock_azure.return_value = (False, "Not logged in")
        valid, error = check_credentials("azure")
        mock_azure.assert_called_once()
    
    @patch('kloudkompass.core.health.check_gcp_credentials')
    def test_routes_to_gcp(self, mock_gcp):
        from kloudkompass.core.health import check_credentials
        mock_gcp.return_value = (False, "No active account")
        valid, error = check_credentials("gcp")
        mock_gcp.assert_called_once()


class TestRequireCredentials:
    """Tests for require_credentials()."""
    
    @patch('kloudkompass.core.health.check_credentials')
    def test_does_not_raise_when_valid(self, mock_check):
        from kloudkompass.core.health import require_credentials
        mock_check.return_value = (True, None)
        require_credentials("aws")  # Should not raise
    
    @patch('kloudkompass.core.health.check_credentials')
    def test_raises_when_invalid(self, mock_check):
        from kloudkompass.core.health import require_credentials
        from kloudkompass.core.exceptions import CredentialError
        mock_check.return_value = (False, "Invalid credentials")
        with pytest.raises(CredentialError):
            require_credentials("aws")


class TestAwsCredentials:
    """Tests for check_aws_credentials()."""
    
    @patch('kloudkompass.core.health.check_cli_installed')
    def test_fails_when_cli_missing(self, mock_cli):
        from kloudkompass.core.health import check_aws_credentials
        mock_cli.return_value = False
        valid, error = check_aws_credentials()
        assert valid is False
        assert "not installed" in error
    
    @patch('kloudkompass.core.health.subprocess.run')
    @patch('kloudkompass.core.health.check_cli_installed')
    def test_succeeds_on_zero_returncode(self, mock_cli, mock_run):
        from kloudkompass.core.health import check_aws_credentials
        mock_cli.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        valid, error = check_aws_credentials()
        assert valid is True
    
    @patch('kloudkompass.core.health.subprocess.run')
    @patch('kloudkompass.core.health.check_cli_installed')
    def test_detects_expired_credentials(self, mock_cli, mock_run):
        from kloudkompass.core.health import check_aws_credentials
        mock_cli.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stderr="token expired")
        valid, error = check_aws_credentials()
        assert valid is False
        assert "expired" in error.lower()
    
    @patch('kloudkompass.core.health.subprocess.run')
    @patch('kloudkompass.core.health.check_cli_installed')
    def test_handles_timeout(self, mock_cli, mock_run):
        import subprocess
        from kloudkompass.core.health import check_aws_credentials
        mock_cli.return_value = True
        mock_run.side_effect = subprocess.TimeoutExpired("aws", 30)
        valid, error = check_aws_credentials()
        assert valid is False
        assert "timed out" in error.lower()
