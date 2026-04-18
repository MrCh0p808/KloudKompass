# tests/test_region_gate.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Region gate + session auto-load tests.

import pytest
from unittest.mock import patch, MagicMock


def _fresh_session(**kwargs):
    """Create a fresh SessionState without triggering config load."""
    from kloudkompass.tui.session import SessionState
    return SessionState(**kwargs)


# ────────────────────────────────────────────────────
#  Pure check: check_region_configured
# ────────────────────────────────────────────────────

class TestCheckRegionConfigured:
    """Tests for the pure check_region_configured function."""

    def test_returns_success_when_session_has_region(self):
        """If session already has a region, return success immediately."""
        from kloudkompass.tui.provider_setup import check_region_configured
        session = _fresh_session(provider="aws", region="us-east-1")
        result = check_region_configured(session)
        assert result.success is True
        assert result.region == "us-east-1"

    def test_returns_config_region_when_session_empty(self):
        """If session has no region but config does, use config."""
        from kloudkompass.tui.provider_setup import check_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config",
                    return_value={"default_region": "eu-west-1"}):
            with patch("kloudkompass.tui.session.update_session"):
                result = check_region_configured(session)

        assert result.success is True
        assert result.region == "eu-west-1"

    def test_returns_needs_prompt_when_no_region_anywhere(self):
        """If no region in session or config, return needs_prompt=True."""
        from kloudkompass.tui.provider_setup import check_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
            result = check_region_configured(session)

        assert result.success is False
        assert result.needs_prompt is True
        assert result.region == ""

    def test_does_not_call_print_or_input(self):
        """Pure function should never call print() or input()."""
        from kloudkompass.tui.provider_setup import check_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
            with patch("builtins.print") as mock_print:
                with patch("builtins.input") as mock_input:
                    check_region_configured(session)

        mock_print.assert_not_called()
        mock_input.assert_not_called()

    def test_updates_session_when_config_has_region(self):
        """Should call update_session when loading region from config."""
        from kloudkompass.tui.provider_setup import check_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config",
                    return_value={"default_region": "ap-south-1"}):
            with patch("kloudkompass.tui.session.update_session") as mock_update:
                check_region_configured(session)

        mock_update.assert_called_once()

    def test_skips_config_lookup_if_session_has_region(self):
        """Should not call load_config if session already has a region."""
        from kloudkompass.tui.provider_setup import check_region_configured
        session = _fresh_session(provider="aws", region="us-west-2")

        with patch("kloudkompass.tui.provider_setup.load_config") as mock_config:
            check_region_configured(session)

        mock_config.assert_not_called()


# ────────────────────────────────────────────────────
#  Pure: apply_region_choice
# ────────────────────────────────────────────────────

class TestApplyRegionChoice:
    """Tests for the apply_region_choice function."""

    def test_returns_success_with_chosen_region(self):
        """apply_region_choice should return the chosen region."""
        from kloudkompass.tui.provider_setup import apply_region_choice
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.session.update_session"):
            with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
                with patch("kloudkompass.tui.provider_setup.save_config"):
                    result = apply_region_choice(session, "eu-central-1")

        assert result.success is True
        assert result.region == "eu-central-1"

    def test_saves_to_config(self):
        """apply_region_choice should persist the region to config."""
        from kloudkompass.tui.provider_setup import apply_region_choice
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.session.update_session"):
            with patch("kloudkompass.tui.provider_setup.load_config",
                       return_value={"default_provider": "aws"}):
                with patch("kloudkompass.tui.provider_setup.save_config") as mock_save:
                    apply_region_choice(session, "us-west-1")

        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][0]
        assert saved_config["default_region"] == "us-west-1"

    def test_survives_config_save_failure(self):
        """If config save fails, should still return success."""
        from kloudkompass.tui.provider_setup import apply_region_choice
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.session.update_session"):
            with patch("kloudkompass.tui.provider_setup.load_config",
                       side_effect=Exception("disk full")):
                result = apply_region_choice(session, "us-east-2")

        assert result.success is True
        assert result.region == "us-east-2"


# ────────────────────────────────────────────────────
#  Interactive: ensure_region_configured (prompts.py)
# ────────────────────────────────────────────────────

