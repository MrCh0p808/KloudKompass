# BashCloud

A terminal-first, multi-cloud CLI tool for cloud practitioners who prefer terminal workflows over GUIs. BashCloud delivers interactive, human-friendly access to AWS, Azure, and GCP services — starting with a cost-tracking module and expanding to inventory, security, config audit, reporting, and alerting.

---

## Features

| Feature | Status |
|---------|--------|
| **AWS Cost Explorer** | ✅ Implemented |
| **Interactive TUI** | ✅ Implemented |
| **Textual Dashboard** | ✅ Implemented |
| **CSV/JSON Export** | ✅ Implemented |
| **File-Based Caching** | ✅ Implemented |
| **Doctor Command** | ✅ Implemented |
| Azure/GCP Cost | 🚧 Planned |
| Inventory Modules | 🚧 Planned |
| Security Checks | 🚧 Planned |

---

## Quick Start

```bash
# Install
pip install -e .

# Interactive TUI (default)
bashcloud

# CLI cost query
bashcloud cost --provider aws --start 2024-01-01 --end 2024-02-01 --breakdown service

# Dashboard mode
bashcloud dashboard

# Health check
bashcloud doctor
```

---

## Requirements

- Python 3.10+
- AWS CLI v2 (for AWS features)
- Azure CLI (for Azure features, planned)
- Google Cloud SDK (for GCP features, planned)

---

## Architecture

```
bashcloud/
├── bashcloud/
│   ├── cli.py              # Click CLI entrypoint
│   ├── config_manager.py   # TOML config handling
│   ├── aws/
│   │   └── cost.py         # AWS Cost Explorer provider
│   ├── core/
│   │   ├── cost_base.py    # CostProvider interface
│   │   ├── models.py       # CostRecord dataclass
│   │   └── exceptions.py   # Custom exceptions
│   ├── infra/
│   │   ├── cli_adapter.py  # Subprocess wrapper
│   │   ├── aws_cli_adapter.py  # AWS-specific adapter
│   │   └── cache.py        # In-memory TTL cache
│   ├── cache/
│   │   └── file_cache.py   # File-based TTL cache
│   ├── tui/
│   │   ├── screens/        # Guided TUI screens
│   │   └── doctor.py       # Environment health checks
│   ├── dashboard/
│   │   ├── app.py          # Textual dashboard app
│   │   ├── views/          # Dashboard views
│   │   └── widgets/        # Dashboard widgets
│   └── utils/
│       ├── formatters.py   # Table/plain/JSON/CSV output
│       ├── pagination.py   # CLI pagination handling
│       ├── exports.py      # CSV/JSON file export
│       └── logger.py       # Debug logging
└── tests/                  # 210+ unit tests
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `bashcloud` | Launch interactive TUI |
| `bashcloud cost` | Query cloud costs |
| `bashcloud doctor` | Check environment health |
| `bashcloud dashboard` | Launch Textual dashboard |
| `bashcloud --help` | Show help |

### Cost Command Options

```bash
bashcloud cost \
  --provider aws \
  --start 2024-01-01 \
  --end 2024-02-01 \
  --breakdown service \  # total, service, usage, daily
  --threshold 1.0 \      # Filter below threshold
  --format table \       # table, plain, json, csv
  --output costs.csv     # Export to file
```

---

## Doctor Command

Checks environment health with actionable remediation:

```
$ bashcloud doctor

  BashCloud Doctor
==================================================

  [OK] AWS CLI: Installed
  [OK] AWS CLI Version: v2.15.0
  [OK] AWS Credentials: Valid
  [OK] Cost Explorer Access: Accessible
  [!!] Azure CLI: Not found in PATH
  [!!] Google Cloud SDK: Not found in PATH
  [OK] BashCloud Config: Found at ~/.bashcloud/config.toml

--------------------------------------------------
  Some checks failed. See remediation steps below.

  Azure CLI:
    Install Azure CLI: https://docs.microsoft.com/cli/azure/install-azure-cli
```

---

## Configuration

Create `~/.bashcloud/config.toml`:

```toml
[defaults]
provider = "aws"
output_format = "table"
threshold = 0.0

[aws]
profile = "default"
region = "us-east-1"

[cache]
ttl = 300  # 5 minutes
```

---

## Development

```bash
# Clone and install
git clone <repo>
cd bashcloud
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with debug logging
bashcloud --debug cost ...
```

### Test Coverage

- **210 tests** covering:
  - CLI commands and options
  - AWS cost provider
  - Pagination handling
  - Formatters and exporters
  - TUI navigation and session
  - File cache TTL and invalidation
  - Doctor version and permission checks

---

## Roadmap

### Phase 1 (Complete)
- [x] AWS Cost Explorer integration
- [x] Interactive TUI with guided menus
- [x] Textual dashboard
- [x] CSV/JSON export
- [x] File-based caching
- [x] Doctor command with remediation

### Phase 2 (Planned)
- [ ] Azure Cost Management
- [ ] GCP Billing Export
- [ ] Cross-cloud cost comparison

### Phase 3 (Future)
- [ ] Compute inventory
- [ ] Storage inventory
- [ ] Security checks
- [ ] Alerting (email/Slack)
- [ ] Cost forecasting

---

## License

MIT
