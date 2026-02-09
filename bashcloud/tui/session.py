# bashcloud/tui/session.py
# -------------------------
# all session state kept here in a dataclass. This persists across
# screens in the TUI so users do not have to re-enter values when
# navigating back and forth.

from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class SessionState:
    """
    Persistent state across TUI screens.
    
    Stores all user selections here so when they navigate back, their
    previous choices are preserved. This also lets me auto-fill prompts
    with last-used values.
    """
    
    # Provider selection
    provider: Optional[str] = None
    profile: Optional[str] = None
    region: Optional[str] = None
    
    # Date range
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    # Cost options
    breakdown: Optional[str] = None
    threshold: Optional[float] = None
    output_format: Optional[str] = None
    
    # General state
    debug_mode: bool = False
    last_error: Optional[str] = None
    last_results: Optional[list] = None
    
    # Arbitrary storage for screen-specific data
    data: Dict[str, Any] = field(default_factory=dict)
    
    def reset_cost_options(self) -> None:
        """Clear cost-related options for a fresh query."""
        self.start_date = None
        self.end_date = None
        self.breakdown = None
        self.threshold = None
        self.last_results = None
    
    def reset_all(self) -> None:
        """Reset all session state."""
        self.provider = None
        self.profile = None
        self.region = None
        self.reset_cost_options()
        self.output_format = None
        self.last_error = None
        self.data.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "provider": self.provider,
            "profile": self.profile,
            "region": self.region,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "breakdown": self.breakdown,
            "threshold": self.threshold,
            "output_format": self.output_format,
        }


# Global session instance
_session: Optional[SessionState] = None


def get_session() -> SessionState:
    """
    Get the global session state.
    
    a singleton pattern here ensures all screens share the same state.
    """
    global _session
    if _session is None:
        _session = SessionState()
    return _session


def reset_session() -> SessionState:
    """Create a fresh session."""
    global _session
    _session = SessionState()
    return _session
