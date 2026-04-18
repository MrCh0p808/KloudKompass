# kloudkompass/dashboard/views/doctor_view.py
# -------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Doctor / health check dashboard view.

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, DataTable, Button, Input
from textual.binding import Binding
import re


class DoctorView(Container):
    """
    Environment health check dashboard view.

    Runs all doctor checks and displays pass/fail results.
    """

    DEFAULT_CSS = """
    DoctorView {
        height: 100%;
        width: 100%;
    }

    DoctorView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    DoctorView .status-line {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }

    DoctorView .search-bar {
        dock: top;
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
        self.all_results = []
        self.current_search = ""

    def compose(self) -> ComposeResult:
        yield Static("🩺 Environment Health Checks", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search Checks... ( / to focus, Esc to clear )", id="doctor_search_input")
        yield Button("Run Doctor", id="btn_doctor", variant="success")
        yield DataTable(id="doctor_table")
        yield Static("Press 'Run Doctor' to check your environment.", classes="status-line", id="doctor_status")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "doctor_search_input":
            self.current_search = event.value.strip().lower()
            self._render_doctor()

    def action_focus_search(self) -> None:
        self.query_one("#doctor_search_input").focus()

    def action_clear_search(self) -> None:
        self.query_one("#doctor_search_input", Input).value = ""
        self.current_search = ""
        self._render_doctor()

    def on_mount(self) -> None:
        table = self.query_one("#doctor_table", DataTable)
        table.add_columns("Status", "Check", "Details")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_doctor":
            self._run_doctor()

    def _run_doctor(self) -> None:
        status = self.query_one("#doctor_status", Static)
        status.update("Running health checks...")
        table = self.query_one("#doctor_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_doctor(), name="doctor_check", exclusive=True)

    async def _fetch_doctor(self) -> None:
        status = self.query_one("#doctor_status", Static)
        table = self.query_one("#doctor_table", DataTable)

        try:
            from kloudkompass.tui.doctor import run_doctor
            import asyncio

            # Use asyncio.to_thread to prevent blocking the UI
            self.all_results = await asyncio.to_thread(run_doctor)
            
            # Save search to config logic might not be needed here, or we can just render
            self.call_from_thread(self._render_doctor)

            passed = sum(1 for _, _, p in self.all_results if p)
            failed = len(self.all_results) - passed

            if failed == 0:
                self.call_from_thread(status.update, f"All {passed} checks passed ✓")
            else:
                self.call_from_thread(status.update, f"{passed} passed, {failed} failed")

        except Exception as e:
            self.call_from_thread(status.update, f"Doctor error: {e}")
            
        finally:
            self.call_from_thread(setattr, table, "loading", False)

    def _render_doctor(self) -> None:
        table = self.query_one("#doctor_table", DataTable)
        table.clear()
        
        for check_name, detail, is_pass in self.all_results:
            search_str = f"{check_name} {detail}".lower()
            if self.current_search:
                if self.current_search not in search_str:
                    continue
                    
            icon = "✅" if is_pass else "❌"
            table.add_row(icon, check_name, detail)
