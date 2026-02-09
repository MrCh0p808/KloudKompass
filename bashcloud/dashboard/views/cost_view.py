# bashcloud/dashboard/views/cost_view.py
# ---------------------------------------
# the cost dashboard view This combines the filter
# panel with the cost table for a complete cost analysis experience.

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static
from textual.worker import Worker, get_current_worker

from bashcloud.dashboard.widgets.cost_table import CostTable
from bashcloud.dashboard.widgets.filter_panel import FilterPanel
from bashcloud.dashboard.widgets.status_bar import StatusBar
from bashcloud.core import get_cost_provider, BashCloudError


class CostView(Container):
    """
    Cost dashboard view.
    
    Layout:
    - Left: Filter panel
    - Right: Cost results table
    - Bottom: Status bar
    """
    
    DEFAULT_CSS = """
    CostView {
        height: 100%;
        width: 100%;
    }
    
    CostView > Horizontal {
        height: 1fr;
    }
    
    CostView .filter-container {
        width: 30;
        height: 100%;
    }
    
    CostView .results-container {
        width: 1fr;
        height: 100%;
        padding: 1;
    }
    
    CostView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Build the cost view layout."""
        yield Static("Cost Analysis", classes="view-title")
        
        with Horizontal():
            with Vertical(classes="filter-container"):
                yield FilterPanel(id="filter_panel")
            
            with Vertical(classes="results-container"):
                yield CostTable(id="cost_table")
        
        yield StatusBar(id="status_bar")
    
    def on_filter_panel_query_requested(
        self,
        message: FilterPanel.QueryRequested,
    ) -> None:
        """Handle query request from filter panel."""
        self._run_query(
            provider=message.provider,
            start_date=message.start_date,
            end_date=message.end_date,
            breakdown=message.breakdown,
            threshold=message.threshold,
        )
    
    def _run_query(
        self,
        provider: str,
        start_date: str,
        end_date: str,
        breakdown: str,
        threshold: float,
    ) -> None:
        """Run the cost query asynchronously."""
        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.set_status("Fetching cost data...")
        
        # Run in background worker
        self.run_worker(
            self._fetch_costs(provider, start_date, end_date, breakdown, threshold),
            name="fetch_costs",
            exclusive=True,
        )
    
    async def _fetch_costs(
        self,
        provider: str,
        start_date: str,
        end_date: str,
        breakdown: str,
        threshold: float,
    ) -> None:
        """Background worker to fetch costs."""
        cost_table = self.query_one("#cost_table", CostTable)
        status_bar = self.query_one("#status_bar", StatusBar)
        
        try:
            cost_provider = get_cost_provider(provider)
            
            records = cost_provider.get_cost(
                start_date=start_date,
                end_date=end_date,
                breakdown=breakdown,
            )
            
            if threshold > 0:
                records = cost_provider.filter_by_threshold(records, threshold)
            
            # Update table on main thread
            cost_table.load_records(records)
            status_bar.set_results(len(records), sum(r.amount for r in records))
            status_bar.set_status(f"{provider.upper()} costs loaded")
            
        except BashCloudError as e:
            cost_table.clear_records()
            status_bar.set_status(f"Error: {e}")
        
        except Exception as e:
            cost_table.clear_records()
            status_bar.set_status(f"Unexpected error: {e}")
