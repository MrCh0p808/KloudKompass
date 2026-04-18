# kloudkompass/core/auth_manager.py
# --------------------------------
# Handles Interactive Login Flows for Cloud Interfaces and parses
# active Identity contexts (Subscriptions, Profiles, Projects).

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Optional

from kloudkompass.utils.logger import error, debug

def get_login_command(provider: str) -> Optional[str]:
    """Returns the native interactive command used to authenticate the provider."""
    provider = provider.lower()
    if provider == "aws":
        return "aws configure sso"
    elif provider == "azure":
        return "az login"
    elif provider == "gcp":
        return "gcloud auth login"
    return None

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
