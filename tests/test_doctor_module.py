# tests/test_doctor_module.py
# -----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Phase 2.6 doctor module tests (20 tests).

import pytest
from unittest.mock import patch, MagicMock


class TestRunDoctor:
    """Tests for run_doctor()."""
    
    def test_run_doctor_exists(self):
        from kloudkompass.tui.doctor import run_doctor
        assert run_doctor is not None
    
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_returns_list(self, mock_cli, mock_creds):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        results = run_doctor()
        assert isinstance(results, list)
    
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_results_are_tuples(self, mock_cli, mock_creds):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        results = run_doctor()
        for result in results:
            assert isinstance(result, tuple)
            assert len(result) == 3
    
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_checks_aws_cli(self, mock_cli, mock_creds):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        results = run_doctor()
        names = [r[0] for r in results]
        assert "AWS CLI" in names
    
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_checks_azure_cli(self, mock_cli, mock_creds):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        results = run_doctor()
        names = [r[0] for r in results]
        assert "Azure CLI" in names
    
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_checks_gcp_cli(self, mock_cli, mock_creds):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        results = run_doctor()
        names = [r[0] for r in results]
        assert "Google Cloud SDK" in names
    
    @patch('kloudkompass.tui.doctor.config_exists')
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_checks_config(self, mock_cli, mock_creds, mock_config):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        mock_config.return_value = False
        results = run_doctor()
        names = [r[0] for r in results]
        assert "Kloud Kompass Config" in names
    
    @patch('kloudkompass.tui.doctor.config_exists')
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_config_present_passes(self, mock_cli, mock_creds, mock_config):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        mock_config.return_value = True
        results = run_doctor()
        config_results = [r for r in results if r[0] == "Kloud Kompass Config"]
        assert config_results[0][2] is True
    
    @patch('kloudkompass.tui.doctor.config_exists')
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_config_absent_still_passes(self, mock_cli, mock_creds, mock_config):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = False
        mock_config.return_value = False
        results = run_doctor()
        config_results = [r for r in results if r[0] == "Kloud Kompass Config"]
        assert config_results[0][2] is True  # Using defaults is OK
    
    @patch('kloudkompass.tui.doctor.check_credentials')
    @patch('kloudkompass.tui.doctor.check_cli_installed')
    def test_cli_installed_shows_ok(self, mock_cli, mock_creds):
        from kloudkompass.tui.doctor import run_doctor
        mock_cli.return_value = True
        mock_creds.return_value = (True, None)
        results = run_doctor()
        aws_result = [r for r in results if r[0] == "AWS CLI"][0]
        assert aws_result[2] is True
        assert "Installed" in aws_result[1]


class TestPrintDoctorReport:
    """Tests for print_doctor_report()."""
    
    @patch('kloudkompass.tui.doctor.run_doctor')
    def test_returns_bool(self, mock_doctor):
        from kloudkompass.tui.doctor import print_doctor_report
        mock_doctor.return_value = [("Test", "OK", True)]
        with patch('builtins.print'):
            result = print_doctor_report()
        assert isinstance(result, bool)
    
    @patch('kloudkompass.tui.doctor.run_doctor')
    def test_returns_true_when_all_pass(self, mock_doctor):
        from kloudkompass.tui.doctor import print_doctor_report
        mock_doctor.return_value = [("A", "OK", True), ("B", "OK", True)]
        with patch('builtins.print'):
            assert print_doctor_report() is True
    
    @patch('kloudkompass.tui.doctor.run_doctor')
    def test_returns_false_when_any_fail(self, mock_doctor):
        from kloudkompass.tui.doctor import print_doctor_report
        mock_doctor.return_value = [("A", "OK", True), ("B", "FAIL", False)]
        with patch('builtins.print'):
            assert print_doctor_report() is False


class TestDoctorBranding:
    """Tests for doctor branding."""
    
    def test_uses_brand_title(self):
        from kloudkompass.tui.doctor import BRAND_TITLE
        assert "Kloud Kompass" in BRAND_TITLE
    
    def test_uses_attribution(self):
        from kloudkompass.tui.doctor import ATTRIBUTION_LINE1
        assert ATTRIBUTION_LINE1 is not None
    
    @patch('kloudkompass.tui.doctor.run_doctor')
    def test_report_includes_brand(self, mock_doctor):
        from kloudkompass.tui.doctor import print_doctor_report, BRAND_TITLE
        mock_doctor.return_value = []
        output = []
        with patch('builtins.print', side_effect=lambda *a, **kw: output.append(str(a))):
            print_doctor_report()
        full_output = "\n".join(output)
        assert "Kloud Kompass" in full_output
    
    @patch('kloudkompass.tui.doctor.run_doctor')
    def test_report_includes_attribution(self, mock_doctor):
        from kloudkompass.tui.doctor import print_doctor_report, ATTRIBUTION_LINE1
        mock_doctor.return_value = []
        output = []
        with patch('builtins.print', side_effect=lambda *a, **kw: output.append(str(a))):
            print_doctor_report()
        full_output = "\n".join(output)
        assert "TTox.Tech" in full_output or ATTRIBUTION_LINE1 in full_output
