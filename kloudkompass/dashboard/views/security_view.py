# kloudkompass/dashboard/views/security_view.py
# ---------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Security audit dashboard view.

from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Static, DataTable, Button, Input
from textual.binding import Binding
from kloudkompass.dashboard.widgets.security_score import SecurityScoreGauge
import re


class SecurityView(Container):
    """
    Security audit dashboard view.

    Runs a security scan across all configured services and groups
    findings by severity: Critical / High / Medium / Low.
    """

    DEFAULT_CSS = """
    SecurityView {
        height: 100%;
        width: 100%;
    }

    SecurityView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    SecurityView .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }

    SecurityView .status-line {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Filters"),
        Binding("i", "ignore_finding", "Ignore Finding"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_findings = []
        self.current_search = ""

    def compose(self) -> ComposeResult:
        yield Static("🛡️ Security Audit", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search Findings... ( / to focus, Esc to clear )", id="sec_search_input")
        yield SecurityScoreGauge(id="security_gauge")
        yield Button("Run Security Scan", id="btn_scan", variant="warning")
        yield DataTable(id="security_table", cursor_type="row")
        yield Static("Press 'Run Security Scan' to begin.", classes="status-line", id="security_status")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "sec_search_input":
            self.current_search = event.value.strip().lower()
            self._render_findings()

    def action_focus_search(self) -> None:
        self.query_one("#sec_search_input").focus()

    def action_clear_search(self) -> None:
        self.query_one("#sec_search_input", Input).value = ""
        self.current_search = ""
        self._render_findings()

    def action_ignore_finding(self) -> None:
        table = self.query_one("#security_table", DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
            if not row_key or "✅" in row_key:
                return

            from kloudkompass.config_manager import get_config_value, set_config_value
            ignored = get_config_value("ignored_security_findings", [])
            if row_key not in ignored:
                ignored.append(row_key)
                set_config_value("ignored_security_findings", ignored)
                
            self.notify(f"Ignored security finding.", severity="information")
            self._run_scan()
        except Exception:
            self.notify("Please select a finding to ignore.", severity="warning")

    def on_mount(self) -> None:
        table = self.query_one("#security_table", DataTable)
        table.add_columns("Severity", "Category", "Finding", "Resource", "Recommendation")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_scan":
            self._run_scan()

    def _run_scan(self) -> None:
        status = self.query_one("#security_status", Static)
        status.update("Scanning...")
        table = self.query_one("#security_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_security(), name="security_scan", exclusive=True)

    async def _fetch_security(self) -> None:
        status = self.query_one("#security_status", Static)
        table = self.query_one("#security_table", DataTable)

        try:
            from kloudkompass.config_manager import load_config, get_config_value
            from kloudkompass.aws.security import AWSSecurityProvider, Severity
            import asyncio
            config = load_config()
            region = config.get("default_region", "us-east-1")
            profile = config.get("default_profile")
            
            provider = AWSSecurityProvider()
            
            # Load saved search on mount
            if not self.current_search:
                saved = get_config_value("security_saved_search", "")
                if saved:
                    self.current_search = saved
                    self.query_one("#sec_search_input", Input).value = saved

            raw_findings = await asyncio.to_thread(
                provider.run_all_checks, 
                region=region, 
                profile=profile
            )
            
            # Convert objects to internal format and filter ignores
            ignored = get_config_value("ignored_security_findings", [])
            self.all_findings = []
            
            for f in raw_findings:
                fid = f"{f.finding_type}_{f.resource_id}"
                if fid in ignored:
                    continue
                
                sev_map = {
                    Severity.CRITICAL: "🔴 Critical",
                    Severity.HIGH: "🟠 High",
                    Severity.MEDIUM: "🟡 Medium",
                    Severity.LOW: "🔵 Low",
                    Severity.INFO: "ℹ️ Info"
                }
                
                self.all_findings.append({
                    "id": fid,
                    "severity": sev_map.get(f.severity, "ℹ️ Info"),
                    "category": f.finding_type.split("-")[0].capitalize(),
                    "finding": f.description,
                    "resource": f.resource_id,
                    "rec": f.recommendation
                })

            self.call_from_thread(self._render_findings)
        except Exception as e:
            self.call_from_thread(status.update, f"Scan error: {e}")
        finally:
            self.call_from_thread(setattr, table, "loading", False)
            
    def _render_findings(self) -> None:
        table = self.query_one("#security_table", DataTable)
        status = self.query_one("#security_status", Static)
        
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("security_saved_search", self.current_search)
        except Exception: pass

        table.clear()
        filtered = []
        for f in self.all_findings:
            search_str = f"{f['finding']} {f['resource']} {f['category']}".lower()
            if self.current_search:
                try:
                    if not re.search(self.current_search, search_str): continue
                except re.error:
                    if self.current_search not in search_str: continue
            filtered.append(f)
            table.add_row(f['severity'], f['category'], f['finding'], f['resource'][:30], f['rec'], key=f['id'])

        if not filtered and not self.current_search:
             table.add_row("✅ None", "—", "No security issues found", "—", "—", key="none")

        # Calculate and set security score
        score = 100
        for f in filtered:
            sev = f['severity']
            if "Critical" in sev: score -= 15
            elif "High" in sev: score -= 8
            elif "Medium" in sev: score -= 3
            elif "Low" in sev: score -= 1
        
        score = max(0, score)
        gauge = self.query_one("#security_gauge", SecurityScoreGauge)
        gauge.set_score(score, len(filtered))
        status.update(f"Scan complete — {len(filtered)} finding(s)")
