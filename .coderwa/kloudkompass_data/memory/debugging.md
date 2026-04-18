# Debugging Log (Kloud Kompass CANONICAL)

Historical record of critical bug resolutions to prevent regression.

## Phase 2.6 Fixes (February 2026)

### TUI Navigation Contract
- **Symptom**: User couldn't quit from Cost Wizard mid-flow.
- **Root Cause**: `prompts.py` used raw `input()` instead of `get_input()`, bypassing navigation interception.
- **Resolution**: All prompts intercept `q`/`b` via `_check_navigation()` helper.
- **Reference**: `tui/prompts.py` lines 21-35.

### Session State Immutability
- **Symptom**: Session changes disappeared between screens.
- **Root Cause**: `with_provider("aws")` returns new instance but wasn't calling `update_session()`.
- **Resolution**: Enforced `update_session(self.session.with_*(...))` pattern in all wizards.
- **Reference**: `tui/session.py`, `tui/cost_menu.py`.

### Cache Key Collision
- **Symptom**: Different profile queries returned same cached result.
- **Root Cause**: Cache key hash didn't include all distinguishing parameters.
- **Resolution**: Key generation uses `json.dumps(key_data, sort_keys=True)` with SHA-256.
- **Pattern**: Always include profile, region, and all query params in cache key.

## Known Open Issues
- [ ] `prompts.py` functions bypass Screen `get_input()` (they're standalone functions, not Screen methods)
- [ ] Dashboard `_switch_view()` only changes button styles, doesn't swap content
- [ ] `confirm_quit()` in `screens.py` uses raw `input()` instead of `get_input()`
- [ ] `AWSCostProvider._parse_grouped_response` shadows variable `data` on line 222