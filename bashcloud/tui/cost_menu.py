# bashcloud/tui/cost_menu.py
# ---------------------------
# the cost wizard flow This is a step-by-step guided
# experience that collects all the parameters needed for a cost query.

from typing import Optional

from bashcloud.tui.screens import Screen
from bashcloud.tui.prompts import (
    select_provider,
    input_date_range,
    select_breakdown,
    input_threshold,
    confirm_action,
)
from bashcloud.core import get_cost_provider, BashCloudError
from bashcloud.utils.formatters import format_records, OutputFormat


class CostWizardScreen(Screen):
    """
    Cost query wizard - step by step flow.
    
    Flow: Provider -> Dates -> Breakdown -> Threshold -> Confirm -> Execute
    """
    
    title = "Cost Query Wizard"
    
    def display(self) -> None:
        self.clear_screen()
        self.print_header()
        
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
    
    def handle_input(self) -> Optional[Screen]:
        # Step 1: Provider selection
        if not self.session.provider:
            provider, action = select_provider(self.session.provider)
            if action == "back":
                return "back"
            self.session.provider = provider
            return None  # Redisplay
        
        # Step 2: Date range
        if not self.session.start_date or not self.session.end_date:
            start, end, action = input_date_range(
                self.session.start_date,
                self.session.end_date,
            )
            if action == "back":
                self.session.provider = None
                return None
            if action == "retry":
                return None
            self.session.start_date = start
            self.session.end_date = end
            return None
        
        # Step 3: Breakdown type
        if not self.session.breakdown:
            breakdown, action = select_breakdown(self.session.breakdown)
            if action == "back":
                self.session.start_date = None
                self.session.end_date = None
                return None
            self.session.breakdown = breakdown
            return None
        
        # Step 4: Threshold
        if self.session.threshold is None:
            threshold, action = input_threshold(self.session.threshold)
            if action == "back":
                self.session.breakdown = None
                return None
            if action == "retry":
                return None
            self.session.threshold = threshold
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
            self.session.threshold = None
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
            
            self.session.last_results = records
            
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
            
            choice = input("Enter choice [2]: ").strip()
            
            if choice == "1":
                self.session.reset_cost_options()
                return None  # Restart wizard
            else:
                return "back"
            
        except BashCloudError as e:
            self.print_error(str(e))
            self.session.last_error = str(e)
            
            print()
            print("Press Enter to try again...")
            input()
            
            # Go back to provider selection
            self.session.reset_cost_options()
            self.session.provider = None
            return None
        
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return "back"
