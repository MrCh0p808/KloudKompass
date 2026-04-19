# kloudkompass/core/workspace_registry.py
# -----------------------------------
# Core registry for the Multi-Kernel OS.
# Manages discovery of cloud accounts and tracks the 10-tab active limit.

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import uuid

from kloudkompass.config_manager import load_config, save_config, get_config_value, set_config_value
from kloudkompass.core.auth_manager import discover_aws_profiles, discover_azure_subscriptions
from kloudkompass.core.provider_factory import get_provider_list

@dataclass
class WorkspaceContext:
    """
    State for a single isolated cloud account kernel.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider: str = "aws"
    profile: Optional[str] = None
    region: Optional[str] = None
    last_view: str = "cost"
    is_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "provider": self.provider,
            "profile": self.profile,
            "region": self.region,
            "last_view": self.last_view,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceContext":
        return cls(**data)


class WorkspaceRegistry:
    """
    Singleton registry to manage cloud account discovery and tab limits.
    """
    
    MAX_ACTIVE_TABS = 10
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.workspaces: Dict[str, WorkspaceContext] = {}
        self._load_from_config()
        self._initialized = True

    def _load_from_config(self) -> None:
        """Load persisted workspaces from config.toml."""
        saved_data = get_config_value("workspaces", [])
        for item in saved_data:
            ws = WorkspaceContext.from_dict(item)
            self.workspaces[ws.id] = ws

    def save_to_config(self) -> None:
        """Persist current workspace states."""
        data = [ws.to_dict() for ws in self.workspaces.values()]
        set_config_value("workspaces", data)

    def discover_all(self) -> List[WorkspaceContext]:
        """
        Scan all providers for configured identities. Returns a list of the 
        newly discovered contexts not already in the registry.
        """
        discovered = []
        
        # AWS Profiles
        for profile in discover_aws_profiles():
            # Check if we already have this context (duplicate check)
            if not any(w.profile == profile and w.provider == "aws" for w in self.workspaces.values()):
                ws = WorkspaceContext(provider="aws", profile=profile)
                discovered.append(ws)
                
        # Azure Subscriptions
        for sub in discover_azure_subscriptions():
            sub_id = sub.get("id")
            if not any(w.profile == sub_id and w.provider == "azure" for w in self.workspaces.values()):
                ws = WorkspaceContext(provider="azure", profile=sub_id)
                discovered.append(ws)
                
        return discovered

    def add_workspace(self, ws: WorkspaceContext) -> bool:
        """Add a discovered workspace to the registry."""
        if ws.id not in self.workspaces:
            self.workspaces[ws.id] = ws
            return True
        return False

    def get_active_workspaces(self) -> List[WorkspaceContext]:
        """Return the current set of mounted kernels."""
        return [ws for ws in self.workspaces.values() if ws.is_active]

    def activate_workspace(self, workspace_id: str) -> bool:
        """
        Attempt to mount a workspace. Enforces the 10-tab limit.
        Returns False if a replacement selection is required.
        """
        if workspace_id not in self.workspaces:
            return False
            
        active = self.get_active_workspaces()
        if len(active) >= self.MAX_ACTIVE_TABS:
            return False  # Trigger UI replacement modal
            
        self.workspaces[workspace_id].is_active = True
        return True

    def deactivate_workspace(self, workspace_id: str) -> None:
        """Unmount a workspace to free a slot."""
        if workspace_id in self.workspaces:
            self.workspaces[workspace_id].is_active = False

    def switch_active(self, to_deactivate_id: str, to_activate_id: str) -> bool:
        """Atomic swap of two workspaces (Replacement logic)."""
        if to_deactivate_id in self.workspaces and to_activate_id in self.workspaces:
            self.deactivate_workspace(to_deactivate_id)
            return self.activate_workspace(to_activate_id)
        return False
