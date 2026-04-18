# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-18

### Added
- **Branding Migration**: Rebranded creator as TTox.Tech and released under MIT License.
- **Packaging Ready**: Added `pyproject.toml`, `MANIFEST.in`, and `.gitignore` updates for Linux packaging (PyPI and DEB).
- **Navigation Model**: Introduced `InputResult` and `get_input()` for global navigation (Q to quit, B to back).
- **Dashboard Features**: Added quit confirmation, export modal (CSV/JSON/MD), and help modal to the Textual dashboard.
- **Provider Gate**: Implemented interactive provider setup flow and configuration gate.
- **Testing**: Added 376 new tests, bringing total coverage to 601 tests across the codebase.

### Changed
- Moved `boto3` to an optional `[aws]` dependency.
- Updated minimum Python requirement to 3.9 (required by Textual 0.50+).
- Standardized attribution string `© 2026 TTox.Tech. Licensed under MIT.` across all files.
- Removed hardcoded navigation numbers from menus in favor of global hotkeys.

### Fixed
- Consistent back navigation at root now triggers quit confirmation instead of crashing.
- Standardized ASCII banner across all interactive screens.
- Fixed AWS region gating for cross-region queries.

### Removed
- Problematic git+ssh dependency in `requirements.txt`.
- "0. Exit" menu options from all screens.

---
*Created by TTox.Tech*
