# kloudkompass/tui/cost_menu.py
# ---------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Cost wizard flow with immutable session updates.
# Phase 2.6: Uses get_input() for navigation model.

from typing import Optional

from kloudkompass.tui.screens import Screen, BRAND_TITLE
from kloudkompass.tui.session import update_session
from kloudkompass.tui.prompts import (
    select_provider,
    input_date_range,
    select_breakdown,
    input_threshold,
    confirm_action,
)
from kloudkompass.tui.provider_setup import ensure_provider_configured
from kloudkompass.core import get_cost_provider, KloudKompassError
from kloudkompass.utils.formatters import format_records, OutputFormat


class CostWizardScreen(Screen):
    """
    Cost query wizard - step by step flow.
    
    Flow: Provider -> Dates -> Breakdown -> Threshold -> Confirm -> Execute
    
    Invariants:
        - All session updates use immutable with_* methods
        - Uses get_input() for navigation
    """
    
    title = "Cost Query Wizard"
    
    def render(self) -> None:
        """Render current wizard state (header handled by mount)."""
        print("This wizard will help you query cloud costs.")
        print()
        
        # Show current selections
        if self.session.provider:
            print(f"  Provider: {self.session.provider.upper()}")
        if self.session.start_date and self.session.end_date:
            print(f"  Date Range: {self.session.start_date} to {self.session.end_date}")
        if self.session.breakdown:
            print(f"  Breakdown: {self.session.breakdown}")
        if self.session.threshold is not None:
            print(f"  Threshold: ${self.session.threshold:.2f}")
        
        print()
        self.print_nav_hint()
    
    def handle_input(self) -> Optional[Screen]:
        # Step 1: Provider selection
        if not self.session.provider:
            provider, action = select_provider(self.session.provider)
            if action == "back":
                return "back"
            if action == "quit":
                return "exit"
            
            # Phase 2.6: Gate — check provider readiness
            gate_result = ensure_provider_configured(provider)
            if not gate_result.success:
                from kloudkompass.tui.provider_setup_screen import ProviderSetupScreen
                return ProviderSetupScreen(provider, gate_result)
            
            update_session(self.session.with_provider(provider))
            return None  # Redisplay
        
        # Step 2: Date range
        if not self.session.start_date or not self.session.end_date:
            start, end, action = input_date_range(
                self.session.start_date,
                self.session.end_date,
            )
            if action == "back":
                update_session(self.session.with_provider(None))
                return None
            if action == "quit":
                return "exit"
            if action == "retry":
                return None
            update_session(self.session.with_dates(start, end))
            return None
        
        # Step 3: Breakdown type
        if not self.session.breakdown:
            breakdown, action = select_breakdown(self.session.breakdown)
            if action == "back":
                update_session(self.session.with_dates(None, None))
                return None
            if action == "quit":
                return "exit"
            update_session(self.session.with_breakdown(breakdown))
            return None
        
        # Step 4: Threshold
        if self.session.threshold is None:
            threshold, action = input_threshold(self.session.threshold)
            if action == "back":
                update_session(self.session.with_breakdown(None))
                return None
            if action == "quit":
                return "exit"
            if action == "retry":
                return None
            update_session(self.session.with_threshold(threshold))
            return None
        
        # Step 5: Confirm and execute
        return self._execute_query()
    
    def _execute_query(self) -> Optional[Screen]:
        """Execute the cost query with collected parameters."""
        print()
        self.print_divider()
        print()
        print("Ready to execute query:")
        print(f"  Provider: {self.session.provider.upper()}")
        print(f"  Date Range: {self.session.start_date} to {self.session.end_date}")
        print(f"  Breakdown: {self.session.breakdown}")
        print(f"  Threshold: ${self.session.threshold:.2f}")
        print()
        
        if not confirm_action("Execute query?"):
            # User cancelled, go back to threshold
            update_session(self.session.with_threshold(None))
            return None
        
        print()
        print("Fetching cost data...")
        print()
        
        try:
            provider = get_cost_provider(self.session.provider)
            
            records = provider.get_cost(
                start_date=self.session.start_date,
                end_date=self.session.end_date,
                breakdown=self.session.breakdown,
                profile=self.session.profile,
                region=self.session.region,
            )
            
            if self.session.threshold > 0:
                records = provider.filter_by_threshold(records, self.session.threshold)
            
            if not records:
                print("No cost data found for the specified criteria.")
            else:
                title = f"{self.session.provider.upper()} Costs - {self.session.breakdown.capitalize()}"
                format_records(records, OutputFormat.TABLE, title=title)
            
            print()
            self.print_divider()
            
            # Ask what to do next
            print()
            print("What would you like to do?")
            print("  1. Run another query")
            print("  2. Return to main menu")
            print()
            
            result = self.get_input("Enter choice [2]: ")
            
            if result.is_quit:
                return "exit"
            if result.is_back:
                return "back"
            
            if result.raw == "1":
                update_session(self.session.reset_cost_options())
                return None  # Restart wizard
            else:
                return "back"
            
        except KloudKompassError as e:
            self.print_error(str(e))
            update_session(self.session.with_error(str(e)))
            
            print()
            print("Press Enter to try again...")
            self.get_input("")
            
            # Go back to provider selection
            new_session = self.session.reset_cost_options()
            update_session(new_session.with_provider(None))
            return None
        
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return "back"
