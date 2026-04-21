<p align="center">
  <strong>☁️ Kloud Kompass OS</strong><br>
  <em>The Multi-Kernel Management OS for the Terminal</em>
</p>

<p align="center">
  <a href="https://github.com/MrCh0p808/KloudKompass/actions/workflows/test.yml"><img src="https://github.com/MrCh0p808/KloudKompass/actions/workflows/test.yml/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9%2B-blue.svg" alt="Python 3.9+"></a>
  <a href="https://github.com/MrCh0p808/KloudKompass"><img src="https://img.shields.io/badge/platform-Linux%20%7C%20WSL-lightgrey.svg" alt="Platform"></a>
</p>

---

**Kloud Kompass OS** is a terminal-first, **multi-kernel management OS** for DevOps engineers, SREs, and secops practitioners. Unlike traditional CLIs, it orchestrates up to 10 isolated, provider-aware cloud account kernels with dynamic sidebar re-composition, global staggered task scheduling, and decision-based notification hubs.

```
╦╔═ ╦  ╔═╗╦ ╦╔╦╗  ╦╔═╔═╗╔╦╗╔═╗╔═╗╔═╗╔═╗
╠╩╗ ║  ║ ║║ ║ ║║  ╠╩╗║ ║║║║╠═╝╠═╣╚═╗╚═╗
╩ ╩ ╩═╝╚═╝╚═╝═╩╝  ╩ ╩╚═╝╩ ╩╩  ╩ ╩╚═╝╚═╝
     Your Cloud Console On Terminal
```

## Why Kloud Kompass?

- 🖥️ **Terminal-native OS** — Tab-based workspace managing up to 10 cloud account kernels simultaneously.
- 🔍 **Adaptive UI Engine** — Sidebar and dashboard re-compose dynamically based on active cloud provider manifests.
- ⚡ **Smart Staggered Updates** — Global `SmartScheduler` prevents CLI "subprocess storms" through prioritized background tasking.
- 📱 **QR Bridge Auth** — High-performance QR terminal bridge for seamless WSL-to-Host cloud SSO authentication.
- 🛡️ **Decision-Based Sentry** — Notification hub for background tab errors with immediate switch-attention modals.
- 📦 **Specialized Lifecycle** — Provider-specific resource actions (e.g., Azure Deallocate, AWS Stop) natively integrated.
- ⚡ **Fast startup** — Lazy-loaded provider modules mean zero cost for unused features.
- 🔌 **Plugin-ready** — Register custom providers with `register_provider()`.

## Quick Install

```bash
# From PyPI (when published)
pip install kloudkompass

# From source
git clone https://github.com/MrCh0p808/KloudKompass.git
cd KloudKompass
python -m venv .venv && source .venv/bin/activate
pip install -e ".[aws,dev]"
```

**Requirements:** Python 3.9+, Linux or WSL. AWS CLI (`aws`) must be installed and configured for AWS features.

## Usage

```bash
# Launch interactive TUI — the main way to use Kloud Kompass
kloudkompass

# Launch the Textual dashboard (sidebar navigation, keyboard shortcuts)
kloudkompass dashboard

# Direct CLI commands (scriptable, pipeable)
kloudkompass cost -p aws -s 2024-01-01 -e 2024-02-01 --breakdown service
kloudkompass compute --state running --output json
kloudkompass network --type sg --region us-east-1
kloudkompass storage --type volume --export volumes.csv
kloudkompass iam --type user
kloudkompass database --type rds
kloudkompass security
kloudkompass doctor
kloudkompass check --provider aws

# Configuration
kloudkompass config --show
kloudkompass config --set-default-provider aws --set-default-region us-east-1
```

## Features

### Live Modules

| Module | What It Does | Provider |
|--------|-------------|----------|
| **Cost** | Billing breakdown by service, usage type, daily, or total | AWS |
| **Compute** | List/start/stop/tag EC2 instances with filters | AWS |
| **Storage** | S3 buckets + EBS volumes with waste highlighting | AWS |
| **IAM** | Users, roles, policies, MFA audit | AWS |
| **Networking** | VPCs, subnets, security group rule exploration | AWS |
| **Database** | RDS + DynamoDB listing and management | AWS |
| **Security** | Vulnerability scanner (public DBs, unencrypted disks, open SGs) | AWS |
| **Doctor** | Health checks for CLI, credentials, and connectivity | All |
| **Reports** | One-press export to CSV, JSON, or Markdown | All |
| **Settings** | Provider, region, profile, cache TTL, custom keybindings | All |

