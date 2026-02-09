# tests/test_doctor_version.py
# -----------------------------
# I test the doctor command version checking and remediation logic.

import pytest
import re
from unittest.mock import patch, Mock


class TestAWSCLIVersionCheck:
    """Tests for AWS CLI version parsing in doctor."""
    
    def test_version_2_passes(self):
        """Should pass for AWS CLI v2.x."""
        from bashcloud.tui.doctor import check_aws_cli_version
        
        mock_adapter = Mock()
        mock_adapter.get_cli_version.return_value = "2.15.0"
        
        with patch("bashcloud.infra.aws_cli_adapter.get_aws_cli_adapter", return_value=mock_adapter):
            passed, msg, remediation = check_aws_cli_version()
        
        assert passed is True
        assert "2.15.0" in msg
        assert remediation is None
    
    def test_version_1_fails(self):
        """Should fail for AWS CLI v1.x."""
        from bashcloud.tui.doctor import check_aws_cli_version
        
        mock_adapter = Mock()
        mock_adapter.get_cli_version.return_value = "1.27.0"
        
        with patch("bashcloud.infra.aws_cli_adapter.get_aws_cli_adapter", return_value=mock_adapter):
            passed, msg, remediation = check_aws_cli_version()
        
        assert passed is False
        assert "requires v2" in msg.lower()
        assert remediation is not None
        assert "upgrade" in remediation.lower()
    
    def test_version_none_fails(self):
        """Should fail when version cannot be determined."""
        from bashcloud.tui.doctor import check_aws_cli_version
        
        mock_adapter = Mock()
        mock_adapter.get_cli_version.return_value = None
        
        with patch("bashcloud.infra.aws_cli_adapter.get_aws_cli_adapter", return_value=mock_adapter):
            passed, msg, remediation = check_aws_cli_version()
        
        assert passed is False


class TestCostExplorerAccessCheck:
    """Tests for Cost Explorer access checking."""
    
    def test_accessible_passes(self):
        """Should pass when Cost Explorer is accessible."""
        from bashcloud.tui.doctor import check_cost_explorer_access
        
        mock_adapter = Mock()
        mock_adapter.check_cost_explorer_access.return_value = (True, None)
        
        with patch("bashcloud.infra.aws_cli_adapter.get_aws_cli_adapter", return_value=mock_adapter):
            passed, msg, remediation = check_cost_explorer_access()
        
        assert passed is True
        assert "accessible" in msg.lower()
    
    def test_not_enabled_fails_with_remediation(self):
        """Should provide remediation for Cost Explorer not enabled."""
        from bashcloud.tui.doctor import check_cost_explorer_access
        
        mock_adapter = Mock()
        mock_adapter.check_cost_explorer_access.return_value = (
            False,
            "Cost Explorer is not enabled for this account"
        )
        
        with patch("bashcloud.infra.aws_cli_adapter.get_aws_cli_adapter", return_value=mock_adapter):
            passed, msg, remediation = check_cost_explorer_access()
        
        assert passed is False
        assert "not enabled" in msg.lower()
        assert remediation is not None
        assert "enable" in remediation.lower()
    
    def test_permission_denied_fails_with_remediation(self):
        """Should provide remediation for permission denied."""
        from bashcloud.tui.doctor import check_cost_explorer_access
        
        mock_adapter = Mock()
        mock_adapter.check_cost_explorer_access.return_value = (
            False,
            "ce:GetCostAndUsage permission denied"
        )
        
        with patch("bashcloud.infra.aws_cli_adapter.get_aws_cli_adapter", return_value=mock_adapter):
            passed, msg, remediation = check_cost_explorer_access()
        
        assert passed is False
        assert "permission" in msg.lower()
        assert remediation is not None
        assert "permission" in remediation.lower() or "iam" in remediation.lower()


class TestDoctorReport:
    """Tests for full doctor report."""
    
    def test_run_doctor_returns_tuples(self):
        """Should return list of 4-tuples."""
        from bashcloud.tui.doctor import run_doctor
        
        with patch("bashcloud.tui.doctor.check_cli_installed", return_value=False):
            with patch("bashcloud.tui.doctor.config_exists", return_value=False):
                results = run_doctor()
        
        assert isinstance(results, list)
        for item in results:
            assert len(item) == 4  # (name, message, passed, remediation)
