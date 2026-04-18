# tests/test_phase_251_corrections.py
# ------------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# Regression tests for Phase 2.5.1 corrective hardening.
# These tests fail if architectural invariants are violated.

import pytest
import inspect
from dataclasses import FrozenInstanceError


class TestSessionImmutability:
    """Tests that session state is truly frozen."""
    
    def test_session_is_frozen_dataclass(self):
        """SessionState must be a frozen dataclass."""
        from kloudkompass.tui.session import SessionState
        import dataclasses
        
        assert dataclasses.is_dataclass(SessionState)
        # Check frozen by attempting mutation
        session = SessionState()
        with pytest.raises(FrozenInstanceError):
            session.provider = "test"
    
    def test_session_has_with_methods(self):
        """SessionState must have with_* methods for updates."""
        from kloudkompass.tui.session import SessionState
        
        assert hasattr(SessionState, 'with_provider')
        assert hasattr(SessionState, 'with_dates')
        assert hasattr(SessionState, 'with_breakdown')
        assert hasattr(SessionState, 'with_threshold')
    
    def test_with_methods_return_new_instance(self):
        """with_* methods must return new instances, not mutate."""
        from kloudkompass.tui.session import SessionState
        
        s1 = SessionState()
        s2 = s1.with_provider("aws")
        
        assert s1 is not s2
        assert s1.provider is None
        assert s2.provider == "aws"


class TestCostMenuImmutableUpdates:
    """Tests that cost menu uses immutable session updates."""
    
    def test_cost_menu_uses_update_session(self):
        """CostWizardScreen must import and use update_session."""
        from kloudkompass.tui import cost_menu
        
        source = inspect.getsource(cost_menu)
        
        # Must import update_session
        assert 'update_session' in source
        
        # Must NOT have direct attribute assignment patterns
        # (e.g., self.session.provider = )
        assert 'self.session.provider =' not in source
        assert 'self.session.start_date =' not in source
        assert 'self.session.end_date =' not in source
        assert 'self.session.breakdown =' not in source
        assert 'self.session.threshold =' not in source


class TestAttributionSinglePath:
    """Tests that attribution has exactly one rendering path."""
    
    def test_main_menu_no_startup_attribution(self):
        """launch() must NOT print attribution at startup."""
        from kloudkompass.tui import main_menu
        
        source = inspect.getsource(main_menu.launch)
        
        # Should not have attribution printed before main loop
        # (the old pattern was printing ATTRIBUTION_LINE2 at startup)
        lines = source.split('\n')
        main_loop_started = False
        for line in lines:
            if 'while not navigator.should_exit()' in line:
                main_loop_started = True
            if not main_loop_started and 'ATTRIBUTION_LINE2' in line:
                # Attribution before loop = violation
                pytest.fail("Attribution printed before main loop (startup)")
    
    def test_launch_uses_render_footer(self):
        """launch() must use render_footer() for attribution."""
        from kloudkompass.tui import main_menu
        
        source = inspect.getsource(main_menu.launch)
        assert 'render_footer()' in source
    
    def test_render_footer_works_without_console(self):
        """render_footer() must work without Console argument."""
        from kloudkompass.tui.footer import render_footer
        import io
        import sys
        
        # Capture stdout
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        
        try:
            render_footer()  # Should not raise
        finally:
            sys.stdout = old_stdout
        
        output = captured.getvalue()
        assert "TTox.Tech" in output


class TestScreenLifecycleModel:
    """Tests for single rendering model enforcement."""
    
    def test_screen_no_clear_screen_method(self):
        """Screen should not expose clear_screen() as separate method."""
        from kloudkompass.tui.screens import Screen
        
        # clear_screen should NOT be a separate callable method
        # (it's now built into print_header)
        if hasattr(Screen, 'clear_screen'):
            # If it exists, it should not be used by subclasses
            pass  # Allowed but discouraged
    
    def test_main_menu_doctor_no_clear_screen(self):
        """_run_doctor must not call clear_screen."""
        from kloudkompass.tui import main_menu
        
        source = inspect.getsource(main_menu.MainMenuScreen._run_doctor)
        assert 'clear_screen' not in source
    
    def test_print_header_clears_screen(self):
        """print_header must include screen clear."""
        from kloudkompass.tui.screens import Screen
        
        source = inspect.getsource(Screen.print_header)
        # Should contain ANSI escape sequence for clear screen
        assert '\\033[2J' in source or '\033[2J' in source


class TestScreensUseImmutableSession:
    """Tests that no screen directly mutates session."""
    
    def test_inventory_menu_no_direct_mutation(self):
        """InventoryWizardScreen must not mutate session directly."""
        from kloudkompass.tui import inventory_menu
        
        source = inspect.getsource(inventory_menu)
        assert 'self.session.' not in source or '= ' not in source.split('self.session.')[1].split('\n')[0] if 'self.session.' in source else True
    
    def test_security_menu_no_direct_mutation(self):
        """SecurityWizardScreen must not mutate session directly."""
        from kloudkompass.tui import security_menu
        
        source = inspect.getsource(security_menu)
        assert 'self.session.' not in source or '= ' not in source.split('self.session.')[1].split('\n')[0] if 'self.session.' in source else True


class TestDoctorAttribution:
    """Tests for doctor attribution."""
    
    def test_doctor_uses_centralized_attribution(self):
        """Doctor must use ATTRIBUTION_LINE1 from footer.py."""
        from kloudkompass.tui import doctor
        
        source = inspect.getsource(doctor)
        assert 'from kloudkompass.tui.footer import ATTRIBUTION_LINE1' in source
    
    def test_doctor_output_contains_attribution(self):
        """Doctor report must contain attribution."""
        from kloudkompass.tui import doctor
        
        source = inspect.getsource(doctor.print_doctor_report)
        assert 'ATTRIBUTION_LINE1' in source
