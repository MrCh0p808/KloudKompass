# Kloud Kompass Tech Stack

## Core Language & Runtime
- **Python 3.8+**: Target compatibility. Tested on 3.8–3.12.
- **pip / setuptools**: Package management via `pyproject.toml`.

## CLI Framework
- **Click 8.1+**: Command groups, options, help text, shell auto-completion.
- **Rich 10.9+**: Tables, panels, color output, spinners, progress bars.
- **Textual 0.50+**: Full TUI dashboard app (Textual framework by Textualize).

## Cloud Provider CLIs (External Dependencies)
- **AWS CLI v2**: `aws ce`, `aws ec2`, `aws s3api`, `aws iam`, `aws rds`.
- **Azure CLI**: `az consumption`, `az vm`, `az network` (Phase 7).
- **Google Cloud SDK**: `gcloud compute`, `gcloud billing` (Phase 8).

## Configuration
- **python-dotenv 1.0+**: Environment variable loading.
- **toml 0.10+**: Config file parsing (`~/.kloudkompass/config.toml`).

## Architecture Patterns
- **Factory Pattern**: `core/provider_factory.py` - lazy-loaded providers.
- **Immutable State**: `tui/session.py` - frozen dataclass with `with_*()` methods.
- **Screen Lifecycle**: `tui/screens.py` - mount/render/unmount + Navigator stack.
- **TTL+LRU Cache**: `infra/cache.py` - in-memory with SHA-256 keys.
- **Subprocess Wrapper**: `utils/subprocess_helpers.py` - timeout, JSON parsing, error wrapping.

## Testing & Quality
- **pytest 7.0+**: Test runner with fixtures.
- **pytest-cov 4.0+**: Coverage reporting.
- **black 23.0+**: Code formatter.
- **mypy 1.0+**: Static type checker.