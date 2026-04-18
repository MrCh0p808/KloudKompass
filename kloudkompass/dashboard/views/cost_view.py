# kloudkompass/dashboard/views/cost_view.py
# ---------------------------------------
# the cost dashboard view This combines the filter
# panel with the cost table for a complete cost analysis experience.

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Input
from textual.worker import Worker, get_current_worker
from textual.binding import Binding
import re

from kloudkompass.dashboard.widgets.cost_table import CostTable
from kloudkompass.dashboard.widgets.filter_panel import FilterPanel
from kloudkompass.dashboard.widgets.status_bar import StatusBar
from kloudkompass.dashboard.widgets.cost_chart import CostChart
from kloudkompass.core import get_cost_provider, KloudKompassError
import asyncio


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
        width: 25%;
        min-width: 25;
        max-width: 40;
        height: 100%;
    }
    
    CostView .results-container {
        width: 1fr;
        height: 100%;
        padding: 1;
    }
    
    CostView .search-bar {
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Filters"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_records = []
        self.current_search = ""
    
    def compose(self) -> ComposeResult:
        """Build the cost view layout."""
        yield Static("Cost Analysis", classes="view-title")
        
        with Horizontal():
            with Vertical(classes="filter-container"):
                yield FilterPanel(id="filter_panel")
            
            with Vertical(classes="results-container"):
                yield Input(placeholder="Search Results... ( / to focus, Esc to clear )", id="cost_search_input")
                yield CostTable(id="cost_table")
                yield CostChart(id="cost_chart")
        
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
        
        cost_table = self.query_one("#cost_table", CostTable)
        cost_table.loading = True
        
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
        status_bar = self.query_one("#status_bar", StatusBar)
        cost_table = self.query_one("#cost_table", CostTable)
        cost_chart = self.query_one("#cost_chart", CostChart)
        
        try:
            cost_provider = get_cost_provider(provider)
            
            self.all_records = await asyncio.to_thread(
                cost_provider.get_cost,
                start_date=start_date,
                end_date=end_date,
                breakdown=breakdown,
            )
            
            if threshold > 0:
                self.all_records = cost_provider.filter_by_threshold(self.all_records, threshold)
            
            # Load saved search on first results fetch
            from kloudkompass.config_manager import get_config_value
            if not self.current_search:
                saved = get_config_value("cost_saved_search", "")
                if saved:
                    self.current_search = saved
                    self.query_one("#cost_search_input", Input).value = saved

            self.call_from_thread(self._render_results)
            self.call_from_thread(status_bar.set_status, f"{provider.upper()} costs loaded")
            
        except KloudKompassError as e:
            self.call_from_thread(cost_table.clear_records)
            try:
                self.call_from_thread(self.query_one("#cost_chart", CostChart).clear_data)
            except Exception: pass
            self.call_from_thread(status_bar.set_status, f"Error: {e}")
        except Exception as e:
            self.call_from_thread(cost_table.clear_records)
            try:
                self.call_from_thread(self.query_one("#cost_chart", CostChart).clear_data)
            except Exception: pass
            self.call_from_thread(status_bar.set_status, f"Unexpected error: {e}")
        finally:
            self.call_from_thread(setattr, cost_table, "loading", False)
            
    def _render_results(self) -> None:
        """Render the filtered records to table and chart."""
        cost_table = self.query_one("#cost_table", CostTable)
        cost_chart = self.query_one("#cost_chart", CostChart)
        status_bar = self.query_one("#status_bar", StatusBar)
        
        # Save search to config
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("cost_saved_search", self.current_search)
        except Exception: pass

        filtered = []
        for r in self.all_records:
            search_str = f"{r.service} {r.period} {r.resource_id or ''}".lower()
            if self.current_search:
                try:
                    if not re.search(self.current_search, search_str): continue
                except re.error:
                    if self.current_search not in search_str: continue
            filtered.append(r)
            
        # Update table
        cost_table.load_records(filtered)
        status_bar.set_results(len(filtered), sum(r.amount for r in filtered))
        
        # Update chart
        if filtered:
            by_date = {}
            for r in filtered:
                by_date[r.period] = by_date.get(r.period, 0.0) + r.amount
            chart_data = sorted([(k, v) for k, v in by_date.items()])
            cost_chart.load_data(chart_data)
        else:
            cost_chart.clear_data()

