# bashcloud/azure/inventory.py
# -----------------------------
# Azure inventory module stub.
#
# To implement:
# 1. List VMs: az vm list
# 2. List storage accounts: az storage account list
# 3. List disks: az disk list
# 4. Handle resource groups and subscriptions

from typing import List


class AzureInventoryProvider:
    """Azure inventory provider stub."""
    
    provider_name = "Azure"
    cli_command = "az"
    
    def list_virtual_machines(self) -> List[dict]:
        """List Azure VMs."""
        raise NotImplementedError("Azure VM inventory not yet implemented")
    
    def list_storage_accounts(self) -> List[dict]:
        """List Azure Storage accounts."""
        raise NotImplementedError("Azure storage inventory not yet implemented")
