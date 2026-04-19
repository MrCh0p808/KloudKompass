# kloudkompass/core/auth_manager.py
# --------------------------------
# Handles Interactive Login Flows for Cloud Interfaces and parses
# active Identity contexts (Subscriptions, Profiles, Projects).

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from kloudkompass.utils.logger import error, debug

@dataclass
class LoginOption:
    """Represents a structured choice for authenticating with a cloud provider."""
    id: str
    name: str
    command: str
    description: str
    guide: List[str]
    is_recommended: bool = False

def get_login_options(provider: str) -> List[LoginOption]:
    """Returns all available login methods for a specific provider."""
    provider = provider.lower()
    options = []
    
    if provider == "aws":
        options.append(LoginOption(
            id="aws_sso",
            name="AWS IAM Identity Center (SSO)",
            command="aws configure sso",
            description="Corporate login with browser-based authentication. Most secure.",
            guide=[
                "💡 AWS SSO Setup Guide:",
                " - Start URL: Found in IAM Identity Center Dashboard (AWS Portal URL).",
                " - Session Name: A local nickname (e.g., 'work').",
                " - Region: The home region of your SSO portal (e.g., us-east-1)."
            ],
            is_recommended=True
        ))
        options.append(LoginOption(
            id="aws_keys",
            name="AWS Access Keys (Legacy)",
            command="aws configure",
            description="Manual input of Access Key ID and Secret Access Key.",
            guide=[
                "💡 AWS Access Keys Guide:",
                " - Access Key ID: Found in IAM > Users > Security Credentials.",
                " - Secret Key: Only visible when the key is first created.",
                " - Default Region: Your primary deployment region (e.g., us-west-2)."
            ]
        ))
        
    elif provider == "azure":
        options.append(LoginOption(
            id="az_standard",
            name="Standard Browser Login",
            command="az login",
            description="Launches a browser window for a standard Microsoft sign-in.",
            guide=[
                "💡 Azure Browser Login:",
                " - Success: Return here ONLY after 'Login successful' appears in browser.",
                " - Tenants: If you have many, run 'az account set' after this flow."
            ],
            is_recommended=True
        ))
        options.append(LoginOption(
            id="az_device",
            name="Device Code Login",
            command="az login --use-device-code",
            description="Use for servers or environments where an auto-browser can't open.",
            guide=[
                "💡 Azure Device Code Flow:",
                " - Code: Copy the code shown in the terminal.",
                " - Link: Go to https://microsoft.com/devicelogin on any device.",
                " - Entry: Paste the code there to complete authentication."
            ]
        ))

    elif provider == "gcp":
        options.append(LoginOption(
            id="gcp_standard",
            name="Standard Browser Login",
            command="gcloud auth login",
            description="Google-standard OAuth2 login flow in your web browser.",
            guide=[
                "💡 GCP Auth Guide:",
                " - Account: Select the Google account you use for projects.",
                " - Authorization: Grant the CLI permissions when prompted."
            ],
            is_recommended=True
        ))
    
    return options

def get_login_command(provider: str) -> Optional[str]:
    """Fallback for backward compatibility. Returns the recommended command."""
    options = get_login_options(provider)
    for opt in options:
        if opt.is_recommended:
            return opt.command
    return options[0].command if options else None

def get_terminal_guide(provider: str) -> List[str]:
    """Fallback for backward compatibility. Returns the recommended guide."""
    options = get_login_options(provider)
    for opt in options:
        if opt.is_recommended:
            return opt.guide
    return options[0].guide if options else []

def discover_aws_profiles() -> List[str]:
    """
    Parses ~/.aws/config and ~/.aws/credentials to find all configured AWS profiles.
    Returns a list of profile names.
    """
    profiles = set()
    aws_dir = Path.home() / ".aws"
    
    # Try reading via CLI first (safest for complex SSO configs)
    try:
        result = subprocess.run(
            ["aws", "configure", "list-profiles"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            profiles.update(line.strip() for line in result.stdout.splitlines() if line.strip())
            return list(profiles)
    except Exception as e:
        debug(f"Failed to run aws configure list-profiles: {e}")

    # Fallback to manual file parsing
    for file_name in ["config", "credentials"]:
        file_path = aws_dir / file_name
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("[") and line.endswith("]"):
                            profile_name = line[1:-1]
                            if profile_name.startswith("profile "):
                                profile_name = profile_name[8:]
                            profiles.add(profile_name)
            except Exception as e:
                error(f"Error reading AWS {file_name}: {e}")

    # If nothing found but files exist, default might be the only one
    if not profiles and (aws_dir / "credentials").exists():
        profiles.add("default")
        
    return list(profiles)

def discover_azure_subscriptions() -> List[Dict[str, str]]:
    """
    Runs `az account list` to fetch all available Azure subscriptions.
    Returns a list of dictionaries with keys: 'name', 'id', 'isDefault'
    """
    subs = []
    try:
        result = subprocess.run(
            ["az", "account", "list", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for item in data:
                subs.append({
                    "name": item.get("name", "Unknown"),
                    "id": item.get("id", ""),
                    "isDefault": item.get("isDefault", False)
                })
    except Exception as e:
        error(f"Failed to discover Azure subscriptions: {e}")

    return subs

def discover_gcp_projects() -> List[Dict[str, str]]:
    """
    Runs `gcloud projects list` to fetch available GCP projects.
    Returns a list of dictionaries with project details.
    """
    projects = []
    try:
        result = subprocess.run(
            ["gcloud", "projects", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            for item in data:
                projects.append({
                    "name": item.get("name", ""),
                    "projectId": item.get("projectId", "")
                })
    except Exception as e:
        error(f"Failed to discover GCP projects: {e}")
        
    return projects