### Textual Dashboard

Full terminal application with:
- **8 sidebar views** — Cost, Compute, Network, Storage, IAM, Database, Security, Doctor
- **Keyboard shortcuts** — Press `1`-`8` for views, `E` for export, `R` for refresh, `?` for help
- **Modal dialogs** — Settings, export, help, and quit confirmation
- **Custom keybindings** — Override defaults via `~/.kloudkompass/keymap.json`
- **Attribution footer** — `© 2026 TTox.Tech | Licensed under MIT`

### Interactive TUI

Menu-driven experience with:
- Provider selection and region configuration
- Guided wizards for cost queries, compute management, and network exploration
- Global navigation: `[B] Back`, `[Q] Quit` on every screen
- Session persistence across screen transitions

## Architecture

```
kloudkompass/
├── cli.py                  # Click entrypoint with 10 subcommands
├── config_manager.py       # TOML config (~/.kloudkompass/config.toml)
├── core/                   # Abstract bases (15 files)
│   ├── cost_base.py        #   CostProvider + CostRecord
│   ├── compute_base.py     #   ComputeProvider + ComputeInstance
│   ├── networking_base.py  #   NetworkProvider + VPCRecord
│   ├── storage_base.py     #   StorageProvider + BucketRecord
│   ├── iam_base.py         #   IAMProvider + IAMUser
│   ├── database_base.py    #   DatabaseProvider + DBInstance
│   ├── security_base.py    #   SecurityProvider + SecurityFinding
│   ├── provider_factory.py #   Lazy-load factory + plugin registry
│   ├── exceptions.py       #   10 custom exception classes
│   ├── health.py           #   CLI + credential health checks
│   ├── keymap.py           #   Customizable hotkey mappings
│   └── updater.py          #   PyPI version checker
├── aws/                    # AWS implementations (9 files)
├── azure/                  # Azure stubs (planned)
├── gcp/                    # GCP stubs (planned)
├── dashboard/              # Textual app
│   ├── app.py              #   Main application (8 views, 15 widgets)
│   ├── views/              #   8 content views
│   └── widgets/            #   15 reusable widgets
├── tui/                    # Interactive menus (20 files)
├── infra/                  # CLI adapters + caching
│   ├── cli_adapter.py      #   Generic subprocess wrapper
│   ├── base_adapter.py     #   Abstract cloud adapter
│   ├── aws_cli_adapter.py  #   AWS-specific adapter with CE pagination
│   └── cache.py            #   TTL + LRU cache with @cache_result
├── cache/                  # File-based cache
└── utils/                  # Shared utilities (formatters, pagination, exports)
```

## Configuration

Kloud Kompass stores configuration in `~/.kloudkompass/config.toml`:

```toml
default_provider = "aws"
default_region = "us-east-1"
default_output = "table"
cache_ttl = 300
```

Custom keybindings in `~/.kloudkompass/keymap.json`:

```json
{
  "quit": "q",
  "export": "e",
  "refresh": "r",
  "show_help": "?",
  "show_cost": "1",
  "show_compute": "2"
}
```

## Development

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=kloudkompass

# Format code
black .

# Type check
mypy kloudkompass/

# Build distribution
python -m build
```

## Roadmap

| Phase | Name | Status |
|-------|------|--------|
| 1-6 | Foundation → Networking & IAM | ✅ Done |
| 7 | **Multi-Kernel OS Core** | ✅ Stabilized |
| 8 | **Azure Specialization** | ✅ Done |
| 9 | GCP High-Kernel Integration | 🔜 In Progress |
| 10 | Global Decision Reports | 🔜 Planned |
| 11 | Testing & CI/CD | ✅ Done |
| 12 | Performance & Polish | ✅ Stabilized |
| 13 | Packaging & Distribution | ✅ Done |

**Upcoming features:**
- Azure Resource Graph and GCP SDK integration
- Cost forecasting and trend analysis
- Tagging hygiene checker
- Resource cleanup assistant
- Auto-remediation scripts in doctor

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE) — © 2026 TTox.Tech

---

*Built with ❤️ by [TTox.Tech](https://github.com/MrCh0p808) for the terminal-first community.*