class TestEnsureRegionConfiguredInteractive:
    """Tests for the interactive ensure_region_configured wrapper."""

    def test_returns_directly_when_region_set(self):
        """Should return immediately if session has a region."""
        from kloudkompass.tui.prompts import ensure_region_configured
        session = _fresh_session(provider="aws", region="us-east-1")
        result = ensure_region_configured(session)

        assert result.success is True
        assert result.region == "us-east-1"

    def test_prompts_when_no_region(self):
        """Should prompt user when no region in session or config."""
        from kloudkompass.tui.prompts import ensure_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
            with patch("builtins.input", return_value="ap-south-1"):
                with patch("builtins.print"):
                    with patch("kloudkompass.tui.session.update_session"):
                        with patch("kloudkompass.tui.provider_setup.save_config"):
                            result = ensure_region_configured(session)

        assert result.success is True
        assert result.region == "ap-south-1"

    def test_defaults_to_us_east_1_on_empty_input(self):
        """Should use us-east-1 when user presses Enter without typing."""
        from kloudkompass.tui.prompts import ensure_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
            with patch("builtins.input", return_value=""):
                with patch("builtins.print"):
                    with patch("kloudkompass.tui.session.update_session"):
                        with patch("kloudkompass.tui.provider_setup.save_config"):
                            result = ensure_region_configured(session)

        assert result.success is True
        assert result.region == "us-east-1"

    def test_handles_keyboard_interrupt(self):
        """Should return failure on KeyboardInterrupt."""
        from kloudkompass.tui.prompts import ensure_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
            with patch("builtins.input", side_effect=KeyboardInterrupt):
                with patch("builtins.print"):
                    result = ensure_region_configured(session)

        assert result.success is False

    def test_handles_eof_error(self):
        """Should return failure on EOFError."""
        from kloudkompass.tui.prompts import ensure_region_configured
        session = _fresh_session(provider="aws")

        with patch("kloudkompass.tui.provider_setup.load_config", return_value={}):
            with patch("builtins.input", side_effect=EOFError):
                with patch("builtins.print"):
                    result = ensure_region_configured(session)

        assert result.success is False


# ────────────────────────────────────────────────────
#  Session auto-load from config
# ────────────────────────────────────────────────────

class TestSessionAutoLoad:
    """Tests for session auto-initialization from config."""

    def setup_method(self):
        """Reset session before each test."""
        from kloudkompass.tui import session as session_module
        session_module._session = None

    def teardown_method(self):
        """Clean up session after each test."""
        from kloudkompass.tui import session as session_module
        session_module._session = None

    def test_session_loads_default_provider_from_config(self):
        """get_session should load default_provider from config on first call."""
        from kloudkompass.tui import session as session_module

        config_data = {"default_provider": "azure", "default_region": "westus2"}

        with patch("kloudkompass.config_manager.load_config", return_value=config_data):
            s = session_module.get_session()

        assert s.provider == "azure"
        assert s.region == "westus2"

    def test_session_defaults_to_aws_when_no_config(self):
        """get_session should default to AWS when config has no provider."""
        from kloudkompass.tui import session as session_module

        with patch("kloudkompass.config_manager.load_config", return_value={}):
            s = session_module.get_session()

        assert s.provider == "aws"
        assert s.region is None

    def test_session_loads_profile_from_config(self):
        """get_session should load default_profile from config."""
        from kloudkompass.tui import session as session_module

        config_data = {"default_profile": "production"}

        with patch("kloudkompass.config_manager.load_config", return_value=config_data):
            s = session_module.get_session()

        assert s.profile == "production"

    def test_session_caches_after_first_load(self):
        """get_session should return same object on subsequent calls."""
        from kloudkompass.tui import session as session_module

        with patch("kloudkompass.config_manager.load_config",
                    return_value={"default_region": "us-east-1"}) as mock_config:
            s1 = session_module.get_session()
            s2 = session_module.get_session()

        assert s1 is s2
        mock_config.assert_called_once()  # Config only loaded once


# ────────────────────────────────────────────────────
#  Constants and dataclasses
# ────────────────────────────────────────────────────

class TestRegionGateConstants:
    """Tests for region gate constants."""

    def test_aws_regions_is_list(self):
        from kloudkompass.tui.provider_setup import AWS_REGIONS
        assert isinstance(AWS_REGIONS, list)
        assert len(AWS_REGIONS) >= 4

    def test_default_region_is_us_east_1(self):
        from kloudkompass.tui.provider_setup import DEFAULT_REGION
        assert DEFAULT_REGION == "us-east-1"

    def test_region_setup_result_has_needs_prompt(self):
        from kloudkompass.tui.provider_setup import RegionSetupResult
        result = RegionSetupResult(success=False, region="", needs_prompt=True)
        assert result.needs_prompt is True

    def test_region_setup_result_default_needs_prompt_false(self):
        from kloudkompass.tui.provider_setup import RegionSetupResult
        result = RegionSetupResult(success=True, region="us-east-1")
        assert result.needs_prompt is False
