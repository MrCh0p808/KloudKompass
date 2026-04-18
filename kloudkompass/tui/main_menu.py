# kloudkompass/tui/main_menu.py
# ---------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Main menu and TUI launcher. Entry point for interactive mode.
# Phase 3: Expanded from 4 to 10 menu items.

from typing import Optional

from kloudkompass.tui.screens import Screen, BRAND_TITLE, confirm_quit
from kloudkompass.tui.session import get_session, reset_session
from kloudkompass.tui.navigation import get_navigator, reset_navigator
from kloudkompass.tui.cost_menu import CostWizardScreen
from kloudkompass.tui.compute_menu import ComputeMenuScreen
from kloudkompass.tui.network_menu import NetworkMenuScreen
from kloudkompass.tui.storage_menu import StorageMenuScreen
from kloudkompass.tui.iam_menu import IAMMenuScreen
from kloudkompass.tui.database_menu import DatabaseMenuScreen
from kloudkompass.tui.inventory_menu import InventoryWizardScreen
from kloudkompass.tui.security_menu import SecurityWizardScreen
from kloudkompass.tui.settings_menu import SettingsMenuScreen
from kloudkompass.tui.doctor import print_doctor_report
from kloudkompass.tui.footer import render_footer


# Menu options - Phase 3: 10 items
# Exit is handled globally via q/Q navigation
MENU_OPTIONS = [
    ("1", "💰 Cost Query", "cost"),
    ("2", "🖥️  Compute (EC2)", "compute"),
    ("3", "🌐 Networking (VPC)", "network"),
    ("4", "📦 Storage (S3/EBS)", "storage"),
    ("5", "🔐 IAM (Users/Roles)", "iam"),
    ("6", "🗄️  Database (RDS/DDB)", "database"),
    ("7", "📋 Inventory", "inventory"),
    ("8", "🛡️  Security Audit", "security"),
    ("9", "🩺 Doctor (Health Check)", "doctor"),
    ("0", "⚙️  Settings", "settings"),
]


class MainMenuScreen(Screen):
    """
    Main menu for the TUI.
    
    This is the root screen that branches to all wizards.
    Phase 3: 10 items covering all cloud operations.
    Exit is NOT a menu option - use Q to quit.
    """
    
    title = BRAND_TITLE
    
    def render(self) -> None:
        """Render menu options (header handled by mount)."""
        print("Welcome to Kloud Kompass. Select an option below.")
        print()
        
        for key, label, _ in MENU_OPTIONS:
            print(f"  {key}. {label}")
        
        self.print_nav_hint()
    
    def handle_input(self) -> Optional[Screen]:
        result = self.get_input()
        
        # Handle navigation intents
        if result.is_quit:
            if confirm_quit():
                return "exit"
            return None  # User cancelled, stay on menu
        
        if result.is_back:
            # Back at root = quit confirmation
            if confirm_quit():
                return "exit"
            return None
        
        # Route to screens
        choice = result.raw
        action = None
        for key, _, act in MENU_OPTIONS:
            if choice == key:
                action = act
                break
        
        if action is None:
            print("\nInvalid choice. Try again.\n")
            input("Press Enter to continue...")
            return None
        
        screen_map = {
            "cost": CostWizardScreen,
            "compute": ComputeMenuScreen,
            "network": NetworkMenuScreen,
            "storage": StorageMenuScreen,
            "iam": IAMMenuScreen,
            "database": DatabaseMenuScreen,
            "inventory": InventoryWizardScreen,
            "security": SecurityWizardScreen,
            "settings": SettingsMenuScreen,
        }
        
        if action == "doctor":
            self._run_doctor()
            return None
        
        screen_class = screen_map.get(action)
        if screen_class:
            return screen_class()
        
        return None
    
    def _run_doctor(self) -> None:
        """Run the doctor command and wait for user."""
        print_doctor_report()
        input("Press Enter to return to menu...")


def launch() -> None:
    """
    Launch the TUI main menu.
    
    This is the entry point for interactive mode. Sets up the session
    and navigation, then runs the main loop.
    
    Rendering Model (Phase 2.6):
        launch() owns: attribution footer (once at exit)
        mount()  owns: screen clear + header (via print_header)
        render() owns: dynamic content only
    
    Navigation Model (Phase 2.6):
        q/Q -> quit with confirmation
        b/B -> back one level
        Back at root -> quit confirmation
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
                # At root with no current screen = exit
                break
    
    except KeyboardInterrupt:
        pass
    
    finally:
        # Attribution footer - single point of rendering
        print()
        render_footer()
        print("  Goodbye.")
        print()
