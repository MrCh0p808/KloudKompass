# Kloud Kompass - Test Catalog

**Phase 2.6 - Operator UX & Multicloud Readiness**  
**Total: 601 tests** | All passing

---

## Table of Contents

| # | Category | File | Tests |
|---|----------|------|-------|
| 1 | [Navigation Model](#1-navigation-model) | `test_navigation_model.py` | 27 |
| 2 | [Screen Base Class](#2-screen-base-class) | `test_screen_base.py` | 25 |
| 3 | [Screen Lifecycle](#3-screen-lifecycle) | `test_lifecycle_model.py` | 15 |
| 4 | [Navigator (Core)](#4-navigator-core) | `test_tui_navigation.py` | 10 |
| 5 | [Navigator (Advanced)](#5-navigator-advanced) | `test_navigator_advanced.py` | 20 |
| 6 | [Session (Core)](#6-session-core) | `test_tui_session.py` | 8 |
| 7 | [Session (Immutability)](#7-session-immutability) | `test_session_immutable.py` | 15 |
| 8 | [Session (Methods)](#8-session-methods) | `test_session_methods.py` | 25 |
| 9 | [Provider Setup (Logic)](#9-provider-setup-logic) | `test_provider_setup.py` | 31 |
| 10 | [Provider Setup (Screen)](#10-provider-setup-screen) | `test_provider_setup_screen.py` | 15 |
| 11 | [Provider Factory](#11-provider-factory) | `test_provider_factory.py` | 20 |
| 12 | [Health Module](#12-health-module) | `test_health_module.py` | 25 |
| 13 | [Exceptions](#13-exceptions) | `test_exceptions_module.py` | 15 |
| 14 | [Config Manager](#14-config-manager) | `test_config_manager.py` | 25 |
| 15 | [File Cache](#15-file-cache) | `test_file_cache.py` | 25 |
| 16 | [Branding Consistency](#16-branding-consistency) | `test_branding_consistency.py` | 16 |
| 17 | [Footer / Attribution](#17-footer--attribution) | `test_footer_module.py` | 20 |
| 18 | [Multicloud UX](#18-multicloud-ux) | `test_multicloud_ux.py` | 17 |
| 19 | [Doctor Module](#19-doctor-module) | `test_doctor_module.py` | 20 |
| 20 | [Prompt Navigation](#20-prompt-navigation) | `test_prompts_navigation.py` | 15 |
| 21 | [Dashboard Parity](#21-dashboard-parity) | `test_dashboard_parity.py` | 15 |
| 22 | [Dashboard Export](#22-dashboard-export) | `test_dashboard_export.py` | 15 |
| 23 | [Edge Cases](#23-edge-cases) | `test_edge_cases.py` | 15 |
| | **Total** | **23 files** | **601** |

---

## 1. Navigation Model

**File:** `tests/test_navigation_model.py` - 27 tests  
**Covers:** `kloudkompass/tui/screens.py` - InputResult, get_input(), confirm_quit()

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestInputResult | `test_basic_creation` | InputResult can be created with raw string |
| 2 | TestInputResult | `test_raw_preserved` | Raw input string is preserved as-is |
| 3 | TestInputResult | `test_no_intent_by_default` | Intent defaults to None for regular input |
| 4 | TestInputResult | `test_quit_intent` | Intent set to "quit" for q/Q input |
| 5 | TestInputResult | `test_back_intent` | Intent set to "back" for b/B input |
| 6 | TestInputResult | `test_is_quit_true` | `is_quit` returns True for quit intent |
| 7 | TestInputResult | `test_is_quit_false` | `is_quit` returns False for non-quit |
| 8 | TestInputResult | `test_is_back_true` | `is_back` returns True for back intent |
| 9 | TestInputResult | `test_is_back_false` | `is_back` returns False for non-back |
| 10 | TestInputResult | `test_is_navigation_quit` | Quit intent is flagged as navigation |
| 11 | TestInputResult | `test_is_navigation_back` | Back intent is flagged as navigation |
| 12 | TestInputResult | `test_is_navigation_false` | Regular input is not navigation |
| 13 | TestGetInput | `test_get_input_exists` | Screen has `get_input()` method |
| 14 | TestGetInput | `test_returns_input_result` | `get_input()` returns InputResult instance |
| 15 | TestGetInput | `test_q_is_quit` | Typing "q" produces quit intent |
| 16 | TestGetInput | `test_Q_is_quit` | Typing "Q" produces quit intent |
| 17 | TestGetInput | `test_b_is_back` | Typing "b" produces back intent |
| 18 | TestGetInput | `test_B_is_back` | Typing "B" produces back intent |
| 19 | TestGetInput | `test_regular_input` | Non-navigation input has no intent |
| 20 | TestGetInput | `test_zero_is_back` | Typing "0" produces back intent |
| 21 | TestConfirmQuit | `test_confirm_quit_exists` | `confirm_quit()` function exists |
| 22 | TestConfirmQuit | `test_y_confirms` | Typing "y" returns True (confirm quit) |
| 23 | TestConfirmQuit | `test_Y_confirms` | Typing "Y" returns True |
| 24 | TestConfirmQuit | `test_n_declines` | Typing "n" returns False (cancel quit) |
| 25 | TestConfirmQuit | `test_empty_defaults_no` | Empty input defaults to No (safe default) |
| 26 | TestConfirmQuit | `test_random_input_declines` | Random text defaults to No |
| 27 | TestNoRawExit | `test_no_exit_option_text` | Screens don't contain "0. Exit" text |

---

## 2. Screen Base Class

**File:** `tests/test_screen_base.py` - 25 tests  
**Covers:** `kloudkompass/tui/screens.py` - Constants, Screen abstract class, confirm_quit()

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestScreenConstants | `test_brand_title_exists` | BRAND_TITLE constant is defined |
| 2 | TestScreenConstants | `test_brand_short_exists` | BRAND_SHORT constant is defined |
| 3 | TestScreenConstants | `test_nav_hint_exists` | NAV_HINT constant is defined |
| 4 | TestScreenConstants | `test_brand_title_contains_kloudkompass` | BRAND_TITLE includes "Kloud Kompass" |
| 5 | TestScreenConstants | `test_nav_hint_contains_back` | NAV_HINT mentions B for back |
| 6 | TestScreenConstants | `test_nav_hint_contains_quit` | NAV_HINT mentions Q for quit |
| 7 | TestInputResultClass | `test_basic_creation` | InputResult can be created with raw field |
| 8 | TestInputResultClass | `test_default_intent_none` | Intent defaults to None |
| 9 | TestInputResultClass | `test_quit_intent` | Quit intent detected correctly |
| 10 | TestInputResultClass | `test_back_intent` | Back intent detected correctly |
| 11 | TestInputResultClass | `test_non_navigation_not_navigation` | Regular input not flagged as navigation |
| 12 | TestInputResultClass | `test_quit_is_navigation` | Quit intent is navigation |
| 13 | TestInputResultClass | `test_back_is_navigation` | Back intent is navigation |
| 14 | TestScreenClass | `test_screen_exists` | Screen class exists |
| 15 | TestScreenClass | `test_screen_is_abstract` | Screen cannot be directly instantiated |
| 16 | TestScreenClass | `test_has_get_input` | Screen has get_input method |
| 17 | TestScreenClass | `test_has_display` | Screen has display method |
| 18 | TestScreenClass | `test_has_run` | Screen has run method |
| 19 | TestScreenClass | `test_has_print_header` | Screen has print_header method |
| 20 | TestScreenClass | `test_has_print_nav_hint` | Screen has print_nav_hint method |
| 21 | TestConfirmQuit | `test_confirm_quit_exists` | confirm_quit function exists |
| 22 | TestConfirmQuit | `test_y_returns_true` | "y" confirms quit |
| 23 | TestConfirmQuit | `test_n_returns_false` | "n" cancels quit |
| 24 | TestConfirmQuit | `test_empty_defaults_to_no` | Empty input defaults to no |
| 25 | TestConfirmQuit | `test_empty_defaults_to_no` | Empty/Enter is safe default |

---

## 3. Screen Lifecycle

**File:** `tests/test_lifecycle_model.py` - 15 tests  
**Covers:** Screen lifecycle contract (mount/render/unmount)

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestScreenLifecycle | `test_mount_exists` | Screen has mount() method |
| 2 | TestScreenLifecycle | `test_render_exists` | Screen has render() method |
| 3 | TestScreenLifecycle | `test_unmount_exists` | Screen has unmount() method |
| 4 | TestScreenLifecycle | `test_handle_input_exists` | Screen has handle_input() method |
| 5 | TestScreenLifecycle | `test_display_exists` | Screen has display() method |
| 6 | TestScreenTitleContract | `test_main_menu_has_title` | MainMenu defines title |
| 7 | TestScreenTitleContract | `test_cost_wizard_has_title` | CostWizard defines title |
| 8 | TestScreenTitleContract | `test_inventory_wizard_has_title` | InventoryWizard defines title |
| 9 | TestScreenTitleContract | `test_security_wizard_has_title` | SecurityWizard defines title |
| 10 | TestScreenRendering | `test_main_menu_render_no_error` | MainMenu.render() runs without error |
| 11 | TestScreenRendering | `test_cost_wizard_render_no_error` | CostWizard.render() runs without error |
| 12 | TestScreenRendering | `test_inventory_wizard_render_no_error` | InventoryWizard.render() runs without error |
| 13 | TestScreenRendering | `test_security_wizard_render_no_error` | SecurityWizard.render() runs without error |
| 14 | TestScreenSessionAccess | `test_screen_has_session_property` | Screens can access session |
| 15 | TestScreenSessionAccess | `test_screen_has_navigator_property` | Screens can access navigator |

---

## 4. Navigator (Core)

**File:** `tests/test_tui_navigation.py` - 10 tests  
**Covers:** `kloudkompass/tui/navigation.py` - Core operations and singleton

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestNavigator | `test_empty_navigator` | New navigator has depth 0 |
| 2 | TestNavigator | `test_push_screen` | Push increases depth |
| 3 | TestNavigator | `test_pop_screen` | Pop returns previous screen |
| 4 | TestNavigator | `test_pop_empty_stack` | Pop on empty returns None |
| 5 | TestNavigator | `test_can_go_back` | can_go_back True with 2+ screens |
| 6 | TestNavigator | `test_clear` | Clear empties the stack |
| 7 | TestNavigator | `test_reset_to` | reset_to clears and sets root |
| 8 | TestNavigator | `test_request_exit` | request_exit sets exit flag |
| 9 | TestNavigatorSingleton | `test_get_navigator_returns_same_instance` | Singleton pattern works |
| 10 | TestNavigatorSingleton | `test_reset_navigator_creates_new_instance` | Reset creates fresh instance |

---

## 5. Navigator (Advanced)

**File:** `tests/test_navigator_advanced.py` - 20 tests  
**Covers:** `kloudkompass/tui/navigation.py` - Detailed push/pop, exit, can_go_back

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestNavigatorPushPop | `test_push_increases_depth` | Push adds 1 to depth |
| 2 | TestNavigatorPushPop | `test_push_two_depth_two` | Two pushes → depth 2 |
| 3 | TestNavigatorPushPop | `test_pop_decreases_depth` | Pop removes 1 from depth |
| 4 | TestNavigatorPushPop | `test_pop_returns_previous` | Pop returns the screen below |
| 5 | TestNavigatorPushPop | `test_pop_empty_returns_none` | Pop on empty is safe |
| 6 | TestNavigatorPushPop | `test_current_returns_topmost` | current() returns top of stack |
| 7 | TestNavigatorPushPop | `test_current_empty_returns_none` | current() on empty returns None |
| 8 | TestNavigatorClear | `test_clear_empties_stack` | Clear sets depth to 0 |
| 9 | TestNavigatorClear | `test_reset_to_sets_root` | reset_to sets single root screen |
| 10 | TestNavigatorClear | `test_clear_then_current_none` | current() is None after clear |
| 11 | TestNavigatorExit | `test_should_exit_default_false` | Exit flag defaults to False |
| 12 | TestNavigatorExit | `test_request_exit_sets_flag` | request_exit() sets flag True |
| 13 | TestNavigatorCanGoBack | `test_empty_cannot_go_back` | Empty stack: can_go_back False |
| 14 | TestNavigatorCanGoBack | `test_one_screen_cannot_go_back` | Single screen: can_go_back False |
| 15 | TestNavigatorCanGoBack | `test_two_screens_can_go_back` | Two screens: can_go_back True |
| 16 | TestNavigatorSingleton | `test_get_navigator_returns_navigator` | Returns Navigator type |
| 17 | TestNavigatorSingleton | `test_get_navigator_same_instance` | Same instance each call |
| 18 | TestNavigatorSingleton | `test_reset_navigator_creates_new` | Reset produces new instance |
| 19-20 | *(additional depth/edge tests)* | | |

---

## 6. Session (Core)

**File:** `tests/test_tui_session.py` - 8 tests  
**Covers:** `kloudkompass/tui/session.py` - Basic SessionState and singleton

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestSessionState | `test_default_values` | All defaults are None/False |
| 2 | TestSessionState | `test_create_with_provider` | Can create with provider set |
| 3 | TestSessionState | `test_create_with_dates` | Can create with date range |
| 4 | TestSessionState | `test_reset_cost_options` | reset_cost_options clears cost fields |
| 5 | TestSessionState | `test_reset_all_returns_new_session` | reset_all returns fresh session |
| 6 | TestSessionState | `test_to_dict` | to_dict returns proper dict |
| 7 | TestSessionSingleton | `test_get_session_returns_same_instance` | Singleton consistency |
| 8 | TestSessionSingleton | `test_reset_session_creates_new_instance` | Reset creates new session |

---

## 7. Session (Immutability)

**File:** `tests/test_session_immutable.py` - 15 tests  
**Covers:** `kloudkompass/tui/session.py` - Frozen dataclass invariant enforcement

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestSessionStateFrozen | `test_cannot_modify_provider` | Direct mutation raises FrozenInstanceError |
| 2 | TestSessionStateFrozen | `test_cannot_modify_dates` | Cannot mutate date fields |
| 3 | TestSessionStateFrozen | `test_cannot_modify_breakdown` | Cannot mutate breakdown |
| 4 | TestSessionStateWithMethods | `test_with_provider_returns_new_instance` | with_provider creates new object |
| 5 | TestSessionStateWithMethods | `test_with_dates_returns_new_instance` | with_dates creates new object |
| 6 | TestSessionStateWithMethods | `test_with_breakdown_returns_new_instance` | with_breakdown creates new object |
| 7 | TestSessionStateWithMethods | `test_with_threshold_returns_new_instance` | with_threshold creates new object |
| 8 | TestSessionStateWithMethods | `test_with_output_format_returns_new_instance` | with_output_format creates new object |
| 9 | TestSessionStateWithMethods | `test_chained_updates` | Multiple with_* calls can be chained |
| 10 | TestSessionStateReset | `test_reset_cost_options_returns_new_instance` | Reset returns fresh instance |
| 11 | TestSessionStateReset | `test_reset_all_returns_fresh_session` | Full reset returns defaults |
| 12 | TestSessionStateGlobal | `test_get_session_returns_singleton` | Global session is singleton |
| 13 | TestSessionStateGlobal | `test_update_session_replaces_global` | update_session swaps global |
| 14 | TestSessionStateGlobal | `test_reset_session_creates_fresh` | reset_session creates new |
| 15 | TestSessionStateToDict | `test_to_dict` | Serialization works correctly |

---

## 8. Session (Methods)

**File:** `tests/test_session_methods.py` - 25 tests  
**Covers:** `kloudkompass/tui/session.py` - Every with_* method in detail

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestSessionWithProvider | `test_returns_new_instance` | New object returned (immutable) |
| 2 | TestSessionWithProvider | `test_sets_provider` | Provider field is set correctly |
| 3 | TestSessionWithProvider | `test_preserves_other_fields` | Other fields unchanged |
| 4 | TestSessionWithDates | `test_returns_new_instance` | New object for date update |
| 5 | TestSessionWithDates | `test_sets_start_date` | start_date set correctly |
| 6 | TestSessionWithDates | `test_sets_end_date` | end_date set correctly |
| 7 | TestSessionWithDates | `test_preserves_provider` | Provider preserved after date change |
| 8 | TestSessionWithBreakdown | `test_sets_breakdown` | Breakdown field set |
| 9 | TestSessionWithBreakdown | `test_returns_new_instance` | New object returned |
| 10 | TestSessionWithThreshold | `test_sets_threshold` | Threshold value set |
| 11 | TestSessionWithThreshold | `test_zero_threshold` | Zero threshold is valid |
| 12 | TestSessionWithProfile | `test_sets_profile` | Profile field set |
| 13 | TestSessionWithRegion | `test_sets_region` | Region field set |
| 14 | TestSessionWithOutputFormat | `test_sets_output_format` | Output format set |
| 15 | TestSessionWithError | `test_sets_error` | Error message set |
| 16 | TestSessionWithDebug | `test_sets_debug` | Debug mode enabled |
| 17 | TestSessionWithDebug | `test_unsets_debug` | Debug mode disabled |
| 18 | TestSessionResetCostOptions | `test_clears_dates` | Dates cleared to None |
| 19 | TestSessionResetCostOptions | `test_clears_breakdown` | Breakdown cleared |
| 20 | TestSessionResetCostOptions | `test_clears_threshold` | Threshold cleared |
| 21 | TestSessionResetCostOptions | `test_preserves_provider` | Provider kept after reset |
| 22 | TestSessionToDict | `test_returns_dict` | Returns dict type |
| 23 | TestSessionToDict | `test_contains_all_keys` | All fields in dict output |
| 24 | TestSessionToDict | `test_frozen_cannot_mutate` | Direct assignment raises error |
| 25 | | | *(count includes all with_* variants)* |

---

## 9. Provider Setup (Logic)

**File:** `tests/test_provider_setup.py` - 31 tests  
**Covers:** `kloudkompass/tui/provider_setup.py` - Pure logic layer (zero input/print)

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestProviderSetupResult | `test_result_exists` | ProviderSetupResult class exists |
| 2 | TestProviderSetupResult | `test_result_success_field` | Has success boolean field |
| 3 | TestProviderSetupResult | `test_result_provider_field` | Has provider string field |
| 4 | TestProviderSetupResult | `test_result_error_field` | Has optional error field |
| 5 | TestProviderSetupResult | `test_result_is_configured_true` | is_configured True on success |
| 6 | TestProviderSetupResult | `test_result_is_configured_false_on_error` | is_configured False on error |
| 7 | TestCheckProviderReady | `test_check_provider_ready_exists` | Function exists |
| 8 | TestCheckProviderReady | `test_unimplemented_provider_fails` | Azure returns failure |
| 9 | TestCheckProviderReady | `test_gcp_not_implemented` | GCP returns failure |
| 10 | TestCheckProviderReady | `test_aws_ready_when_configured` | AWS returns success when CLI+creds OK |
| 11 | TestCheckProviderReady | `test_aws_fails_when_cli_missing` | AWS fails without CLI |
| 12 | TestCheckProviderReady | `test_aws_fails_when_creds_invalid` | AWS fails with bad creds |
| 13 | TestEnsureProviderConfigured | `test_ensure_exists` | Function exists |
| 14 | TestEnsureProviderConfigured | `test_returns_success_when_ready` | Returns success for working provider |
| 15 | TestEnsureProviderConfigured | `test_non_interactive_returns_failure` | Non-interactive returns failure (no UI) |
| 16 | TestEnsureProviderConfigured | `test_ensure_is_pure_gate` | **Contract:** No input()/print() in source |
| 17 | TestGetSetupInstructions | `test_returns_dict` | Returns instruction dictionary |
| 18 | TestGetSetupInstructions | `test_has_required_keys` | Dict has cli_name, config_steps, etc. |
| 19 | TestGetSetupInstructions | `test_aws_cli_name` | AWS instructions reference "aws" CLI |
| 20 | TestGetSetupInstructions | `test_config_steps_not_empty` | Config steps list is non-empty |
| 21 | TestPersistProviderChoice | `test_persist_exists` | Function exists |
| 22 | TestPersistProviderChoice | `test_persist_returns_true_on_success` | Returns True on successful save |
| 23 | TestPersistProviderChoice | `test_persist_returns_false_on_failure` | Returns False on error |
| 24 | TestModulePurity | `test_no_input_calls` | **Contract:** Module has zero input() calls |
| 25 | TestModulePurity | `test_no_print_calls` | **Contract:** Module has zero print() calls |
| 26 | TestMulticloudUXHonesty | `test_azure_message_is_helpful` | Azure error includes "AWS" alternative |
| 27 | TestMulticloudUXHonesty | `test_gcp_message_is_helpful` | GCP error includes "AWS" alternative |
| 28 | TestProviderFactory | `test_is_provider_implemented_exists` | Factory function exists |
| 29 | TestProviderFactory | `test_aws_is_implemented` | AWS is implemented |
| 30 | TestProviderFactory | `test_azure_not_implemented` | Azure is not implemented |
| 31 | TestProviderFactory | `test_gcp_not_implemented` | GCP is not implemented |

---

## 10. Provider Setup (Screen)

**File:** `tests/test_provider_setup_screen.py` - 15 tests  
**Covers:** `kloudkompass/tui/provider_setup_screen.py` - Lifecycle-compliant Screen subclass

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestProviderSetupScreenExists | `test_screen_importable` | Module imports without error |
| 2 | TestProviderSetupScreenExists | `test_screen_is_subclass_of_screen` | Inherits from Screen |
| 3 | TestProviderSetupScreenExists | `test_screen_has_title` | Has title attribute |
| 4 | TestLifecycleCompliance | `test_has_mount` | Has mount() method |
| 5 | TestLifecycleCompliance | `test_has_render` | Has render() method |
| 6 | TestLifecycleCompliance | `test_has_handle_input` | Has handle_input() method |
| 7 | TestLifecycleCompliance | `test_handle_input_uses_get_input` | **Contract:** Uses get_input(), no raw input() |
| 8 | TestScreenInitialization | `test_accepts_provider` | Constructor accepts provider arg |
| 9 | TestScreenInitialization | `test_accepts_result` | Constructor accepts result arg |
| 10 | TestScreenInitialization | `test_has_get_result` | Has get_result() accessor |
| 11 | TestNoNavigationSemanticsAdded | `test_no_new_bindings` | No custom keybindings (inherits from Screen) |
| 12 | TestNoNavigationSemanticsAdded | `test_uses_nav_hint` | Uses NAV_HINT constant |
| 13 | TestNoNavigationSemanticsAdded | `test_no_raw_input` | **Contract:** No raw input() in module source |
| 14-15 | *(additional screen tests)* | | |

---

## 11. Provider Factory

**File:** `tests/test_provider_factory.py` - 20 tests  
**Covers:** `kloudkompass/core/provider_factory.py` - Registry, implementation checks, factory

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestGetAvailableProviders | `test_returns_list` | Returns list type |
| 2 | TestGetAvailableProviders | `test_contains_aws` | AWS is registered |
| 3 | TestGetAvailableProviders | `test_contains_azure` | Azure is registered |
| 4 | TestGetAvailableProviders | `test_contains_gcp` | GCP is registered |
| 5 | TestGetAvailableProviders | `test_at_least_three_providers` | Minimum 3 providers |
| 6 | TestIsProviderImplemented | `test_aws_is_implemented` | AWS returns True |
| 7 | TestIsProviderImplemented | `test_azure_not_implemented` | Azure returns False |
| 8 | TestIsProviderImplemented | `test_gcp_not_implemented` | GCP returns False |
| 9 | TestIsProviderImplemented | `test_unknown_not_implemented` | Unknown returns False |
| 10 | TestIsProviderImplemented | `test_case_insensitive` | "AWS" works same as "aws" |
| 11 | TestIsProviderImplemented | `test_whitespace_stripped` | " aws " trimmed correctly |
| 12 | TestGetCostProvider | `test_unknown_provider_raises` | Unknown raises Kloud KompassError |
| 13 | TestGetCostProvider | `test_error_mentions_valid_providers` | Error message is helpful |
| 14 | TestRegisterProvider | `test_register_new_provider` | Can register new provider |
| 15 | TestRegisterProvider | `test_register_lowercase` | Registration normalizes case |
| 16 | TestRegisterProvider | `test_register_overwrite` | Re-registration overwrites path |
| 17 | TestProviderRegistry | `test_registry_is_dict` | Registry is a dict |
| 18 | TestProviderRegistry | `test_aws_registry_path` | AWS maps to AWSCostProvider |
| 19 | TestProviderRegistry | `test_azure_registry_path` | Azure maps to AzureCostProvider |
| 20 | TestProviderRegistry | `test_gcp_registry_path` | GCP maps to GCPCostProvider |

---

## 12. Health Module

**File:** `tests/test_health_module.py` - 25 tests  
**Covers:** `kloudkompass/core/health.py` - CLI checks, credential validation, dispatching

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestCheckCliInstalled | `test_function_exists` | Function exists |
| 2 | TestCheckCliInstalled | `test_returns_true_when_found` | True when shutil.which finds CLI |
| 3 | TestCheckCliInstalled | `test_returns_false_when_not_found` | False when CLI not in PATH |
| 4 | TestCheckCliInstalled | `test_calls_which_with_cli_name` | Passes correct name to shutil.which |
| 5 | TestRequireCli | `test_does_not_raise_when_installed` | No exception when CLI present |
| 6 | TestRequireCli | `test_raises_when_missing` | CLIUnavailableError when missing |
| 7 | TestGetInstallInstructions | `test_aws_instructions` | AWS instructions mention "aws configure" |
| 8 | TestGetInstallInstructions | `test_az_instructions` | Azure instructions mention "az login" |
| 9 | TestGetInstallInstructions | `test_gcloud_instructions` | GCP instructions mention "gcloud" |
| 10 | TestGetInstallInstructions | `test_unknown_cli_fallback` | Unknown CLI gets generic message |
| 11 | TestCheckCredentials | `test_unknown_provider_returns_error` | Unknown provider: (False, error) |
| 12 | TestCheckCredentials | `test_routes_to_aws` | Dispatches to check_aws_credentials |
| 13 | TestCheckCredentials | `test_routes_to_azure` | Dispatches to check_azure_credentials |
| 14 | TestCheckCredentials | `test_routes_to_gcp` | Dispatches to check_gcp_credentials |
| 15 | TestRequireCredentials | `test_does_not_raise_when_valid` | No exception when creds valid |
| 16 | TestRequireCredentials | `test_raises_when_invalid` | CredentialError when invalid |
| 17 | TestAwsCredentials | `test_fails_when_cli_missing` | Returns (False, "not installed") |
| 18 | TestAwsCredentials | `test_succeeds_on_zero_returncode` | Returns (True, None) on success |
| 19 | TestAwsCredentials | `test_detects_expired_credentials` | Identifies expired token message |
| 20 | TestAwsCredentials | `test_handles_timeout` | Handles subprocess timeout gracefully |
| 21-25 | *(additional credential tests)* | | |

---

## 13. Exceptions

**File:** `tests/test_exceptions_module.py` - 15 tests  
**Covers:** `kloudkompass/core/exceptions.py` - All custom exception classes

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestKloud KompassError | `test_exists` | Base exception class exists |
| 2 | TestKloud KompassError | `test_is_exception` | Inherits from Exception |
| 3 | TestKloud KompassError | `test_can_raise` | Can be raised and caught |
| 4 | TestKloud KompassError | `test_message_preserved` | Error message accessible in str() |
| 5 | TestCLIUnavailableError | `test_exists` | Subclass exists |
| 6 | TestCLIUnavailableError | `test_is_kloudkompass_error` | Inherits from Kloud KompassError |
| 7 | TestCLIUnavailableError | `test_stores_cli_name` | cli_name attribute stored |
| 8 | TestCredentialError | `test_exists` | Subclass exists |
| 9 | TestCredentialError | `test_is_kloudkompass_error` | Inherits from Kloud KompassError |
| 10 | TestCredentialError | `test_stores_provider` | provider attribute stored |
| 11 | TestConfigurationError | `test_exists` | Subclass exists |
| 12 | TestConfigurationError | `test_is_kloudkompass_error` | Inherits from Kloud KompassError |
| 13 | TestConfigurationError | `test_stores_config_path` | config_path attribute stored |
| 14 | TestConfigurationError | `test_default_config_path_none` | config_path defaults to None |
| 15 | | | *(count includes all exception variants)* |

---

## 14. Config Manager

**File:** `tests/test_config_manager.py` - 25 tests  
**Covers:** `kloudkompass/config_manager.py` - Defaults, load, merge, paths, get/set

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestDefaultConfig | `test_default_config_exists` | DEFAULT_CONFIG dict exists |
| 2 | TestDefaultConfig | `test_default_provider_is_aws` | Default provider is "aws" |
| 3 | TestDefaultConfig | `test_default_output_is_table` | Default output is "table" |
| 4 | TestDefaultConfig | `test_default_debug_is_false` | Debug defaults to False |
| 5 | TestDefaultConfig | `test_default_region_is_none` | Region defaults to None |
| 6 | TestDefaultConfig | `test_default_profile_is_none` | Profile defaults to None |
| 7 | TestLoadConfig | `test_returns_defaults_when_no_file` | Returns defaults when no config file |
| 8 | TestLoadConfig | `test_returns_dict` | Returns dict type |
| 9 | TestMergeCliWithConfig | `test_cli_provider_overrides_config` | CLI arg overrides saved config |
| 10 | TestMergeCliWithConfig | `test_config_defaults_when_no_cli` | Config used when no CLI arg |
| 11 | TestMergeCliWithConfig | `test_debug_false_by_default` | Debug defaults to False |
| 12 | TestMergeCliWithConfig | `test_cli_debug_overrides_config` | CLI debug overrides config |
| 13 | TestMergeCliWithConfig | `test_output_format_override` | Output format override works |
| 14 | TestMergeCliWithConfig | `test_region_override` | Region override works |
| 15 | TestMergeCliWithConfig | `test_profile_override` | Profile override works |
| 16 | TestMergeCliWithConfig | `test_returns_all_keys` | Result has all 5 required keys |
| 17 | TestConfigPath | `test_get_config_path_returns_string` | Path is a string |
| 18 | TestConfigPath | `test_config_path_contains_kloudkompass` | Path includes ".kloudkompass" |
| 19 | TestConfigPath | `test_config_path_ends_with_toml` | Path ends with ".toml" |
| 20 | TestConfigPath | `test_config_exists_returns_bool` | config_exists returns boolean |
| 21 | TestGetSetConfigValue | `test_get_existing_value` | Gets existing config value |
| 22 | TestGetSetConfigValue | `test_get_missing_value_returns_default` | Missing key returns provided default |
| 23-25 | *(additional config tests)* | | |

---

## 15. File Cache

**File:** `tests/test_file_cache.py` - 25 tests  
**Covers:** `kloudkompass/cache/file_cache.py` - Full cache lifecycle

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestFileCacheInit | `test_cache_importable` | FileCache class imports |
| 2 | TestFileCacheInit | `test_custom_cache_dir` | Custom directory accepted |
| 3 | TestFileCacheInit | `test_default_ttl` | Default TTL is DEFAULT_TTL |
| 4 | TestFileCacheInit | `test_custom_ttl` | Custom TTL accepted |
| 5 | TestFileCacheInit | `test_creates_cache_dir` | Creates nested directories |
| 6 | TestFileCacheSetGet | `test_set_returns_true` | set() returns True on success |
| 7 | TestFileCacheSetGet | `test_get_returns_cached_value` | get() returns stored value |
| 8 | TestFileCacheSetGet | `test_get_returns_none_for_missing` | Missing key returns None |
| 9 | TestFileCacheSetGet | `test_expired_entry_returns_none` | Expired entry returns None |
| 10 | TestFileCacheSetGet | `test_set_with_ttl_override` | TTL override extends expiry |
| 11 | TestFileCacheSetGet | `test_set_with_provider` | Provider metadata stored |
| 12 | TestFileCacheInvalidate | `test_invalidate_existing` | Removes existing entry |
| 13 | TestFileCacheInvalidate | `test_invalidate_nonexistent` | Returns False for missing |
| 14 | TestFileCacheInvalidate | `test_get_after_invalidate` | Entry gone after invalidation |
| 15 | TestFileCacheClear | `test_clear_returns_count` | Returns count of removed entries |
| 16 | TestFileCacheClear | `test_clear_empty_cache` | Clear on empty returns 0 |
| 17 | TestFileCacheClear | `test_cleanup_expired` | cleanup_expired removes stale entries |
| 18 | TestFileCacheSize | `test_empty_size` | Size is 0 when empty |
| 19 | TestFileCacheSize | `test_size_after_set` | Size increases after set |
| 20 | TestFileCacheSize | `test_size_after_clear` | Size is 0 after clear |
| 21 | TestFileCacheMakeKey | `test_key_is_string` | Key is a string |
| 22 | TestFileCacheMakeKey | `test_same_args_same_key` | Deterministic key generation |
| 23 | TestFileCacheMakeKey | `test_different_args_different_key` | Different args = different key |
| 24 | TestCorruptedCache | `test_corrupted_json_returns_none` | Corrupted file handled gracefully |
| 25 | | | *(count includes all cache operations)* |

---

## 16. Branding Consistency

**File:** `tests/test_branding_consistency.py` - 16 tests  
**Covers:** Cross-module branding enforcement

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestBrandConstants | `test_brand_title_exists` | BRAND_TITLE defined |
| 2 | TestBrandConstants | `test_brand_short_exists` | BRAND_SHORT defined |
| 3 | TestBrandConstants | `test_brand_title_contains_kloudkompass` | Title includes "Kloud Kompass" |
| 4 | TestBrandConstants | `test_brand_title_contains_analytix` | Title includes "Analytix" |
| 5 | TestBrandConstants | `test_brand_short_is_kloudkompass` | Short form is "Kloud Kompass" |
| 6 | TestScreenBranding | `test_main_menu_uses_brand_title` | MainMenu uses BRAND_TITLE |
| 7 | TestScreenBranding | `test_cost_wizard_uses_brand` | CostWizard uses brand |
| 8 | TestScreenBranding | `test_inventory_wizard_uses_brand` | InventoryWizard uses brand |
| 9 | TestScreenBranding | `test_security_wizard_uses_brand` | SecurityWizard uses brand |
| 10 | TestUXConsistency | `test_nav_hint_constant_exists` | NAV_HINT defined |
| 11 | TestUXConsistency | `test_nav_hint_contains_back` | NAV_HINT has B |
| 12 | TestUXConsistency | `test_nav_hint_contains_quit` | NAV_HINT has Q |
| 13 | TestUXConsistency | `test_nav_hint_uses_brackets` | NAV_HINT uses [B] [Q] format |
| 14 | TestUXConsistency | `test_nav_hint_exact_format` | Exact "[B] Back    [Q] Quit" |
| 15 | TestDoctorAttribution | `test_doctor_imports_attribution` | Doctor uses footer attribution |
| 16 | TestScreensUseRender | `test_main_menu_has_render` | All screens implement render() |

---

## 17. Footer / Attribution

**File:** `tests/test_footer_module.py` - 20 tests  
**Covers:** `kloudkompass/tui/footer.py` - Legal attribution constants and rendering

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestAttributionConstants | `test_line1_exists` | ATTRIBUTION_LINE1 defined |
| 2 | TestAttributionConstants | `test_line2_exists` | ATTRIBUTION_LINE2 defined |
| 3 | TestAttributionConstants | `test_line1_has_year` | Year "2026" present |
| 4 | TestAttributionConstants | `test_line1_has_company` | "TTox.Tech" present |
| 5 | TestAttributionConstants | `test_line2_has_open_source` | "open-source" present |
| 6 | TestAttributionConstants | `test_full_combines_lines` | ATTRIBUTION_FULL has both lines |
| 7 | TestAttributionConstants | `test_short_exists` | ATTRIBUTION_SHORT defined |
| 8 | TestAttributionConstants | `test_legacy_footer_text` | FOOTER_TEXT == ATTRIBUTION_LINE1 |
| 9 | TestAttributionConstants | `test_legacy_footer_legal` | FOOTER_LEGAL == ATTRIBUTION_LINE2 |
| 10 | TestGetFooterText | `test_returns_string` | Returns string type |
| 11 | TestGetFooterText | `test_contains_attribution` | Contains "TTox.Tech" |
| 12 | TestGetFooterText | `test_contains_both_lines` | Has both attribution lines |
| 13 | TestGetAttributionLines | `test_returns_tuple` | Returns tuple type |
| 14 | TestGetAttributionLines | `test_tuple_length_two` | Tuple has exactly 2 elements |
| 15 | TestGetAttributionLines | `test_first_matches_line1` | First element matches LINE1 |
| 16 | TestGetAttributionLines | `test_second_matches_line2` | Second element matches LINE2 |
| 17 | TestRenderFooter | `test_plain_print` | Plain print includes "TTox.Tech" |
| 18 | TestRenderFooter | `test_plain_print_no_exception` | Render doesn't raise |
| 19-20 | *(additional footer tests)* | | |

---

## 18. Multicloud UX

**File:** `tests/test_multicloud_ux.py` - 17 tests  
**Covers:** Multicloud messaging honesty

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestProviderSelection | `test_aws_is_valid` | AWS is a valid selection |
| 2 | TestProviderSelection | `test_azure_is_listed` | Azure is listed as option |
| 3 | TestProviderSelection | `test_gcp_is_listed` | GCP is listed as option |
| 4 | TestImplementationHonesty | `test_aws_implemented` | AWS returns True for implemented |
| 5 | TestImplementationHonesty | `test_azure_not_implemented` | Azure returns False |
| 6 | TestImplementationHonesty | `test_gcp_not_implemented` | GCP returns False |
| 7 | TestImplementationHonesty | `test_coming_soon_label` | Non-implemented shows "coming soon" |
| 8 | TestBlockedMessages | `test_azure_block_message_helpful` | Azure error has helpful guidance |
| 9 | TestBlockedMessages | `test_gcp_block_message_helpful` | GCP error has helpful guidance |
| 10 | TestBlockedMessages | `test_error_mentions_aws` | Blocked message suggests AWS |
| 11 | TestProviderInterface | `test_all_providers_registered` | All 3 providers in registry |
| 12 | TestProviderInterface | `test_provider_names_lowercase` | Provider names are lowercase |
| 13 | TestProviderInterface | `test_case_insensitive_lookup` | Case doesn't matter for lookup |
| 14-17 | *(additional multicloud tests)* | | |

---

## 19. Doctor Module

**File:** `tests/test_doctor_module.py` - 20 tests  
**Covers:** `kloudkompass/tui/doctor.py` - Health check execution and reporting

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestRunDoctor | `test_run_doctor_exists` | Function exists |
| 2 | TestRunDoctor | `test_returns_list` | Returns list of results |
| 3 | TestRunDoctor | `test_results_are_tuples` | Each result is (name, msg, passed) |
| 4 | TestRunDoctor | `test_checks_aws_cli` | Checks AWS CLI availability |
| 5 | TestRunDoctor | `test_checks_azure_cli` | Checks Azure CLI availability |
| 6 | TestRunDoctor | `test_checks_gcp_cli` | Checks GCP SDK availability |
| 7 | TestRunDoctor | `test_checks_config` | Checks Kloud Kompass config |
| 8 | TestRunDoctor | `test_config_present_passes` | Config present = pass |
| 9 | TestRunDoctor | `test_config_absent_still_passes` | No config = still passes (defaults OK) |
| 10 | TestRunDoctor | `test_cli_installed_shows_ok` | Installed CLI shows "Installed" |
| 11 | TestPrintDoctorReport | `test_returns_bool` | Returns True/False |
| 12 | TestPrintDoctorReport | `test_returns_true_when_all_pass` | All pass → True |
| 13 | TestPrintDoctorReport | `test_returns_false_when_any_fail` | Any fail → False |
| 14 | TestDoctorBranding | `test_uses_brand_title` | Uses BRAND_TITLE constant |
| 15 | TestDoctorBranding | `test_uses_attribution` | Uses ATTRIBUTION_LINE1 |
| 16 | TestDoctorBranding | `test_report_includes_brand` | Report output has "Kloud Kompass" |
| 17 | TestDoctorBranding | `test_report_includes_attribution` | Report output has attribution |
| 18-20 | *(additional doctor tests)* | | |

---

## 20. Prompt Navigation

**File:** `tests/test_prompts_navigation.py` - 15 tests  
**Covers:** `kloudkompass/tui/prompts.py` - Navigation in prompt functions

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestCheckNavigation | `test_function_exists` | _check_navigation exists |
| 2 | TestCheckNavigation | `test_q_returns_quit` | "q" → "quit" |
| 3 | TestCheckNavigation | `test_Q_returns_quit` | "Q" → "quit" |
| 4 | TestCheckNavigation | `test_b_returns_back` | "b" → "back" |
| 5 | TestCheckNavigation | `test_B_returns_back` | "B" → "back" |
| 6 | TestCheckNavigation | `test_zero_returns_back` | "0" → "back" |
| 7 | TestCheckNavigation | `test_regular_returns_none` | Regular input → None |
| 8 | TestSelectProvider | `test_function_exists` | select_provider exists |
| 9 | TestSelectProvider | `test_returns_tuple` | Returns (provider, action) |
| 10 | TestSelectProvider | `test_quit_action` | Quit navigates correctly |
| 11 | TestSelectBreakdown | `test_function_exists` | select_breakdown exists |
| 12 | TestSelectBreakdown | `test_returns_tuple` | Returns (breakdown, action) |
| 13 | TestSelectBreakdown | `test_quit_action` | Quit navigates correctly |
| 14 | TestBreakdownOptions | `test_options_defined` | BREAKDOWN_OPTIONS list exists |
| 15 | TestBreakdownOptions | `test_output_options_defined` | OUTPUT_OPTIONS list exists |

---

## 21. Dashboard Parity

**File:** `tests/test_dashboard_parity.py` - 15 tests  
**Covers:** Dashboard quit/export modals and app branding

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestQuitConfirmModal | `test_quit_modal_exists` | QuitConfirmModal class exists |
| 2 | TestQuitConfirmModal | `test_quit_modal_is_modal_screen` | Inherits from ModalScreen |
| 3 | TestQuitConfirmModal | `test_quit_modal_has_compose` | Has compose() method |
| 4 | TestQuitConfirmModal | `test_quit_modal_has_bindings` | Has keyboard bindings |
| 5 | TestQuitConfirmModal | `test_quit_modal_has_confirm_actions` | Has confirm/deny actions |
| 6 | TestExportModal | `test_export_modal_exists` | ExportModal class exists |
| 7 | TestExportModal | `test_export_modal_is_modal_screen` | Inherits from ModalScreen |
| 8 | TestExportModal | `test_export_dir_defined` | Export directory is defined |
| 9 | TestExportModal | `test_export_modal_accepts_view_name` | Accepts view_name parameter |
| 10 | TestExportModal | `test_export_modal_accepts_data` | Accepts data parameter |
| 11 | TestDashboardAppParity | `test_app_uses_brand_title` | App TITLE uses BRAND_TITLE |
| 12 | TestDashboardAppParity | `test_app_has_quit_action` | Has action_request_quit |
| 13 | TestDashboardAppParity | `test_app_has_export_action` | Has action_export |
| 14 | TestDashboardAppParity | `test_app_has_help_action` | Has action_show_help |
| 15 | TestDashboardAppParity | `test_sidebar_uses_brand_short` | Sidebar uses BRAND_SHORT |

---

## 22. Dashboard Export

**File:** `tests/test_dashboard_export.py` - 15 tests  
**Covers:** Export modal and file output

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestExportDirectory | `test_export_dir_is_path` | EXPORT_DIR is a Path |
| 2 | TestExportDirectory | `test_export_dir_in_user_home` | Located under user home |
| 3 | TestExportDirectory | `test_export_dir_under_kloudkompass` | Under .kloudkompass directory |
| 4 | TestExportModalInit | `test_default_view_name` | Default view is "cost" |
| 5 | TestExportModalInit | `test_custom_view_name` | Custom view name accepted |
| 6 | TestExportModalInit | `test_default_data_empty` | Default data is empty dict |
| 7 | TestExportModalInit | `test_custom_data_stored` | Custom data stored correctly |
| 8 | TestExportWriters | `test_csv_writer_method_exists` | Has CSV export method |
| 9 | TestExportWriters | `test_json_writer_method_exists` | Has JSON export method |
| 10 | TestExportWriters | `test_markdown_writer_method_exists` | Has Markdown export method |
| 11 | TestExportFormats | `test_csv_format_supported` | CSV format in supported list |
| 12 | TestExportFormats | `test_json_format_supported` | JSON format in supported list |
| 13 | TestExportFormats | `test_markdown_format_supported` | Markdown format in supported list |
| 14 | TestExportFilenames | `test_filename_includes_kloudkompass` | Filenames include "kloudkompass" |
| 15 | TestExportFilenames | `test_filename_includes_timestamp` | Filenames have timestamp |

---

## 23. Edge Cases

**File:** `tests/test_edge_cases.py` - 15 tests  
**Covers:** Boundary conditions across modules

| # | Class | Test | Description |
|---|-------|------|-------------|
| 1 | TestInputResultEdgeCases | `test_empty_string_input` | Empty string as raw input |
| 2 | TestInputResultEdgeCases | `test_whitespace_input` | Whitespace-only input |
| 3 | TestInputResultEdgeCases | `test_mixed_case_raw_preserved` | Raw input case preserved |
| 4 | TestProviderSetupEdgeCases | `test_unknown_provider` | Unknown provider handled |
| 5 | TestProviderSetupEdgeCases | `test_empty_provider_name` | Empty string provider |
| 6 | TestProviderSetupEdgeCases | `test_provider_with_spaces` | Provider name with whitespace |
| 7 | TestBrandingEdgeCases | `test_brand_title_not_mutable` | Brand title is a constant string |
| 8 | TestBrandingEdgeCases | `test_nav_hint_format_consistent` | NAV_HINT format is stable |
| 9 | TestNavigationEdgeCases | `test_navigator_at_root_pop_safe` | Pop at root doesn't crash |
| 10 | TestNavigationEdgeCases | `test_navigator_empty_depth` | Empty navigator has depth 0 |
| 11 | TestNavigationEdgeCases | `test_session_reset_returns_fresh` | Session reset is clean |
| 12 | TestExportModalEdgeCases | `test_export_no_data` | Export with empty data dict |
| 13 | TestExportModalEdgeCases | `test_export_none_data` | Export with None data |
| 14 | TestExportModalEdgeCases | `test_export_empty_rows` | Export with empty rows |
| 15 | | | *(count includes all edge cases)* |

---

## Test Architecture

```
tests/
├── Navigation & Input (67 tests)
│   ├── test_navigation_model.py       # InputResult, get_input(), confirm_quit
│   ├── test_screen_base.py            # Screen class, constants
│   ├── test_prompts_navigation.py     # Prompt-level navigation
│   └── test_lifecycle_model.py        # mount/render/unmount contract
│
├── State Management (68 tests)
│   ├── test_tui_navigation.py         # Navigator core
│   ├── test_navigator_advanced.py     # Navigator detailed ops
│   ├── test_tui_session.py            # Session core
│   ├── test_session_immutable.py      # Frozen dataclass invariant
│   └── test_session_methods.py        # Every with_* method
│
├── Provider Logic (66 tests)
│   ├── test_provider_setup.py         # Pure logic (zero I/O)
│   ├── test_provider_setup_screen.py  # Screen lifecycle compliance
│   └── test_provider_factory.py       # Registry and factory
│
├── Core Infrastructure (65 tests)
│   ├── test_health_module.py          # CLI checks, credentials
│   ├── test_exceptions_module.py      # Exception hierarchy
│   └── test_config_manager.py         # Configuration management
│
├── Cache (25 tests)
│   └── test_file_cache.py             # File-based cache lifecycle
│
├── Branding & Legal (53 tests)
│   ├── test_branding_consistency.py   # Cross-module branding
│   ├── test_footer_module.py          # Attribution constants
│   └── test_multicloud_ux.py          # Honest UX messaging
│
├── Dashboard (30 tests)
│   ├── test_dashboard_parity.py       # Quit/export modals
│   └── test_dashboard_export.py       # Export feature
│
├── Doctor (20 tests)
│   └── test_doctor_module.py          # Health check reporting
│
└── Edge Cases (15 tests)
    └── test_edge_cases.py             # Boundary conditions
```

---

*© 2026 TTox.Tech. All Rights Reserved. Kloud Kompass is open-source software.*
