# tests/test_cli_tag_filtering.py
# --------------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# CLI --tag argument parsing and multi-tag handling.

import pytest
from unittest.mock import patch


class TestTagParsing:
    """Test parsing of --tag arguments from CLI."""

    def test_parse_single_tag(self):
        """Parse 'env=prod' into dict."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(["env=prod"])
        assert result == {"env": "prod"}

    def test_parse_multiple_tags(self):
        """Parse multiple key=value pairs."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(["env=prod", "team=ops"])
        assert result == {"env": "prod", "team": "ops"}

    def test_parse_tag_no_value(self):
        """Tag with key only (no =) should use empty string value."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(["env"])
        assert result == {"env": ""}

    def test_parse_empty_tags(self):
        """Empty tag list returns empty dict."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags([])
        assert result == {}

    def test_parse_none_tags(self):
        """None tags returns empty dict."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(None)
        assert result == {}

    def test_parse_tag_with_equals_in_value(self):
        """Tag value can contain = character."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(["config=key=value"])
        assert result["config"] == "key=value"

    def test_parse_tag_whitespace_stripped(self):
        """Whitespace around key/value should be stripped."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(["  env = prod  "])
        assert "env" in result

    def test_parse_tag_case_preserved(self):
        """Tag keys and values preserve original case."""
        from kloudkompass.utils.parsers import parse_tags
        result = parse_tags(["Environment=Production"])
        assert result["Environment"] == "Production"
