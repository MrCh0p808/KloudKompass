# kloudkompass/tui/provider_setup.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Provider configuration — PURE LOGIC ONLY.
# Phase 2.6 refactor: zero input(), zero print().
# All UI rendering lives in provider_setup_screen.py.

from dataclasses import dataclass
from typing import Optional, Dict, List

from kloudkompass.core.health import check_cli_installed, check_credentials, get_install_instructions
from kloudkompass.core.provider_factory import is_provider_implemented, get_available_providers
from kloudkompass.config_manager import load_config, save_config


@dataclass
class ProviderSetupResult:
    """Result of provider setup check."""
    success: bool
    provider: str
    error: Optional[str] = None
    
    @property
    def is_configured(self) -> bool:
        """True if provider is fully configured and ready."""
        return self.success and self.error is None


# CLI name mapping
_PROVIDER_CLI = {
    "aws": "aws",
    "azure": "az",
    "gcp": "gcloud",
}


def check_provider_ready(provider: str) -> ProviderSetupResult:
    """
    Check if a provider is ready for use.
    
    Pure function — no side effects, no IO.
    
    Checks:
        1. Provider is implemented
        2. CLI is installed
        3. Credentials are configured
    
    Returns:
        ProviderSetupResult with status and any error message.
    """
    provider_lower = provider.lower().strip()
    
    # Check if implemented
    if not is_provider_implemented(provider_lower):
        return ProviderSetupResult(
            success=False,
            provider=provider_lower,
            error=f"{provider.upper()} cost analysis is not yet available. Currently supported: AWS",
        )
    
    # Check CLI installed
    cli_name = _PROVIDER_CLI.get(provider_lower)
    if not cli_name:
        return ProviderSetupResult(
            success=False,
            provider=provider_lower,
            error=f"Unknown provider: {provider}",
        )
    
    if not check_cli_installed(cli_name):
        instructions = get_install_instructions(cli_name)
        return ProviderSetupResult(
            success=False,
            provider=provider_lower,
            error=f"{provider.upper()} CLI not found.\n\n{instructions}",
        )
    
    # Check credentials
    is_valid, cred_error = check_credentials(provider_lower)
    if not is_valid:
        return ProviderSetupResult(
            success=False,
            provider=provider_lower,
            error=f"{provider.upper()} credentials not configured.\n\n{cred_error}",
        )
    
    return ProviderSetupResult(success=True, provider=provider_lower)


def get_setup_instructions(provider: str) -> Dict[str, object]:
    """
    Return structured setup data for a provider.
    
    Pure function — returns data, never prints.
    
    Returns:
        Dict with keys:
            - provider: str
            - cli_name: str
            - cli_installed: bool
            - creds_valid: bool
            - cred_error: Optional[str]
            - install_instructions: str
            - config_steps: List[str]
    """
    provider_lower = provider.lower().strip()
    cli_name = _PROVIDER_CLI.get(provider_lower, provider_lower)
    
    cli_installed = check_cli_installed(cli_name)
    
    creds_valid = False
    cred_error = None
    if cli_installed:
        creds_valid, cred_error = check_credentials(provider_lower)
    
    # Provider-specific config steps
    config_steps = _get_config_steps(provider_lower)
    
    return {
        "provider": provider_lower,
        "cli_name": cli_name,
        "cli_installed": cli_installed,
        "creds_valid": creds_valid,
        "cred_error": cred_error,
        "install_instructions": get_install_instructions(cli_name),
        "config_steps": config_steps,
    }


def _get_config_steps(provider: str) -> List[str]:
    """Return provider-specific credential config steps."""
    steps = {
        "aws": [
            "Run: aws configure",
            "Enter your Access Key ID",
            "Enter your Secret Access Key",
            "Enter your default region (e.g., us-east-1)",
        ],
        "azure": [
            "Run: az login",
            "Complete browser authentication",
        ],
        "gcp": [
            "Run: gcloud auth login",
            "Complete browser authentication",
        ],
    }
    return steps.get(provider, [f"Configure {provider} credentials"])


def persist_provider_choice(provider: str) -> bool:
    """
    Save provider choice to config file.
    
    Pure side-effect: only touches config file.
    Returns True on success, False on failure.
    """
    try:
        config = load_config()
        config['default_provider'] = provider.lower().strip()
        save_config(config)
        return True
    except Exception:
        return False


def ensure_provider_configured(provider: str, interactive: bool = True) -> ProviderSetupResult:
    """
    Gate function — checks if provider is ready.
    
    This is a PURE CHECK. It does not run any UI.
    When interactive=True and check fails, caller is responsible
    for pushing ProviderSetupScreen.
    
    Args:
        provider: Provider name (aws, azure, gcp)
        interactive: Hint to caller — if True, caller should show setup UI.
    
    Returns:
        ProviderSetupResult with status.
    
    Usage:
        result = ensure_provider_configured("aws")
        if not result.success:
            # Caller pushes ProviderSetupScreen
            return ProviderSetupScreen(result)
    """
    return check_provider_ready(provider)


@dataclass
class RegionSetupResult:
    """Result of region configuration check."""
    success: bool
    region: str
    needs_prompt: bool = False
    message: Optional[str] = None


# Common AWS regions for quick selection
AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-central-1", "ap-south-1", "ap-southeast-1",
]

DEFAULT_REGION = "us-east-1"


def check_region_configured(session) -> RegionSetupResult:
    """
    Pure check — is a region configured? No I/O.

    Resolution order:
        1. Session already has a region → use it
        2. Config file has a region → use it and update session
        3. Return needs_prompt=True so caller can handle interactively

    Returns:
        RegionSetupResult with resolved region or needs_prompt flag.
    """
    from kloudkompass.tui.session import update_session

    # 1. Check session
    if session.region:
        return RegionSetupResult(success=True, region=session.region)

    # 2. Check config
    config = load_config()
    saved_region = config.get("default_region")
    if saved_region:
        update_session(session.with_region(saved_region))
        return RegionSetupResult(success=True, region=saved_region)

    # 3. Region not found — caller must prompt
    return RegionSetupResult(
        success=False, region="", needs_prompt=True,
        message="No region configured."
    )


def apply_region_choice(session, region: str) -> RegionSetupResult:
    """Save chosen region to session and config."""
    from kloudkompass.tui.session import update_session

    update_session(session.with_region(region))
    try:
        config = load_config()
        config["default_region"] = region
        save_config(config)
    except Exception:
        pass  # Non-critical

    return RegionSetupResult(success=True, region=region)


