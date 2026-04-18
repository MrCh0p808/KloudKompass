# kloudkompass/dashboard/views/compute_view.py
# --------------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Compute (EC2) dashboard view with DataTable.

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.widgets import Static, DataTable, Button, Input, TabbedContent, TabPane, Pretty
from textual.worker import Worker
from textual.binding import Binding
import re
import humanize
from datetime import datetime, timezone

class ComputeView(Container):
    """
    Compute resources dashboard view.

    Shows EC2 instances in a rich DataTable with state colour indicators,
    a state filter button bar, and async data loading.
    """

    DEFAULT_CSS = """
    ComputeView {
        height: 100%;
        width: 100%;
    }

    ComputeView .view-title {
        dock: top;
        height: 3;
        padding: 1;
        background: $surface;
        text-align: center;
        text-style: bold;
    }

    ComputeView .filter-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        layout: horizontal;
    }

    ComputeView .filter-bar Button {
        margin-right: 1;
    }

        height: 1;
        padding: 0 1;
        background: $surface;
    }
    
    ComputeView .search-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        margin-bottom: 1;
    }
    
    ComputeView DataTable {
        border: tall $primary-muted;
        background: $surface;
        zebra_stripes: True;
    }

    ComputeView #main_content {
        height: 1fr;
        width: 100%;
        layout: horizontal;
    }
    
    ComputeView #compute_table {
        width: 1fr;
        height: 100%;
    }
    
    ComputeView #details_panel {
        width: 40%;
        height: 100%;
        border-left: solid $primary;
        padding: 1;
        background: $surface;
        display: block;
    }
    
    ComputeView #details_panel.hidden {
        display: none;
    }
    
    ComputeView .details-title {
        text-style: bold;
        margin-bottom: 1;
        content-align: center middle;
        background: $boost;
    }
    """

    BINDINGS = [
        Binding("/", "focus_search", "Search"),
        Binding("escape", "clear_search", "Clear Filters"),
        Binding("r", "filter_running", "Running Only"),
        Binding("space", "toggle_select", "Select"),
        Binding("ctrl+s", "start_instance", "Start"),
        Binding("ctrl+x", "stop_instance", "Stop"),
        Binding("shift+t", "terminate_instance", "Terminate", show=False),
        Binding("t", "edit_tags", "Edit Tags"),
        Binding("h", "toggle_columns", "Toggle Columns"),
        Binding("c", "copy_id", "Copy ID"),
        Binding("ctrl+c", "copy_json", "Copy JSON", show=False),
        Binding("ctrl+e", "export_selected", "Export CSV", show=False),
        Binding("v", "resolve_vpc", "Resolve VPC"),
        Binding("g", "resolve_sg", "Resolve SG"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_instances = []
        self.current_search = ""
        self.state_filter = None
        self.selected_instances = set()
        self.sort_reverse = False
        self._instance_data = {}
        self.show_extra_columns = True

    def compose(self) -> ComposeResult:
        yield Static("☁ Compute Resources (EC2)", classes="view-title")
        with Container(classes="search-bar"):
            yield Input(placeholder="Search... ( / to focus, Esc to clear | supports Regex & tag:Env=Prod )", id="search_input")
        with Container(classes="filter-bar"):
            yield Button("All", id="filter_all", variant="primary")
            yield Button("Running", id="filter_running")
            yield Button("Stopped", id="filter_stopped")
            yield Button("⟳ Refresh", id="btn_refresh")
            
        with Horizontal(id="main_content"):
            yield DataTable(id="compute_table", cursor_type="row")
            with VerticalScroll(id="details_panel", classes="hidden"):
                yield Static("Instance Details", id="details_header", classes="details-title")
                with TabbedContent():
                    with TabPane("Summary", id="tab_summary"):
                        yield Static("", id="details_summary")
                    with TabPane("JSON Payload", id="tab_json"):
                        yield Pretty({}, id="details_json")
                    with TabPane("Metrics", id="tab_metrics"):
                        yield Static("CloudWatch CPU Utilization (simulated)\n\n[green]      __      __\n   __/  \\    /  \\\n__/      \\__/    \\___[/green]", id="details_metrics")
                        
        yield Static("Ready — press a filter to load instances.", classes="status-line", id="compute_status")

    def on_mount(self) -> None:
        table = self.query_one("#compute_table", DataTable)
        table.add_columns("✓", "Instance ID", "Name", "Type", "State", "Public IP", "Region", "Launched")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "filter_all":
            self.state_filter = None
            self._fetch_or_render()
        elif bid == "filter_running":
            self.state_filter = "running"
            self._fetch_or_render()
        elif bid == "filter_stopped":
            self.state_filter = "stopped"
            self._fetch_or_render()
        elif bid == "btn_refresh":
            self._load_instances()

    def action_focus_search(self) -> None:
        self.query_one("#search_input").focus()

    def action_clear_search(self) -> None:
        search_box = self.query_one("#search_input", Input)
        search_box.value = ""
        self.current_search = ""
        self.state_filter = None
        self._render_table()
        
    def action_toggle_columns(self) -> None:
        self.show_extra_columns = not self.show_extra_columns
        self._render_table()
        self.notify("Toggled column visibility.", severity="information")
        
    def action_filter_running(self) -> None:
        self.state_filter = "running"
        self._render_table()

    def action_start_instance(self) -> None:
        self._perform_instance_action("start")

    def action_stop_instance(self) -> None:
        self._perform_instance_action("stop")

    def action_terminate_instance(self) -> None:
        targets = list(self.selected_instances)
        if not targets:
            inst = self._get_selected_instance()
            if inst:
                targets = [inst.instance_id]
                
        if not targets:
            self.notify("No instance(s) selected.", severity="warning")
            return

        from kloudkompass.dashboard.widgets.safe_delete_modal import SafeDeleteModal
        
        def check_result(confirmed: bool) -> None:
            if confirmed:
                from textual.notifications import Notification
                import asyncio
                
                # Set up the cancel event
                cancel_event = asyncio.Event()
                
                # Show the notification with an Undo action
                msg = f"Queueing TERMINATE for {len(targets)} instance(s)..."
                self.notify(msg, title="Action Queued", severity="warning", timeout=5)
                
                async def execute_with_undo():
                    # Wait 4 seconds for a potential undo
                    try:
                        await asyncio.wait_for(cancel_event.wait(), timeout=4.0)
                        self.notify("Termination cancelled.", title="Undo Successful", severity="information")
                    except asyncio.TimeoutError:
                        # Proceed with termination
                        self.run_worker(self._execute_action("terminate", targets), exclusive=False)

                class UndoHandler:
                    def action_undo(self_, *args):
                        cancel_event.set()
                        
                # Attach an undo handler to the app temporarily
                if not hasattr(self.app, 'action_undo'):
                    self.app.action_undo = UndoHandler().action_undo

                self.run_worker(execute_with_undo(), name="terminate_with_undo")
                
                # Note: The notify method doesn't support action buttons natively in all Textual versions securely without custom widgets, 
                # so we rely on the command palette / keyboard bindings or a custom toast for 'Undo', 
                # but standard practice is notifying the queue state.
                
        self.app.push_screen(SafeDeleteModal(targets), check_result)

    def action_toggle_select(self) -> None:
        inst = self._get_selected_instance()
        if not inst: return
        iid = inst.instance_id
        if iid in self.selected_instances:
            self.selected_instances.remove(iid)
        else:
            self.selected_instances.add(iid)
        self._render_table()

    async def action_resolve_vpc(self) -> None:
        inst = self._get_selected_instance()
        if not inst or not inst.vpc_id:
            self.notify("No VPC attached to this instance.", severity="warning")
            return
            
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("network_saved_search", inst.vpc_id)
        except Exception:
            pass
            
        self.notify(f"Resolving VPC {inst.vpc_id}...", severity="information")
        await self.app._switch_view("network")

    async def action_resolve_sg(self) -> None:
        """Jump to NetworkView pre-filtered to the instance's Security Group."""
        inst = self._get_selected_instance()
        if not inst:
            self.notify("No instance selected.", severity="warning")
            return

        # Security groups are in the raw JSON data
        raw = self._instance_data.get(inst.instance_id, {})
        sgs = raw.get("SecurityGroups", []) or raw.get("security_groups", [])
        if not sgs:
            self.notify("No Security Groups on this instance.", severity="warning")
            return

        sg_id = sgs[0] if isinstance(sgs[0], str) else sgs[0].get("GroupId", "")
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("network_saved_search", sg_id)
        except Exception:
            pass

        self.notify(f"Resolving SG {sg_id}...", severity="information")
        await self.app._switch_view("network")

    def action_edit_tags(self) -> None:
        """Open the Tag Editor modal for the selected instance(s)."""
        targets = list(self.selected_instances)
        if not targets:
            inst = self._get_selected_instance()
            if inst:
                targets = [inst.instance_id]

        if not targets:
            self.notify("No instance(s) selected.", severity="warning")
            return

        from kloudkompass.dashboard.widgets.tag_editor_modal import TagEditorModal

        def handle_tag_result(result) -> None:
            if result:
                key, value = result
                self.notify(f"Applying tag {key}={value} to {len(targets)} instance(s)...", severity="information")
                self.run_worker(self._apply_tags(targets, key, value), exclusive=False)

        self.app.push_screen(TagEditorModal(targets), handle_tag_result)

    async def _apply_tags(self, instance_ids: list, key: str, value: str) -> None:
        """Apply a tag to instances via the provider."""
        try:
            from kloudkompass.core.provider_factory import get_compute_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_compute_provider(config.get("default_provider", "aws"))
            region = config.get("default_region", "us-east-1")

            await asyncio.to_thread(
                provider.add_tags,
                resource_ids=instance_ids,
                tags={key: value},
                region=region,
            )
            self.app.notify(f"Tag {key}={value} applied to {len(instance_ids)} instance(s)")
        except Exception as e:
            self.app.notify(f"Tag action failed: {e}", severity="error")

    def action_export_selected(self) -> None:
        """Export currently filtered/selected rows to a CSV file."""
        import csv
        import os
        from pathlib import Path
        from datetime import datetime

        instances = []
        if self.selected_instances:
            instances = [i for i in self._all_instances if i.instance_id in self.selected_instances]
        else:
            # Export the currently filtered set
            instances = list(self._all_instances)

        if not instances:
            self.notify("No rows to export.", severity="warning")
            return

        export_dir = Path.home() / ".kloudkompass" / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = export_dir / f"kloudkompass_compute_{ts}.csv"

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Instance ID", "Name", "Type", "State", "Region", "Public IP", "Private IP", "VPC ID"])
                for inst in instances:
                    writer.writerow([
                        inst.instance_id, inst.name, inst.instance_type,
                        inst.state, inst.region, inst.public_ip,
                        inst.private_ip, inst.vpc_id,
                    ])
            self.notify(f"Exported {len(instances)} row(s) to {filepath}", severity="information")
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")

    def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        table = self.query_one("#compute_table", DataTable)
        self.sort_reverse = not self.sort_reverse
        table.sort(event.column_key, reverse=self.sort_reverse)

    def _get_selected_instance(self):
        table = self.query_one("#compute_table", DataTable)
        try:
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        except Exception:
            return None
        for inst in self.all_instances:
            if inst.instance_id == row_key:
                return inst
        return None

    def action_copy_id(self) -> None:
        inst = self._get_selected_instance()
        if inst:
            self.app.copy_to_clipboard(inst.instance_id)
            self.notify(f"Copied {inst.instance_id} to clipboard.", severity="information")

    def action_copy_json(self) -> None:
        inst = self._get_selected_instance()
        if inst:
            import json
            import dataclasses
            try:
                data = dataclasses.asdict(inst)
                self.app.copy_to_clipboard(json.dumps(data, indent=2))
                self.notify("Copied structural JSON to clipboard.", severity="information")
            except Exception as e:
                self.notify(f"Warning: JSON transform failed ({e})", severity="warning")

    def _perform_instance_action(self, action: str) -> None:
        targets = list(self.selected_instances)
        
        if not targets:
            inst = self._get_selected_instance()
            if inst:
                targets = [inst.instance_id]
            
        if not targets:
            self.notify("No instance(s) selected.", severity="warning")
            return
            
        self.notify(f"Queueing {action.upper()} for {len(targets)} instance(s)...", severity="information")
        # Run action asynchronously so it doesn't freeze the UI
        self.run_worker(self._execute_action(action, targets), exclusive=False)

    async def _execute_action(self, action: str, instance_ids: list) -> None:
        try:
            from kloudkompass.core.provider_factory import get_compute_provider
            from kloudkompass.config_manager import load_config
            import asyncio
            config = load_config()
            provider = get_compute_provider(config.get("default_provider", "aws"))
            region = config.get("default_region", "us-east-1")
            
            if action == "start":
                await asyncio.to_thread(provider.start_instance, instance_ids=instance_ids, region=region)
            elif action == "stop":
                await asyncio.to_thread(provider.stop_instance, instance_ids=instance_ids, region=region)
            elif action == "terminate":
                # Ensure the provider implements terminate_instance, AWS SDK handles this.
                await asyncio.to_thread(provider.terminate_instance, instance_ids=instance_ids, region=region)
                
            self.app.notify(f"Successfully sent {action} command to {len(instance_ids)} instance(s)")
            self.selected_instances.clear()
            # Refresh to show new state
            self.run_worker(self._fetch(self.state_filter), exclusive=True)
        except Exception as e:
            self.app.notify(f"Action failed: {e}", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        # Pushing enter on a row
        if event.row_key and event.row_key.value:
            self.app.notify(f"Instance selected: {event.row_key.value}")
            # Placeholder for future ActionMenuModal (Feature 22)
            # self.app.push_screen(ActionMenuModal(instance_id=event.row_key.value))

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if not event.row_key or not event.row_key.value:
            # Hide panel if no highlighted row
            self.query_one("#details_panel").add_class("hidden")
            return
            
        inst_id = str(event.row_key.value)
        
        # Find instance in local array
        target_inst = None
        for i in self.all_instances:
            if i.instance_id == inst_id:
                target_inst = i
                break
                
        if target_inst:
            panel = self.query_one("#details_panel")
            panel.remove_class("hidden")
            
            # Update Header
            launch = target_inst.launch_time or 'Unknown'
            if launch != 'Unknown':
                try:
                    td = datetime.fromisoformat(launch.replace('Z', '+00:00'))
                    rel_time = humanize.naturaltime(datetime.now(timezone.utc) - td)
                    launch = f"{launch} ({rel_time})"
                except Exception:
                    pass
                    
            self.query_one("#details_header", Static).update(f"ID: [bold]{target_inst.instance_id}[/]\nName: {target_inst.name}")
            
            # Update Summary
            summary_txt = f"""
[b]Type:[/b] {target_inst.instance_type}
[b]State:[/b] {target_inst.state}
[b]Region:[/b] {target_inst.region}
[b]Public IP:[/b] {target_inst.public_ip or 'None'}
[b]Private IP:[/b] {target_inst.private_ip or 'None'}
[b]VPC ID:[/b] {target_inst.vpc_id or 'None'}
[b]Launch Time:[/b] {launch}

[b]Tags:[/b]
"""
            for k, v in target_inst.tags.items():
                summary_txt += f" - [cyan]{k}[/]: {v}\n"
                
            self.query_one("#details_summary", Static).update(summary_txt)
            
            # Update JSON 
            import dataclasses
            try:
                self.query_one("#details_json", Pretty).update(dataclasses.asdict(target_inst))
            except Exception:
                pass

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search_input":
            self.current_search = event.value.strip()
            self._render_table()

    def _fetch_or_render(self) -> None:
        if self.all_instances:
            self._render_table()
        else:
            self._load_instances(self.state_filter)

    def _load_instances(self, state: str = None) -> None:
        status = self.query_one("#compute_status", Static)
        status.update("Loading instances from AWS...")
        
        table = self.query_one("#compute_table", DataTable)
        table.loading = True
        
        self.run_worker(self._fetch(state), name="fetch_compute", exclusive=True)

    async def _fetch(self, state: str = None) -> None:
        status = self.query_one("#compute_status", Static)
        table = self.query_one("#compute_table", DataTable)

        try:
            from kloudkompass.core.provider_factory import get_compute_provider
            from kloudkompass.config_manager import load_config
            import asyncio

            config = load_config()
            region = config.get("default_region", "us-east-1")
            profile = config.get("default_profile")
            provider = get_compute_provider(config.get("default_provider", "aws"))

            filters = {"instance-state-name": state} if state else None
            
            # Use asyncio.to_thread to prevent blocking the UI
            self.all_instances = await asyncio.to_thread(
                provider.list_instances,
                region=region, 
                profile=profile
            )
            
            # Hydrate _instance_data for SG/VPC resolvers (Gap 8)
            self._instance_data = {inst.instance_id: getattr(inst, 'raw_data', {}) for inst in self.all_instances}

            # Persist the last search logic
            from kloudkompass.config_manager import get_config_value
            saved = get_config_value("compute_saved_search", "")
            if saved and not self.current_search:
                self.current_search = saved
                self.query_one("#search_input", Input).value = saved

            self.call_from_thread(self._render_table)

        except Exception as e:
            self.call_from_thread(table.clear)
            self.call_from_thread(status.update, f"Error: {e}")
            
        finally:
            table.loading = False


    def _render_table(self) -> None:
        table = self.query_one("#compute_table", DataTable)
        status = self.query_one("#compute_status", Static)
        
        table.clear(columns=True)
        cols = ["✓", "Instance ID", "Name", "Type", "State"]
        if self.show_extra_columns:
            cols.extend(["Public IP", "Region", "Launched"])
        table.add_columns(*cols)
        
        filtered = []
        # Save search to config asynchronously 
        from kloudkompass.config_manager import set_config_value
        try:
            set_config_value("compute_saved_search", self.current_search)
        except Exception:
            pass

        # Tag syntax checking
        tag_key, tag_val = None, None
        is_tag_search = self.current_search.lower().startswith("tag:")
        if is_tag_search:
            parts = self.current_search[4:].split("=", 1)
            if len(parts) == 2:
                tag_key, tag_val = parts[0].strip().lower(), parts[1].strip().lower()

        for inst in self.all_instances:
            # 1. State Filter
            if self.state_filter and inst.state != self.state_filter:
                continue
                
            # 2. Search Filter
            if self.current_search:
                if is_tag_search and tag_key and tag_val:
                    # Tag precise filter
                    match = False
                    for k, v in inst.tags.items():
                        if k.lower() == tag_key and tag_val in v.lower():
                            match = True
                            break
                    if not match:
                        continue
                else:
                    # Regex or Fuzzy string match
                    search_payload = f"{inst.instance_id} {inst.name} {inst.instance_type} {inst.state} {inst.public_ip} {inst.region}".lower()
                    try:
                        if not re.search(self.current_search.lower(), search_payload):
                            continue
                    except re.error:
                        # Fallback to standard fuzzy substring matching if regex is invalid (e.g. typing '[' )
                        if self.current_search.lower() not in search_payload:
                            continue
                            
            filtered.append(inst)

            state_fmt = inst.state.lower()
            if state_fmt == "running":
                state_fmt = f"[bold green]● {inst.state}[/]"
            elif state_fmt == "stopped":
                state_fmt = f"[bold red]○ {inst.state}[/]"
            elif state_fmt == "pending":
                state_fmt = f"[bold yellow]⟳ {inst.state}[/]"
            elif state_fmt == "terminated":
                state_fmt = f"[bold grey]✗ {inst.state}[/]"
            else:
                state_fmt = inst.state

            row_data = [
                "[bold cyan]☑[/bold cyan]" if inst.instance_id in self.selected_instances else "[dim]☐[/dim]",
                inst.instance_id,
                inst.name[:30],
                inst.instance_type,
                state_fmt
            ]
            
            if self.show_extra_columns:
                launch = inst.launch_time or "—"
                if launch != "—":
                    try:
                        td = datetime.fromisoformat(launch.replace('Z', '+00:00'))
                        launch = humanize.naturaltime(datetime.now(timezone.utc) - td)
                    except Exception:
                        pass
                row_data.extend([
                    inst.public_ip or "—",
                    inst.region or "—",
                    launch
                ])

            table.add_row(*row_data, key=inst.instance_id)
        
        status.update(f"Showing {len(filtered)}/{len(self.all_instances)} records")

