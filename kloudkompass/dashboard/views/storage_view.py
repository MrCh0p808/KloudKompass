# kloudkompass/dashboard/views/storage_view.py
# --------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Storage (S3/EBS) dashboard view with tabbed interface.

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, DataTable, TabbedContent, TabPane, Button, Input
from textual.binding import Binding
import re

class StorageView(Container):
    """
    Storage resources dashboard view.

    Tabbed interface: S3 Buckets / EBS Volumes.
    Unattached volumes highlighted for waste detection.
    """

    DEFAULT_CSS = """
    StorageView {
        height: 100%;
        width: 100%;
    }

    StorageView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    StorageView .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }

    StorageView .status-line {
        dock: bottom;
        height: 1;
        padding: 0 1;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Filters"),
        Binding("o", "open_in_browser", "Open in Browser"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_buckets = []
        self.all_volumes = []
        self.current_search = ""

    def compose(self) -> ComposeResult:
        yield Static("📦 Storage Resources (S3/EBS)", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search... ( / to focus, Esc to clear )", id="storage_search_input")
        with TabbedContent():
            with TabPane("S3 Buckets", id="tab_buckets"):
                yield DataTable(id="bucket_table", cursor_type="row")
            with TabPane("EBS Volumes", id="tab_volumes"):
                yield DataTable(id="volume_table", cursor_type="row")
        yield Static("Select a tab to load data.", classes="status-line", id="storage_status")

    def on_mount(self) -> None:
        bt = self.query_one("#bucket_table", DataTable)
        bt.add_columns("Bucket Name", "Created")

        vt = self.query_one("#volume_table", DataTable)
        vt.add_columns("Volume ID", "Name", "Size (GB)", "Type", "State", "Attached To", "Enc")

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "storage_search_input":
            self.current_search = event.value.strip().lower()
            self._render_buckets()
            self._render_volumes()

    def action_focus_search(self) -> None:
        self.query_one("#storage_search_input").focus()

    def action_clear_search(self) -> None:
        self.query_one("#storage_search_input", Input).value = ""
        self.current_search = ""
        self._render_buckets()
        self._render_volumes()

    def on_tabbed_content_tab_activated(self, event) -> None:
        tab_id = str(getattr(event, "tab", getattr(event.tab, "id", "")))
        
        # Load saved search
        if not self.current_search:
            from kloudkompass.config_manager import get_config_value
            saved = get_config_value("storage_saved_search", "")
            if saved:
                self.current_search = saved
                self.query_one("#storage_search_input", Input).value = saved

        if "buckets" in tab_id:
            self._load_buckets()
        elif "volumes" in tab_id:
            self._load_volumes()

    def action_open_in_browser(self) -> None:
        try:
            tabbed_content = self.query_one(TabbedContent)
            if tabbed_content.active == "tab_buckets":
                table = self.query_one("#bucket_table", DataTable)
                row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
                if row_key:
                    import webbrowser
                    from kloudkompass.config_manager import load_config
                    config = load_config()
                    region = config.get("default_region", "us-east-1")
                    url = f"https://s3.console.aws.amazon.com/s3/buckets/{row_key}?region={region}&tab=objects"
                    webbrowser.open(url)
                    self.notify(f"Opening S3 Bucket {row_key} in browser...")
        except Exception:
            self.notify("Please highlight a bucket first.", severity="warning")

    def _load_buckets(self) -> None:
        table = self.query_one("#bucket_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_buckets(), name="fetch_buckets", exclusive=True)

    def _load_volumes(self) -> None:
        table = self.query_one("#volume_table", DataTable)
        table.loading = True
        self.run_worker(self._fetch_volumes(), name="fetch_volumes", exclusive=True)

    async def _fetch_buckets(self) -> None:
        status = self.query_one("#storage_status", Static)
        table = self.query_one("#bucket_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_storage_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_storage_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_buckets = await asyncio.to_thread(
                provider.list_buckets,
                profile=config.get("default_profile")
            )
            self.call_from_thread(self._render_buckets)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_buckets(self) -> None:
        table = self.query_one("#bucket_table", DataTable)
        status = self.query_one("#storage_status", Static)
        
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("storage_saved_search", self.current_search)
        except Exception: pass

        table.clear()
        count = 0
        for b in self.all_buckets:
            search_str = f"{b.bucket_name}".lower()
            if self.current_search and self.current_search not in search_str:
                continue
            table.add_row(b.bucket_name, b.creation_date[:19] if b.creation_date else "—", key=b.bucket_name)
            count += 1
        status.update(f"Found {count}/{len(self.all_buckets)} bucket(s)")

    async def _fetch_volumes(self) -> None:
        status = self.query_one("#storage_status", Static)
        table = self.query_one("#volume_table", DataTable)
        try:
            from kloudkompass.core.provider_factory import get_storage_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_storage_provider(config.get("default_provider", "aws"))

            # Use asyncio.to_thread
            self.all_volumes = await asyncio.to_thread(
                provider.list_volumes,
                region=config.get("default_region", "us-east-1"),
                profile=config.get("default_profile"),
            )
            self.call_from_thread(self._render_volumes)
        except Exception as e:
            status.update(f"Error: {e}")
        finally:
            table.loading = False

    def _render_volumes(self) -> None:
        table = self.query_one("#volume_table", DataTable)
        status = self.query_one("#storage_status", Static)
        table.clear()
        count = 0
        
        tag_key, tag_val = None, None
        is_tag_search = self.current_search.startswith("tag:")
        if is_tag_search:
            parts = self.current_search[4:].split("=", 1)
            if len(parts) == 2:
                tag_key, tag_val = parts[0].strip(), parts[1].strip()

        for v in self.all_volumes:
            search_str = f"{v.volume_id} {v.name} {v.state} {v.attached_to}".lower()
            if self.current_search:
                if is_tag_search and tag_key and tag_val:
                    match = False
                    for tk, tv in v.tags.items():
                        if tk.lower() == tag_key and tag_val in tv.lower():
                            match = True; break
                    if not match: continue
                else:
                    try:
                        if not re.search(self.current_search, search_str): continue
                    except re.error:
                        if self.current_search not in search_str: continue

            enc = "✓" if v.encrypted else "✗"
            table.add_row(v.volume_id, v.name[:20], str(v.size_gb), v.volume_type, v.state, v.attached_to or "—", enc)
            count += 1
        status.update(f"Found {count}/{len(self.all_volumes)} volume(s)")
