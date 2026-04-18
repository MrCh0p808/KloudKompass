# 03 Error Patterns & Gotchas Library

Mistakes that have cost real time. Organized by **technique**, not project.

## Python & Runtime Safety
```text
❌ Using `subprocess.run(cmd, shell=True)` with user input
   → NEVER use shell=True. Always pass command as a list. Command injection risk.

❌ Catching bare `except Exception` and swallowing errors
   → Always log with context: `logger.error(f'[Module.method] {error}', exc_info=True)`
   → Re-raise or return structured error. Never return None for crashes.

❌ Using mutable default arguments (e.g., `def foo(data={})`)
   → Use `None` default + `if data is None: data = {}` pattern.

❌ Modifying a frozen dataclass in-place
   → Kloud Kompass SessionState is frozen. Always use `with_*()` → returns NEW instance.
   → Call `update_session(new_session)` after creating new instance.

❌ Global mutable state without thread safety
   → `_session`, `_navigator`, `_cost_cache` are global singletons.
   → Safe for single-threaded TUI, but never assume thread safety.

❌ Using `type(x) == str` instead of `isinstance(x, str)`
   → Always use isinstance() for type checking. Handles subclasses correctly.

❌ String formatting with `%` or `.format()` in f-string-capable code
   → Use f-strings consistently. They're faster and more readable.
```

## Subprocess & CLI Integration
```text
❌ Not handling `subprocess.TimeoutExpired` separately from `CalledProcessError`
   → Timeout = network/performance issue. CalledProcessError = API/permission error.
   → Different error messages, different recovery paths.

❌ Assuming CLI output is always valid JSON
   → Always wrap `json.loads()` in try-catch with `ParsingError`.
   → Log `raw_output[:500]` for debugging, never the full output (could be huge).

❌ Forgetting `--output json` flag in AWS CLI commands
   → AWS CLI defaults to `text` output. Always specify `--output json`.

❌ Not handling pagination tokens
   → AWS APIs return `NextPageToken`. Always paginate or use paginate_aws_cost_explorer().
   → Guard against infinite loops: max page count + duplicate token detection.

❌ Passing unsanitized user input to subprocess args
   → Profile names, region strings, dates - all must be validated before subprocess.
   → Use allowlists for enum-like values (providers, regions, breakdowns).

❌ Not setting timeout on subprocess.run()
   → Default should be 120s. Always pass `timeout=` parameter.
   → Timeout error should suggest narrowing date range or checking network.
```

## TUI & Screen Lifecycle
```text
❌ Calling `input()` directly instead of `self.get_input()`
   → `get_input()` intercepts q/b navigation intents globally.
   → Direct `input()` bypasses navigation contract - user can't quit/back.

❌ Printing headers in `render()` instead of `mount()`
   → mount() owns: screen clear + header (runs once)
   → render() owns: dynamic content only (called on each loop)
   → Violation causes duplicate headers.

❌ Returning string literals from `handle_input()` without matching expected values
   → Only "back", "exit", None, or Screen instances are valid returns.
   → Any other string is silently treated as a Screen push, causing crashes.

❌ Forgetting to call `update_session()` after `with_*()` methods
   → `session.with_provider("aws")` returns a NEW instance but doesn't update global.
   → Must always: `update_session(self.session.with_provider("aws"))`

❌ Not resetting `_mounted = False` when screen needs re-rendering
   → The `_mounted` guard prevents duplicate mount(). Set to False to force re-mount.
```

## Click CLI Patterns
```text
❌ Using `@click.option(prompt=...)` for non-interactive commands
   → Prompting breaks piped usage. Use `required=True` and let user pass via flag.

❌ Not providing `--help` text for options and commands
   → Every command and option must have help text. This IS the documentation.

❌ Forgetting `sys.exit(1)` on error paths in CLI
   → Shell scripts checking `$?` need non-zero exit codes on failure.

❌ Using `click.echo()` for errors instead of `click.echo(..., err=True)`
   → Errors should go to stderr, not stdout. Allows piping stdout safely.
```

## Import & Module Resolution
```text
❌ Using relative imports (from ..utils.x import y) inconsistently
   → Always use absolute: `from kloudkompass.utils.parsers import validate_date_format`

❌ Circular imports between tui/ and core/ modules
   → Use TYPE_CHECKING guard: `if TYPE_CHECKING: from kloudkompass.tui.screens import Screen`
   → Or use lazy imports inside functions.

❌ Importing at module level when lazy import is needed
   → Provider factory uses lazy imports. Don't add top-level imports that defeat this.
```

## Environment & Configuration
```text
❌ Debugging Python code when `aws` CLI isn't in PATH
   → `which aws` FIRST. WSL PATH doesn't always include Windows executables.

❌ Assuming `~/.kloudkompass/config.toml` exists on first run
   → Always create with defaults if missing. Use `os.makedirs(exist_ok=True)`.

❌ Not handling TOML parsing errors gracefully
   → Corrupted config file should show clear error, not crash with traceback.

❌ Hardcoding paths with `/` separator
   → Use `pathlib.Path` or `os.path.join()`. Kloud Kompass runs on Linux/WSL but respect OS conventions.
```

> **Add to this list every time a new pattern is discovered.** This is the project's battle-hardened neural net.
