# Kloud Kompass System Map

High-level architectural directory routing.

## Core Directories

### `kloudkompass/` (Main Package)
- `cli.py`: Click entrypoint with `cost`, `compute`, `network`, `storage`, `iam`, `database`, `security`, `doctor`, `config`, `check`, `dashboard` subcommands.
- `config_manager.py`: TOML config loading/saving (`~/.kloudkompass/config.toml`).
- `__init__.py`: Version, copyright constants.

### `kloudkompass/core/` (Business Logic Layer - 12 files)
- `cost_base.py`: Abstract `CostProvider` + `CostRecord` dataclass.
- `compute_base.py`: Abstract `ComputeProvider` + `ComputeInstance` dataclass.
- `networking_base.py`: Abstract `NetworkProvider` + `VPCRecord` dataclass.
- `storage_base.py`: Abstract `StorageProvider` + `BucketRecord` dataclass.
- `iam_base.py`: Abstract `IAMProvider` + `IAMUser` dataclass.
- `database_base.py`: Abstract `DatabaseProvider` + `DBInstance` dataclass.
- `security_base.py`: Abstract `SecurityProvider` + `SecurityFinding` + `Severity` enum.
- `provider_factory.py`: Factory with lazy imports + plugin registry.
- `exceptions.py`: Error hierarchy (KloudKompassError -> CLIUnavailable, Credential, Permission, Parsing, etc).
- `health.py`: CLI installation checks, credential validation.
- `provider_base.py`: Base provider interface.

### `kloudkompass/aws/` (AWS Provider Layer - 9 files)
- `cost.py`: `AWSCostProvider` - full implementation with pagination, parsing, grouping.
- `compute.py`: `AWSComputeProvider` - EC2 describe-instances, start/stop/reboot.
- `networking.py`: `AWSNetworkProvider` - VPCs, subnets, security groups, EIPs, NACLs.
- `storage.py`: `AWSStorageProvider` - S3 buckets, EBS volumes, snapshots.
- `iam.py`: `AWSIAMProvider` - users, roles, policies, MFA status.
- `database.py`: `AWSDatabaseProvider` - RDS, DynamoDB, ElastiCache.
- `security.py`: `AWSSecurityProvider` - vulnerability scanning, severity findings.
- `inventory.py`: `AWSInventoryProvider` + `InventoryRecord`.

### `kloudkompass/azure/` & `kloudkompass/gcp/` (Future Providers)
- Stub modules for multi-cloud expansion.

### `kloudkompass/dashboard/` (Textual Dashboard - 20 files)
- `app.py`: `KloudKompassApp` Textual application with sidebar, keybindings, modals, ASCII banner.
- `views/`: 8 content views (cost, compute, network, storage, IAM, database, security, doctor).
- `widgets/`: 8 reusable widgets (attribution_footer, cost_table, export_modal, filter_panel, help_modal, quit_modal, settings_modal, status_bar).

### `kloudkompass/tui/` (Terminal UI Layer - 20 files)
- `screens.py`: `Screen` ABC with mount/render/unmount lifecycle, `InputResult`, `get_input()`, `BRAND_TITLE`, `BRAND_SHORT`, `BRAND_BANNER`.
- `main_menu.py`: Root menu screen (10 categories).
- `navigation.py`: Stack-based `Navigator` controller.
- `session.py`: Frozen `SessionState` dataclass with `with_*()` immutable updates.
- `prompts.py`: Centralized user prompts (provider, dates, breakdown, threshold).
- `cost_menu.py`: Cost query wizard flow.
- `compute_menu.py`: Compute drill-down menu (list, filter, details).
- `network_menu.py`: Network exploration menu (VPCs, SGs, subnets).
- `storage_menu.py`: Storage management menu (S3, EBS, snapshots).
- `iam_menu.py`: IAM audit menu (users, roles, policies).
- `database_menu.py`: Database management menu (RDS, DynamoDB).
- `settings_menu.py`: Settings configuration menu.
- `inventory_menu.py`: Inventory wizard.
- `security_menu.py`: Security wizard.
- `provider_setup.py`: Pure-logic provider readiness check.
- `provider_setup_screen.py`: UI screen for provider configuration guidance.
- `doctor.py`: Health check report renderer.
- `footer.py`: Attribution footer renderer.
- `menu_result.py`: Menu result dataclass.

### `kloudkompass/utils/` (Shared Utilities)
- `subprocess_helpers.py`: `run_cli_command()`, `run_cli_json()`, command builders.
- `parsers.py`: Date validation, cost amount parsing, `safe_get_nested()`.
- `formatters.py`: `format_records()`, `OutputFormat` enum.
- `exports.py`: CSV/JSON file export.
- `pagination.py`: AWS pagination handler with infinite-loop guard.
- `logger.py`: Debug logging utilities.

### `kloudkompass/infra/` (Infrastructure Layer)
- `cache.py`: `ResultCache` with TTL + LRU eviction, `@cache_result()` decorator.
- `cli_adapter.py`: Generic CLI execution adapter.

### `tests/` (Test Suite)
- 46 test files, 724 tests covering cache, CLI, config, navigation, session, parsers, dashboard views, modals, provider factories, branding consistency, and more.

### `.coderwa/` (The AI Brain)
- `CoderWa.md`: Unified operating protocol.
- `BashCloud_data/`: Project-specific context (legacy name, maps to Kloud Kompass).
- `agents/`: 20 role-specific AI personas.
- `skills/`: 37 capability-specific task instructions.