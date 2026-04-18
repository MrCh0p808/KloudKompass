# kloudkompass/tui/doctor.py
# ------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Doctor command for environment health checks.

from typing import List, Tuple

from kloudkompass.core.health import check_cli_installed, check_credentials
from kloudkompass.config_manager import config_exists, get_config_path
from kloudkompass.tui.footer import ATTRIBUTION_LINE1
from kloudkompass.tui.screens import BRAND_TITLE


def run_doctor() -> List[Tuple[str, str, bool]]:
    """
    Run all health checks and return results.
    
    Returns:
        List of (check_name, message, passed) tuples
    """
    results = []
    
    # Check each cloud CLI
    cli_checks = [
        ("AWS CLI", "aws"),
        ("Azure CLI", "az"),
        ("Google Cloud SDK", "gcloud"),
    ]
    
    for name, cli in cli_checks:
        if check_cli_installed(cli):
            results.append((name, "Installed", True))
        else:
            results.append((name, "Not found in PATH", False))
    
    # Check credentials for installed CLIs
    if check_cli_installed("aws"):
        is_valid, error = check_credentials("aws")
        if is_valid:
            results.append(("AWS Credentials", "Valid", True))
        else:
            results.append(("AWS Credentials", error or "Invalid", False))
    
    if check_cli_installed("az"):
        is_valid, error = check_credentials("azure")
        if is_valid:
            results.append(("Azure Credentials", "Valid", True))
        else:
            results.append(("Azure Credentials", error or "Invalid", False))
    
    if check_cli_installed("gcloud"):
        is_valid, error = check_credentials("gcp")
        if is_valid:
            results.append(("GCP Credentials", "Valid", True))
        else:
            results.append(("GCP Credentials", error or "Invalid", False))
    
    # Check Kloud Kompass config
    if config_exists():
        results.append(("Kloud Kompass Config", f"Found at {get_config_path()}", True))
    else:
        results.append(("Kloud Kompass Config", "No config file (using defaults)", True))
    
    return results


def print_doctor_report() -> bool:
    """
    Print a formatted doctor report with attribution.
    
    Returns:
        True if all checks passed, False otherwise
    """
    print()
    print("=" * 50)
    print(f"  {BRAND_TITLE} - Doctor")
    print("=" * 50)
    print()
    
    results = run_doctor()
    all_passed = True
    
    for name, message, passed in results:
        status = "[OK]" if passed else "[!!]"
        print(f"  {status} {name}: {message}")
        if not passed:
            all_passed = False
    
    print()
    print("-" * 50)
    
    if all_passed:
        print("  All checks passed.")
    else:
        print("  Some checks failed. See above for details.")
    
    print()
    print("-" * 50)
    print(f"  {ATTRIBUTION_LINE1}")
    print("-" * 50)
    print()
    return all_passed
