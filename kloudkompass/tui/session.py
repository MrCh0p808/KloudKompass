# kloudkompass/tui/session.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Immutable session state for TUI. Each step returns a new session
# instance - no in-place mutation allowed per Master Brief.

from dataclasses import dataclass, replace
from typing import Optional, Dict, Any, Tuple


@dataclass(frozen=True)
class SessionState:
    """
    Immutable session state across TUI screens.
    
    This is a frozen dataclass - all fields are read-only after creation.
    To update state, use the with_* methods which return new instances.
    
    Invariant:
        - No in-place mutation allowed
        - Each step returns a new session instance
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
    
    # Note: last_results and data dict removed because frozen dataclass
    # cannot have mutable default values. Store results separately.
    
    def with_provider(self, provider: str) -> "SessionState":
        """Return new session with updated provider."""
        return replace(self, provider=provider)
    
    def with_profile(self, profile: str) -> "SessionState":
        """Return new session with updated profile."""
        return replace(self, profile=profile)
    
    def with_region(self, region: str) -> "SessionState":
        """Return new session with updated region."""
        return replace(self, region=region)
    
    def with_dates(self, start_date: str, end_date: str) -> "SessionState":
        """Return new session with updated date range."""
        return replace(self, start_date=start_date, end_date=end_date)
    
    def with_breakdown(self, breakdown: str) -> "SessionState":
        """Return new session with updated breakdown."""
        return replace(self, breakdown=breakdown)
    
    def with_threshold(self, threshold: float) -> "SessionState":
        """Return new session with updated threshold."""
        return replace(self, threshold=threshold)
    
    def with_output_format(self, output_format: str) -> "SessionState":
        """Return new session with updated output format."""
        return replace(self, output_format=output_format)
    
    def with_error(self, error: str) -> "SessionState":
        """Return new session with updated error."""
        return replace(self, last_error=error)
    
    def with_debug(self, debug_mode: bool) -> "SessionState":
        """Return new session with updated debug mode."""
        return replace(self, debug_mode=debug_mode)
    
    def reset_cost_options(self) -> "SessionState":
        """Return new session with cost options cleared."""
        return replace(
            self,
            start_date=None,
            end_date=None,
            breakdown=None,
            threshold=None,
        )
    
    def reset_all(self) -> "SessionState":
        """Return fresh session with all defaults."""
        return SessionState(debug_mode=self.debug_mode)
    
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


# Global session instance - immutable, replaced on each update
_session: Optional[SessionState] = None


def get_session() -> SessionState:
    """
    Get the current session state.
    
    On first access, auto-loads defaults from config_manager so that
    region/profile/provider are populated from saved preferences.
    """
    global _session
    if _session is None:
        from kloudkompass.config_manager import load_config
        config = load_config()
        _session = SessionState(
            provider=config.get("default_provider", "aws"),
            region=config.get("default_region"),
            profile=config.get("default_profile"),
        )
    return _session


def update_session(new_session: SessionState) -> SessionState:
    """
    Replace the global session with a new instance.
    
    This is the only way to update session state. The session is
    immutable, so this always replaces the entire instance.
    """
    global _session
    _session = new_session
    return _session


def reset_session() -> SessionState:
    """Create a fresh session."""
    global _session
    _session = SessionState()
    return _session
