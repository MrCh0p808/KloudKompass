# bashcloud/core/health.py
# -------------------------
# Centralized all CLI availability and credential checks.
# Before running any cloud command, This calls these functions to fail fast
# with a helpful error message instead of cryptic subprocess failures.

import subprocess
import shutil
from typing import Optional, Tuple

from bashcloud.core.exceptions import CLIUnavailableError, CredentialError


def check_cli_installed(cli_name: str) -> bool:
    """
    Check if a CLI tool is installed and in PATH.
    
    shutil.which used because it works cross-platform and handles
    PATH lookup correctly. Returns True if found, False otherwise.
    """
    return shutil.which(cli_name) is not None


def require_cli(cli_name: str, install_instructions: Optional[str] = None) -> None:
    """
    Raise CLIUnavailableError if the CLI is not installed.
    
    This as a guard at the start of provider methods. It gives
    users clear instructions on how to install what they need.
    """
    if not check_cli_installed(cli_name):
        instructions = install_instructions or get_install_instructions(cli_name)
        raise CLIUnavailableError(cli_name, instructions)


def get_install_instructions(cli_name: str) -> str:
    """
    Return installation instructions for common CLI tools.
    
    Keeps these here instead of hardcoding in exceptions so they are
    easy to update and the exception class stays generic.
    """
    instructions = {
        "aws": (
            "Install the AWS CLI:\n"
            "  - Linux: curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o awscliv2.zip && unzip awscliv2.zip && sudo ./aws/install\n"
            "  - macOS: brew install awscli\n"
            "  - Then run: aws configure"
        ),
        "az": (
            "Install the Azure CLI:\n"
            "  - Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash\n"
            "  - macOS: brew install azure-cli\n"
            "  - Then run: az login"
        ),
        "gcloud": (
            "Install the Google Cloud SDK:\n"
            "  - Linux/macOS: curl https://sdk.cloud.google.com | bash\n"
            "  - Then run: gcloud init"
        ),
    }
    return instructions.get(cli_name, f"Install {cli_name} and ensure it is in your PATH.")


def check_aws_credentials() -> Tuple[bool, Optional[str]]:
    """
    Verify AWS credentials are configured and valid.
    
    Runs 'aws sts get-caller-identity' which is a lightweight call that
    confirms credentials work. Returns (True, None) if valid, or
    (False, error_message) if not.
    """
    if not check_cli_installed("aws"):
        return False, "AWS CLI is not installed"
    
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, None
        else:
            # Parse common error patterns
            stderr = result.stderr.lower()
            if "unable to locate credentials" in stderr:
                return False, "No credentials configured. Run 'aws configure'."
            elif "expired" in stderr:
                return False, "Credentials have expired. Refresh your credentials."
            elif "invalid" in stderr:
                return False, "Credentials are invalid. Check your access key and secret."
            else:
                return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Credential check timed out. Check your network connection."
    except Exception as e:
        return False, str(e)


def check_azure_credentials() -> Tuple[bool, Optional[str]]:
    """
    Verify Azure credentials are configured and valid.
    
    Runs 'az account show' which returns current subscription info
    if logged in. Returns (True, None) or (False, error_message).
    """
    if not check_cli_installed("az"):
        return False, "Azure CLI is not installed"
    
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return True, None
        else:
            stderr = result.stderr.lower()
            if "please run 'az login'" in stderr or "no subscription" in stderr:
                return False, "Not logged in. Run 'az login' to authenticate."
            else:
                return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Credential check timed out. Check your network connection."
    except Exception as e:
        return False, str(e)


def check_gcp_credentials() -> Tuple[bool, Optional[str]]:
    """
    Verify GCP credentials are configured and valid.
    
    Runs 'gcloud auth list' to see if there are active credentials.
    Returns (True, None) or (False, error_message).
    """
    if not check_cli_installed("gcloud"):
        return False, "Google Cloud SDK is not installed"
    
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            import json
            accounts = json.loads(result.stdout)
            if accounts and any(a.get("status") == "ACTIVE" for a in accounts):
                return True, None
            else:
                return False, "No active account. Run 'gcloud auth login'."
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Credential check timed out. Check your network connection."
    except Exception as e:
        return False, str(e)


def check_credentials(provider: str) -> Tuple[bool, Optional[str]]:
    """
    Check credentials for the specified provider.
    
    This as a unified entry point that routes to the provider-specific
    check. Makes the CLI code cleaner.
    """
    checkers = {
        "aws": check_aws_credentials,
        "azure": check_azure_credentials,
        "gcp": check_gcp_credentials,
    }
    
    checker = checkers.get(provider.lower())
    if checker is None:
        return False, f"Unknown provider: {provider}"
    
    return checker()


def require_credentials(provider: str) -> None:
    """
    Raise CredentialError if credentials are not valid.
    
    This as a guard before making API calls. Fails fast with
    a helpful message.
    """
    is_valid, error = check_credentials(provider)
    if not is_valid:
        raise CredentialError(provider, error)
