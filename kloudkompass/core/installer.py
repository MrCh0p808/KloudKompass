# kloudkompass/core/installer.py
# ----------------------------
# Evaluates host OS and generates native package installation commands
# for AWS, Azure, and GCP CLIs.

import platform
import shutil
from typing import Optional

def get_os_type() -> str:
    """Returns simplified OS type: 'linux', 'darwin', or 'windows'."""
    system = platform.system().lower()
    return system

def is_cli_installed(command: str) -> bool:
    return shutil.which(command) is not None

def get_install_command(provider: str) -> Optional[str]:
    """
    Returns the exact shell string to run OS-native installation
    for the requested provider based on the current system.
    """
    os_type = get_os_type()
    
    if provider == "aws":
        if os_type == "linux":
            # Installs AWS CLI v2 via official script
            return "curl 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip' -o 'awscliv2.zip' && unzip awscliv2.zip && sudo ./aws/install"
        elif os_type == "darwin":
            return "curl 'https://awscli.amazonaws.com/AWSCLIV2.pkg' -o 'AWSCLIV2.pkg' && sudo installer -pkg AWSCLIV2.pkg -target /"
        elif os_type == "windows":
            return "msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi"
            
    elif provider == "azure":
        if os_type == "linux":
            return "curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
        elif os_type == "darwin":
            return "brew update && brew install azure-cli"
        elif os_type == "windows":
            return "Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'"
            
    elif provider == "gcp":
        if os_type in ["linux", "darwin"]:
            return "curl https://sdk.cloud.google.com | bash"
        elif os_type == "windows":
            return "(New-Object Net.WebClient).DownloadFile('https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe', 'GoogleCloudSDKInstaller.exe'); Start-Process 'GoogleCloudSDKInstaller.exe' -Wait"

    return None
