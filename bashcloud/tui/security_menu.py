# bashcloud/tui/security_menu.py
# -------------------------------
# Placeholder for security wizard. Will expand this when the security
# providers are implemented.

from typing import Optional

from bashcloud.tui.screens import Screen


class SecurityWizardScreen(Screen):
    """
    Security audit wizard.
    
    This is a placeholder that will be expanded when security providers
    are implemented.
    """
    
    title = "Security Audit"
    
    def display(self) -> None:
        self.clear_screen()
        self.print_header()
        
        print("Security module is not yet implemented.")
        print()
        print("Planned features:")
        print("  - IAM policy analyzer")
        print("  - Security group audit")
        print("  - Public resource detection")
        print("  - Compliance checks")
        print()
    
    def handle_input(self) -> Optional[Screen]:
        print()
        input("Press Enter to return to main menu...")
        return "back"
