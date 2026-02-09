# bashcloud/tui/doctor.py
# ------------------------
# the doctor command It checks the environment health
# including CLI installations, credentials, and configuration.

from typing import List, Tuple

from bashcloud.core.health import check_cli_installed, check_credentials
from bashcloud.config_manager import config_exists, get_config_path


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
    
    # Check BashCloud config
    if config_exists():
        results.append(("BashCloud Config", f"Found at {get_config_path()}", True))
    else:
        results.append(("BashCloud Config", "No config file (using defaults)", True))
    
    return results


def print_doctor_report() -> bool:
    """
    Print a formatted doctor report.
    
    Returns:
        True if all checks passed, False otherwise
    """
    print()
    print("=" * 50)
    print("  BashCloud Doctor")
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
    return all_passed
