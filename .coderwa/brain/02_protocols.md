# 02 Protocols & Layered Debugging

## Session Start Protocol (Kloud Kompass Edition)
Before writing any code or asking questions, the Agent must:
1. Read `.coderwa/master_report.md` to understand current Phase & Wave.
2. Read `.coderwa/brain/04_phases_waves.md` to identify the immediate next task.
3. Read `.coderwa/rules/` for capability-specific context.
4. Read `.coderwa/Kloud Kompass_data/context/state.md` for active ticket.
5. If context is missing, immediately report it to the Developer using `notify_user`.

## Pre-Code Checklist (Python / CLI / TUI)
```markdown
☐ Does this address the *exact* user prompt?
☐ Are all imports using absolute package paths (e.g., `kloudkompass.core.exceptions`)?
☐ Have I handled edge cases (CLI not installed, credentials expired, malformed JSON, subprocess timeout)?
☐ Has the target file been reviewed via `view_file` to prevent blind overwrites?
☐ Will `pytest` pass? Will `mypy` pass?
☐ Does the TUI Screen implement the mount/render/unmount lifecycle correctly?
☐ Does immutable SessionState use `with_*()` methods (no in-place mutation)?
☐ Does the provider follow the factory pattern in `core/provider_factory.py`?
```

## Layer-First Diagnosis (CLI/TUI Debugging)
Never fix blindly. Trace the error layer by layer.

```
App not working?
├── 1. Is the CLI installed?              → `which kloudkompass` or `pip show kloudkompass`
│    ├── No  → Package not installed. Run `pip install -e .`
│    └── Yes → Next layer.
├── 2. Does the command parse?            → `kloudkompass --help`, `kloudkompass cost --help`
│    ├── No  → Click group/command registration error.
│    └── Yes → Next layer.
├── 3. Does the provider CLI exist?       → `which aws`, `which az`, `which gcloud`
│    ├── No  → Provider CLI not installed. Show install instructions.
│    └── Yes → Next layer.
├── 4. Are credentials valid?             → `aws sts get-caller-identity`
│    ├── No  → Credential error. Guide user to `aws configure`.
│    └── Yes → Next layer.
├── 5. Does the subprocess call succeed?  → Run the raw CLI command manually
│    ├── No  → API error (permissions, disabled service, throttling).
│    └── Yes → Next layer.
└── 6. Does the parser handle the output? → Check JSON structure matches expectations
     ├── Parse error → Schema mismatch. Log `raw_output[:500]`.
     └── Clean parse → Logic error in display/export layer.
```

**Key Principle:** Prove each layer works before moving to the next. Changing Python code to fix an AWS IAM permissions issue wastes time and creates regressions.

## Decision Tree for Ambiguity
If multiple solutions exist, present them as **Option A** vs **Option B** in a markdown table.
- Detail the Performance, Security, and Complexity of each.
- Wait for the Developer to make the final architectural decision before proceeding.

## Kloud Kompass-Specific Debug Patterns
| Symptom | First Check | Likely Cause |
|---------|-------------|-------------|
| `subprocess.TimeoutExpired` | Network connectivity | VPN/proxy blocking AWS API |
| `json.JSONDecodeError` | Run CLI command manually | CLI version mismatch or missing `--output json` |
| `Kloud KompassError: CLI not found` | `which <cli_name>` | PATH not configured in WSL |
| TUI screen not rendering | Check `_mounted` flag | `mount()` guard preventing re-render |
| Session state lost | Check `update_session()` calls | Forgot to call `update_session()` after `with_*()` |
| Cache returning stale data | Check TTL and profile/region | Cache key doesn't include profile/region |
| `NotImplementedError` raised | Check provider module | Feature stub not yet implemented |
