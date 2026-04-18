# kloudkompass/tui/provider_setup_screen.py
# ----------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Provider setup TUI screen — Phase 2.6 lifecycle-compliant.
# All user interaction goes through Screen.get_input().

from typing import Optional

from kloudkompass.tui.screens import Screen, BRAND_TITLE, NAV_HINT
from kloudkompass.tui.provider_setup import (
    ProviderSetupResult,
    check_provider_ready,
    get_setup_instructions,
    persist_provider_choice,
)


class ProviderSetupScreen(Screen):
    """
    Provider setup screen — guides user through CLI and credential setup.
    
    Lifecycle-compliant:
        - mount(): prints header and step indicator
        - render(): shows check results and instructions
        - handle_input(): uses get_input() exclusively
    
    Does not loop, auto-retry, or mutate session state implicitly.
    """
    
    title = BRAND_TITLE
    
    def __init__(self, provider: str, result: Optional[ProviderSetupResult] = None):
        super().__init__()
        self.provider = provider.lower().strip()
        self.setup_result = result or check_provider_ready(self.provider)
        self.setup_data = get_setup_instructions(self.provider)
    
    def mount(self):
        """Print header — called once."""
        if self._mounted:
            return
        self._mounted = True
        self.print_header()
    
    def render(self):
        """Render setup status and instructions."""
        provider_upper = self.provider.upper()
        
        print()
        print("=" * 50)
        print(f"  {provider_upper} Provider Setup")
        print("=" * 50)
        print()
        
        # Step 1: CLI check
        print("Step 1: CLI installation")
        print()
        
        if not self.setup_data["cli_installed"]:
            print(f"[!!] {provider_upper} CLI not found in PATH.")
            print()
            print("Installation instructions:")
            print("-" * 40)
            print(self.setup_data["install_instructions"])
            print("-" * 40)
            print()
            print("After installing, restart Kloud Kompass and try again.")
            print()
            print(NAV_HINT)
            return
        
        print(f"[OK] {provider_upper} CLI is installed.")
        print()
        
        # Step 2: Credential check
        print("Step 2: Credentials")
        print()
        
        if not self.setup_data["creds_valid"]:
            print(f"[!!] {provider_upper} credentials not configured.")
            print()
            if self.setup_data["cred_error"]:
                print(f"Error: {self.setup_data['cred_error']}")
                print()
            
            # Show config steps
            steps = self.setup_data["config_steps"]
            if steps:
                print(f"To configure {provider_upper} credentials:")
                for i, step in enumerate(steps, 1):
                    print(f"  {i}. {step}")
            
            print()
            print("After configuring, restart Kloud Kompass and try again.")
            print()
            print(NAV_HINT)
            return
        
        print(f"[OK] {provider_upper} credentials are valid.")
        print()
        
        # Both checks passed
        print("-" * 50)
        print(f"  {provider_upper} is ready to use!")
        print("-" * 50)
        print()
        
        # Persist choice
        persist_provider_choice(self.provider)
        
        # Update result to success
        self.setup_result = ProviderSetupResult(success=True, provider=self.provider)
        
        print(NAV_HINT)
    
    def handle_input(self) -> Optional["Screen"]:
        """
        Handle input using get_input() — contract-compliant.
        
        Returns:
            'back' to go back, 'exit' to quit, None to stay.
        """
        result = self.get_input("Press Enter to go back: ")
        
        if result.is_quit:
            from kloudkompass.tui.screens import confirm_quit
            if confirm_quit():
                return "exit"
            return None
        
        if result.is_back:
            return "back"
        
        # Any other input (including Enter) → go back
        return "back"
    
    def get_result(self) -> ProviderSetupResult:
        """Return the setup result after screen interaction."""
        return self.setup_result
