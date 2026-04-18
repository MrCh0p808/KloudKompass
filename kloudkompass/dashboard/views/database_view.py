# kloudkompass/dashboard/views/database_view.py
# ---------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Database (RDS/DynamoDB) dashboard view with tabbed interface.

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Static, DataTable, TabbedContent, TabPane, Input
from textual.binding import Binding
import re


class DatabaseView(Container):
    """
    Database resources dashboard view.

    Tabbed interface: RDS Instances / DynamoDB Tables.
    """

    DEFAULT_CSS = """
    DatabaseView {
        height: 100%;
        width: 100%;
    }

    DatabaseView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    DatabaseView .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }

    DatabaseView .status-line {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Filters"),
        Binding("ctrl+s", "start_rds", "Start RDS"),
        Binding("ctrl+x", "stop_rds", "Stop RDS"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_rds = []
        self.all_dynamodb = []
        self.current_search = ""

    def compose(self) -> ComposeResult:
        yield Static("🗄️ Database Resources", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search... ( / to focus, Esc to clear )", id="db_search_input")
        with TabbedContent():
            with TabPane("RDS Instances", id="tab_rds"):
                yield DataTable(id="rds_table", cursor_type="row")
            with TabPane("DynamoDB Tables", id="tab_dynamodb"):
                yield DataTable(id="dynamodb_table", cursor_type="row")
        yield Static("Select a tab to load data.", classes="status-line", id="db_status")

    def on_mount(self) -> None:
        rt = self.query_one("#rds_table", DataTable)
        rt.add_columns("DB ID", "Engine", "Class", "Status", "Multi-AZ", "Enc", "Public")

        dt = self.query_one("#dynamodb_table", DataTable)
        dt.add_columns("Table Name", "Status", "Items", "Billing", "RCU", "WCU")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "db_search_input":
            self.current_search = event.value.strip().lower()
            self._render_rds()
            self._render_dynamodb()

    def action_focus_search(self) -> None:
        self.query_one("#db_search_input").focus()

    def action_clear_search(self) -> None:
        self.query_one("#db_search_input", Input).value = ""
        self.current_search = ""
        self._render_rds()
        self._render_dynamodb()

    def on_tabbed_content_tab_activated(self, event) -> None:
        tab_id = str(getattr(event, "tab", ""))
        # Persist the last search logic from config on first load
        if not self.current_search:
            from kloudkompass.config_manager import get_config_value
            saved = get_config_value("database_saved_search", "")
            if saved:
                self.current_search = saved
                self.query_one("#db_search_input", Input).value = saved

        if "rds" in tab_id:
            self._load_rds()
        elif "dynamodb" in tab_id:
            self._load_dynamodb()

    def action_start_rds(self) -> None:
        self._perform_rds_action("start")

    def action_stop_rds(self) -> None:
        self._perform_rds_action("stop")

    def _perform_rds_action(self, action: str) -> None:
        table = self.query_one("#rds_table", DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        except Exception:
            self.notify("No RDS instance selected.", severity="warning")
            return
            
        if not row_key:
            return
            
        self.notify(f"Queueing {action.upper()} for RDS {row_key}...", severity="information")
        self.run_worker(self._execute_rds_action(action, str(row_key)), exclusive=False)

    async def _execute_rds_action(self, action: str, db_id: str) -> None:
        try:
            from kloudkompass.core.provider_factory import get_database_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_database_provider(config.get("default_provider", "aws"))
            region = config.get("default_region", "us-east-1")
            
            if action == "start":
                await asyncio.to_thread(provider.start_db_instance, db_id=db_id, region=region)
            elif action == "stop":
                await asyncio.to_thread(provider.stop_db_instance, db_id=db_id, region=region)
                
            self.app.notify(f"Successfully sent {action} command to RDS {db_id}")
            self.run_worker(self._fetch_rds(), exclusive=True)
        except Exception as e:
            self.app.notify(f"Action failed: {e}", severity="error")

    def _load_rds(self) -> None:
        table = self.query_one("#rds_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_rds(), name="fetch_rds", exclusive=True)

    def _load_dynamodb(self) -> None:
        table = self.query_one("#dynamodb_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_dynamodb(), name="fetch_dynamodb", exclusive=True)

    async def _fetch_rds(self) -> None:
        status = self.query_one("#db_status", Static)
        table = self.query_one("#rds_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_database_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_database_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_rds = await asyncio.to_thread(
                provider.list_db_instances,
                region=config.get("default_region", "us-east-1"),
                profile=config.get("default_profile"),
            )
            self.call_from_thread(self._render_rds)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_rds(self) -> None:
        table = self.query_one("#rds_table", DataTable)
        status = self.query_one("#db_status", Static)
        
        # Save search to config
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("database_saved_search", self.current_search)
        except Exception:
            pass

        table.clear()
        count = 0
        tag_key, tag_val = None, None
        is_tag_search = self.current_search.startswith("tag:")
        if is_tag_search:
            parts = self.current_search[4:].split("=", 1)
            if len(parts) == 2:
                tag_key, tag_val = parts[0].strip(), parts[1].strip()

        for db in self.all_rds:
            search_str = f"{db.db_id} {db.engine} {db.status} {db.instance_class}".lower()
            
            if self.current_search:
                if is_tag_search and tag_key and tag_val:
                    match = False
                    for k, v in db.tags.items():
                        if k.lower() == tag_key and tag_val in v.lower():
                            match = True; break
                    if not match: continue
                else:
                    try:
                        if not re.search(self.current_search, search_str): continue
                    except re.error:
                        if self.current_search not in search_str: continue

            maz = "✓" if db.multi_az else "✗"
            enc = "✓" if db.encrypted else "✗"
            pub = "✓" if db.publicly_accessible else "✗"
            table.add_row(db.db_id[:28], db.engine, db.instance_class, db.status, maz, enc, pub, key=db.db_id)
            count += 1
        
        status.update(f"Found {count}/{len(self.all_rds)} RDS instance(s)")

    async def _fetch_dynamodb(self) -> None:
        status = self.query_one("#db_status", Static)
        table = self.query_one("#dynamodb_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_database_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_database_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_dynamodb = await asyncio.to_thread(
                provider.list_nosql_tables,
                region=config.get("default_region", "us-east-1"),
                profile=config.get("default_profile"),
            )
            self.call_from_thread(self._render_dynamodb)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_dynamodb(self) -> None:
        table = self.query_one("#dynamodb_table", DataTable)
        status = self.query_one("#db_status", Static)
        table.clear()
        
        count = 0
        for t in self.all_dynamodb:
            search_str = f"{t.table_name} {t.status} {t.billing_mode}".lower()
            if self.current_search and self.current_search not in search_str:
                continue
                
            table.add_row(t.table_name[:35], t.status, str(t.item_count), t.billing_mode, str(t.read_capacity), str(t.write_capacity))
            count += 1
            
        status.update(f"Found {count}/{len(self.all_dynamodb)} DynamoDB table(s)")
