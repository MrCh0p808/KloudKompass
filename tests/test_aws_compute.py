# tests/test_aws_compute.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# AWS compute provider tests — filters, tags, edge cases.

import pytest
from unittest.mock import patch, MagicMock
from kloudkompass.core.compute_base import ComputeInstance


def _make_instance(**overrides) -> ComputeInstance:
    """Factory for test ComputeInstance."""
    defaults = dict(
        instance_id="i-test123",
        name="test-server",
        instance_type="t3.micro",
        state="running",
        region="us-east-1a",
        public_ip="1.2.3.4",
        private_ip="10.0.0.5",
        launch_time="2025-01-01T00:00:00Z",
        platform="Linux/UNIX",
        vpc_id="vpc-abc123",
        tags={"Name": "test-server", "env": "prod"},
    )
    defaults.update(overrides)
    return ComputeInstance(**defaults)


class TestComputeInstanceDataclass:
    """Tests for the ComputeInstance data model."""

    def test_create_instance(self):
        inst = _make_instance()
        assert inst.instance_id == "i-test123"
        assert inst.name == "test-server"

    def test_to_dict_returns_all_fields(self):
        inst = _make_instance()
        d = inst.to_dict()
        assert "instance_id" in d
        assert "tags" in d
        assert d["state"] == "running"

    def test_default_empty_fields(self):
        inst = ComputeInstance(instance_id="i-1", name="x", instance_type="t2.nano", state="running", region="us-east-1")
        assert inst.public_ip == ""
        assert inst.private_ip == ""
        assert inst.tags == {}

    def test_tags_are_dict(self):
        inst = _make_instance()
        assert isinstance(inst.tags, dict)
        assert inst.tags["env"] == "prod"


class TestFilterByState:
    """Tests for ComputeProvider.filter_by_state (concrete method)."""

    def _get_provider(self):
        """Get a real provider instance (only uses non-abstract methods)."""
        from kloudkompass.aws.compute import AWSComputeProvider
        return AWSComputeProvider()

    def test_filter_running(self):
        p = self._get_provider()
        instances = [
            _make_instance(instance_id="i-1", state="running"),
            _make_instance(instance_id="i-2", state="stopped"),
            _make_instance(instance_id="i-3", state="running"),
        ]
        result = p.filter_by_state(instances, "running")
        assert len(result) == 2
        assert all(i.state == "running" for i in result)

    def test_filter_stopped(self):
        p = self._get_provider()
        instances = [
            _make_instance(instance_id="i-1", state="running"),
            _make_instance(instance_id="i-2", state="stopped"),
        ]
        result = p.filter_by_state(instances, "stopped")
        assert len(result) == 1
        assert result[0].instance_id == "i-2"

    def test_filter_returns_empty_for_no_match(self):
        p = self._get_provider()
        instances = [_make_instance(state="running")]
        result = p.filter_by_state(instances, "terminated")
        assert len(result) == 0

    def test_filter_case_insensitive(self):
        p = self._get_provider()
        instances = [_make_instance(state="Running")]
        result = p.filter_by_state(instances, "running")
        assert len(result) == 1


class TestFilterByTag:
    """Tests for ComputeProvider.filter_by_tag (concrete method)."""

    def _get_provider(self):
        from kloudkompass.aws.compute import AWSComputeProvider
        return AWSComputeProvider()

    def test_filter_by_tag_key_only(self):
        p = self._get_provider()
        instances = [
            _make_instance(instance_id="i-1", tags={"env": "prod"}),
            _make_instance(instance_id="i-2", tags={"team": "ops"}),
        ]
        result = p.filter_by_tag(instances, "env")
        assert len(result) == 1
        assert result[0].instance_id == "i-1"

    def test_filter_by_tag_key_value(self):
        p = self._get_provider()
        instances = [
            _make_instance(instance_id="i-1", tags={"env": "prod"}),
            _make_instance(instance_id="i-2", tags={"env": "dev"}),
        ]
        result = p.filter_by_tag(instances, "env", "prod")
        assert len(result) == 1
        assert result[0].instance_id == "i-1"

    def test_filter_no_match(self):
        p = self._get_provider()
        instances = [_make_instance(tags={"team": "data"})]
        result = p.filter_by_tag(instances, "env")
        assert len(result) == 0

    def test_filter_empty_instances(self):
        p = self._get_provider()
        result = p.filter_by_tag([], "env")
        assert result == []
