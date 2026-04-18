# tests/test_exceptions_module.py
# ---------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 exceptions module tests (15 tests).

import pytest


class TestKloudKompassError:
    """Tests for base KloudKompassError."""
    
    def test_exists(self):
        from kloudkompass.core.exceptions import KloudKompassError
        assert KloudKompassError is not None
    
    def test_is_exception(self):
        from kloudkompass.core.exceptions import KloudKompassError
        assert issubclass(KloudKompassError, Exception)
    
    def test_can_raise(self):
        from kloudkompass.core.exceptions import KloudKompassError
        with pytest.raises(KloudKompassError):
            raise KloudKompassError("test error")
    
    def test_message_preserved(self):
        from kloudkompass.core.exceptions import KloudKompassError
        try:
            raise KloudKompassError("test error")
        except KloudKompassError as e:
            assert "test error" in str(e)


class TestCLIUnavailableError:
    """Tests for CLIUnavailableError."""
    
    def test_exists(self):
        from kloudkompass.core.exceptions import CLIUnavailableError
        assert CLIUnavailableError is not None
    
    def test_is_kloudkompass_error(self):
        from kloudkompass.core.exceptions import CLIUnavailableError, KloudKompassError
        assert issubclass(CLIUnavailableError, KloudKompassError)
    
    def test_stores_cli_name(self):
        from kloudkompass.core.exceptions import CLIUnavailableError
        err = CLIUnavailableError("aws", "Install aws")
        assert err.cli_name == "aws"


class TestCredentialError:
    """Tests for CredentialError."""
    
    def test_exists(self):
        from kloudkompass.core.exceptions import CredentialError
        assert CredentialError is not None
    
    def test_is_kloudkompass_error(self):
        from kloudkompass.core.exceptions import CredentialError, KloudKompassError
        assert issubclass(CredentialError, KloudKompassError)
    
    def test_stores_provider(self):
        from kloudkompass.core.exceptions import CredentialError
        err = CredentialError("aws", "No credentials")
        assert err.provider == "aws"


class TestConfigurationError:
    """Tests for ConfigurationError."""
    
    def test_exists(self):
        from kloudkompass.core.exceptions import ConfigurationError
        assert ConfigurationError is not None
    
    def test_is_kloudkompass_error(self):
        from kloudkompass.core.exceptions import ConfigurationError, KloudKompassError
        assert issubclass(ConfigurationError, KloudKompassError)
    
    def test_stores_config_path(self):
        from kloudkompass.core.exceptions import ConfigurationError
        err = ConfigurationError("parse error", config_path="/path/to/config")
        assert err.config_path == "/path/to/config"
    
    def test_default_config_path_none(self):
        from kloudkompass.core.exceptions import ConfigurationError
        err = ConfigurationError("parse error")
        assert err.config_path is None
