# bashcloud/tui/main_menu.py
# ---------------------------
# the main menu and TUI launcher This is the entry
# point for interactive mode.

from typing import Optional

from bashcloud.tui.screens import Screen
from bashcloud.tui.session import get_session, reset_session
from bashcloud.tui.navigation import get_navigator, reset_navigator
from bashcloud.tui.cost_menu import CostWizardScreen
from bashcloud.tui.inventory_menu import InventoryWizardScreen
from bashcloud.tui.security_menu import SecurityWizardScreen
from bashcloud.tui.doctor import print_doctor_report


MENU_OPTIONS = [
    ("1", "Cost Query", "cost"),
    ("2", "Inventory", "inventory"),
    ("3", "Security Audit", "security"),
    ("4", "Doctor (Health Check)", "doctor"),
    ("0", "Exit", "exit"),
]


class MainMenuScreen(Screen):
    """
    Main menu for the TUI.
    
    This is the root screen that branches to all wizards.
    """
    
    title = "BashCloud - Main Menu"
    
    def display(self) -> None:
        self.clear_screen()
        self.print_header()
        
        print("Welcome to BashCloud. Select an option below.")
        print()
        
        for key, label, _ in MENU_OPTIONS:
            print(f"  {key}. {label}")
        
        print()
    
    def handle_input(self) -> Optional[Screen]:
        choice = input("Enter choice: ").strip()
        
        # Find matching option
        action = None
        for key, _, act in MENU_OPTIONS:
            if choice == key:
                action = act
                break
        
        if action is None:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
            return None
        
        if action == "exit":
            return "exit"
        
        if action == "cost":
            return CostWizardScreen()
        
        if action == "inventory":
            return InventoryWizardScreen()
        
        if action == "security":
            return SecurityWizardScreen()
        
        if action == "doctor":
            self._run_doctor()
            return None
        
        return None
    
    def _run_doctor(self) -> None:
        """Run the doctor command and wait for user."""
        self.clear_screen()
        print_doctor_report()
        input("Press Enter to return to menu...")


def launch() -> None:
    """
    Launch the TUI main menu.
    
    This is the entry point for interactive mode. Sets up the session
    and navigation, then run the main loop.
    """
    # Reset state for fresh start
    reset_session()
    navigator = reset_navigator()
    
    # Start at main menu
    main_menu = MainMenuScreen()
    navigator.push(main_menu)
    
    # Main TUI loop
    try:
        while not navigator.should_exit():
            current = navigator.current()
            
            if current is None:
                break
            
            next_screen = current.run()
            
            if next_screen is not None and next_screen != "back" and next_screen != "exit":
                navigator.push(next_screen)
            elif navigator.should_exit():
                break
            elif navigator.depth == 0:
                # Back from main menu = exit
                break
    
    except KeyboardInterrupt:
        pass
    
    finally:
        print("\nGoodbye.")
