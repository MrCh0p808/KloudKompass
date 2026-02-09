# tests/test_cli_integration.py
# ------------------------------
# Tests CLI commands using Click's CliRunner. This lets me invoke
# the CLI as if from the command line and check the output.

import pytest
from unittest.mock import patch, Mock
from click.testing import CliRunner

from bashcloud.cli import main


class TestCLIHelp:
    """Tests for CLI help output."""
    
    def test_main_help(self):
        """Should display help text."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "BashCloud" in result.output
        assert "cost" in result.output
        assert "config" in result.output
    
    def test_version(self):
        """Should display version."""
        runner = CliRunner()
        result = runner.invoke(main, ['--version'])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    def test_cost_help(self):
        """Should display cost command help."""
        runner = CliRunner()
        result = runner.invoke(main, ['cost', '--help'])
        
        assert result.exit_code == 0
        assert "--provider" in result.output
        assert "--start" in result.output
        assert "--end" in result.output
        assert "--breakdown" in result.output


class TestCLIConfig:
    """Tests for config command."""
    
    def test_config_show(self):
        """Should show current config."""
        runner = CliRunner()
        
        with patch('bashcloud.config_manager.load_config', return_value={
            "default_provider": "aws",
            "default_output": "table",
            "default_profile": None,
            "default_region": None,
        }):
            result = runner.invoke(main, ['config', '--show'])
        
        assert result.exit_code == 0
        assert "default_provider" in result.output
        assert "aws" in result.output


class TestCLICheck:
    """Tests for check command."""
    
    def test_check_all_installed(self):
        """Should pass when all CLIs installed and configured."""
        runner = CliRunner()
        
        with patch('shutil.which', return_value='/usr/bin/aws'):
            with patch('bashcloud.core.health.check_credentials', 
                       return_value=(True, None)):
                result = runner.invoke(main, ['check'])
        
        assert "Installed" in result.output
        assert "Valid" in result.output
    
    def test_check_cli_not_found(self):
        """Should report when CLI not found."""
        runner = CliRunner()
        
        with patch('shutil.which', return_value=None):
            result = runner.invoke(main, ['check', '--provider', 'aws'])
        
        assert "Not found" in result.output
        assert result.exit_code == 1


class TestCLICostCommand:
    """Tests for cost command invocation."""
    
    def test_cost_missing_dates(self):
        """Should require start and end dates."""
        runner = CliRunner()
        result = runner.invoke(main, ['cost'])
        
        # Should fail due to missing required option
        assert result.exit_code != 0
        assert "start" in result.output.lower() or "required" in result.output.lower()
    
    def test_cost_cli_not_installed(self):
        """Should error gracefully when CLI not installed."""
        runner = CliRunner()
        
        with patch('shutil.which', return_value=None):
            result = runner.invoke(main, [
                'cost',
                '--provider', 'aws',
                '--start', '2024-01-01',
                '--end', '2024-02-01',
            ])
        
        assert result.exit_code == 1
        assert "not installed" in result.output.lower() or "error" in result.output.lower()


class TestCLIDebugMode:
    """Tests for debug mode."""
    
    def test_debug_flag_accepted(self):
        """Debug flag should be accepted."""
        runner = CliRunner()
        result = runner.invoke(main, ['--debug', '--help'])
        
        # Should not error
        assert result.exit_code == 0
