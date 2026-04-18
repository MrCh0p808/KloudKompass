# kloudkompass/gcp/inventory.py
# ---------------------------
# GCP inventory module stub.
#
# To implement:
# 1. List VMs: gcloud compute instances list
# 2. List storage: gcloud storage buckets list
# 3. List disks: gcloud compute disks list
# 4. Handle projects: gcloud config get-value project

from typing import List


class GCPInventoryProvider:
    """GCP inventory provider stub."""
    
    provider_name = "GCP"
    cli_command = "gcloud"
    
    def list_compute_instances(self) -> List[dict]:
        """List GCP Compute Engine instances."""
        raise NotImplementedError("GCP compute inventory not yet implemented")
    
    def list_storage_buckets(self) -> List[dict]:
        """List GCP Cloud Storage buckets."""
        raise NotImplementedError("GCP storage inventory not yet implemented")
