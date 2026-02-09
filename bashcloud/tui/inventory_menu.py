# bashcloud/tui/inventory_menu.py
# --------------------------------
# Placeholder for inventory wizard. Will expand this when the inventory
# providers are implemented.

from typing import Optional

from bashcloud.tui.screens import Screen


class InventoryWizardScreen(Screen):
    """
    Inventory query wizard.
    
    This is a placeholder that will be expanded when inventory providers
    are implemented.
    """
    
    title = "Inventory Query"
    
    def display(self) -> None:
        self.clear_screen()
        self.print_header()
        
        print("Inventory module is not yet implemented.")
        print()
        print("Planned features:")
        print("  - EC2 instance inventory")
        print("  - S3 bucket listing")
        print("  - RDS database inventory")
        print("  - Cross-cloud resource unification")
        print()
    
    def handle_input(self) -> Optional[Screen]:
        print()
        input("Press Enter to return to main menu...")
        return "back"
