# bashcloud/tui/doctor.py
# ------------------------
# I implement the doctor command here. It checks the environment health
# including CLI installations, credentials, versions, and permissions.

import re
from typing import List, Tuple, Optional

from bashcloud.core.health import check_cli_installed, check_credentials
from bashcloud.config_manager import config_exists, get_config_path


def check_aws_cli_version() -> Tuple[bool, str, Optional[str]]:
    """
    Check AWS CLI version is 2.x or higher.
    
    Returns (passed, message, remediation).
    """
    from bashcloud.infra.aws_cli_adapter import get_aws_cli_adapter
    
    adapter = get_aws_cli_adapter()
    version = adapter.get_cli_version()
    
    if version is None:
        return (
            False,
            "Unable to determine version",
            "Run 'aws --version' to check manually.",
        )
    
    # I parse major version
    match = re.match(r"(\d+)\.", version)
    if match:
        major = int(match.group(1))
        if major >= 2:
            return (True, f"v{version}", None)
        else:
            return (
                False,
                f"v{version} (requires v2.x)",
                "Upgrade AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
            )
    
    return (False, f"Unknown format: {version}", None)


def check_cost_explorer_access() -> Tuple[bool, str, Optional[str]]:
    """
    Check if Cost Explorer API is accessible.
    
    Returns (passed, message, remediation).
    """
    from bashcloud.infra.aws_cli_adapter import get_aws_cli_adapter
    
    adapter = get_aws_cli_adapter()
    is_ok, error = adapter.check_cost_explorer_access()
    
    if is_ok:
        return (True, "Accessible", None)
    
    # I provide specific remediation based on error
    if "not enabled" in error.lower():
        return (
            False,
            "Cost Explorer not enabled",
            "Enable Cost Explorer in AWS Console: Billing > Cost Explorer > Enable",
        )
    elif "permission denied" in error.lower() or "access denied" in error.lower():
        return (
            False,
            "Permission denied",
            "Add ce:GetCostAndUsage permission to your IAM user/role.",
        )
    else:
        return (False, error, "Check AWS credentials and permissions.")


def run_doctor() -> List[Tuple[str, str, bool, Optional[str]]]:
    """
    Run all health checks and return results.
    
    Returns:
        List of (check_name, message, passed, remediation) tuples
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
            results.append((name, "Installed", True, None))
        else:
            results.append((
                name,
                "Not found in PATH",
                False,
                f"Install {name}: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html" if cli == "aws" else None,
            ))
    
    # AWS-specific checks
    if check_cli_installed("aws"):
        # Version check
        passed, msg, remediation = check_aws_cli_version()
        results.append(("AWS CLI Version", msg, passed, remediation))
        
        # Credentials check
        is_valid, error = check_credentials("aws")
        if is_valid:
            results.append(("AWS Credentials", "Valid", True, None))
        else:
            results.append((
                "AWS Credentials",
                error or "Invalid",
                False,
                "Run 'aws configure' to set up credentials.",
            ))
        
        # Cost Explorer access check
        if is_valid:  # Only check if credentials are valid
            passed, msg, remediation = check_cost_explorer_access()
            results.append(("Cost Explorer Access", msg, passed, remediation))
    
    # Azure credentials
    if check_cli_installed("az"):
        is_valid, error = check_credentials("azure")
        if is_valid:
            results.append(("Azure Credentials", "Valid", True, None))
        else:
            results.append((
                "Azure Credentials",
                error or "Invalid",
                False,
                "Run 'az login' to authenticate.",
            ))
    
    # GCP credentials
    if check_cli_installed("gcloud"):
        is_valid, error = check_credentials("gcp")
        if is_valid:
            results.append(("GCP Credentials", "Valid", True, None))
        else:
            results.append((
                "GCP Credentials",
                error or "Invalid",
                False,
                "Run 'gcloud auth login' to authenticate.",
            ))
    
    # Check BashCloud config
    if config_exists():
        results.append(("BashCloud Config", f"Found at {get_config_path()}", True, None))
    else:
        results.append(("BashCloud Config", "No config file (using defaults)", True, None))
    
    return results


def print_doctor_report() -> bool:
    """
    Print a formatted doctor report.
    
    Returns:
        True if all checks passed, False otherwise
    """
    print()
    print("=" * 60)
    print("  BashCloud Doctor")
    print("=" * 60)
    print()
    
    results = run_doctor()
    all_passed = True
    remediations = []
    
    for name, message, passed, remediation in results:
        status = "[OK]" if passed else "[!!]"
        print(f"  {status} {name}: {message}")
        if not passed:
            all_passed = False
            if remediation:
                remediations.append((name, remediation))
    
    print()
    print("-" * 60)
    
    if all_passed:
        print("  All checks passed.")
    else:
        print("  Some checks failed. See remediation steps below.")
        print()
        
        if remediations:
            print("  Remediation Steps:")
            print("  " + "-" * 40)
            for name, fix in remediations:
                print(f"  {name}:")
                print(f"    {fix}")
                print()
    
    print()
    return all_passed
