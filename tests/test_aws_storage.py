# tests/test_aws_storage.py
# -------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# AWS storage provider tests — buckets, volumes, unattached detection.

import pytest
from kloudkompass.core.storage_base import BucketRecord, VolumeRecord


def _make_bucket(**overrides) -> BucketRecord:
    defaults = dict(
        bucket_name="test-bucket-2025",
        creation_date="2025-01-15T00:00:00Z",
        region="us-east-1",
        tags={"Name": "test-bucket"},
    )
    defaults.update(overrides)
    return BucketRecord(**defaults)


def _make_volume(**overrides) -> VolumeRecord:
    defaults = dict(
        volume_id="vol-test123",
        name="test-volume",
        size_gb=50,
        volume_type="gp3",
        state="in-use",
        attached_to="i-abc123",
        region="us-east-1",
        encrypted=True,
        tags={"Name": "test-volume"},
    )
    defaults.update(overrides)
    return VolumeRecord(**defaults)


class TestBucketRecord:
    def test_create_bucket(self):
        b = _make_bucket()
        assert b.bucket_name == "test-bucket-2025"

    def test_bucket_creation_date(self):
        b = _make_bucket(creation_date="2024-06-01T12:00:00Z")
        assert "2024" in b.creation_date

    def test_bucket_tags(self):
        b = _make_bucket(tags={"env": "prod"})
        assert b.tags["env"] == "prod"


class TestVolumeRecord:
    def test_create_volume(self):
        v = _make_volume()
        assert v.volume_id == "vol-test123"
        assert v.size_gb == 50

    def test_volume_type(self):
        v = _make_volume(volume_type="io2")
        assert v.volume_type == "io2"

    def test_volume_encrypted(self):
        v = _make_volume(encrypted=True)
        assert v.encrypted is True

    def test_volume_not_encrypted(self):
        v = _make_volume(encrypted=False)
        assert v.encrypted is False

    def test_volume_attached(self):
        v = _make_volume(attached_to="i-abc123")
        assert v.attached_to == "i-abc123"

    def test_volume_unattached(self):
        v = _make_volume(attached_to="", state="available")
        assert v.attached_to == ""
        assert v.state == "available"


class TestUnattachedDetection:
    """Test the unattached volume detection logic."""

    def _get_provider(self):
        from kloudkompass.aws.storage import AWSStorageProvider
        return AWSStorageProvider()

    def test_find_unattached_volumes(self):
        p = self._get_provider()
        volumes = [
            _make_volume(volume_id="vol-1", state="in-use", attached_to="i-1"),
            _make_volume(volume_id="vol-2", state="available", attached_to=""),
            _make_volume(volume_id="vol-3", state="available", attached_to=""),
        ]
        unattached = p.find_unattached_volumes(volumes)
        assert len(unattached) == 2
        assert all(v.state == "available" for v in unattached)

    def test_no_unattached_volumes(self):
        p = self._get_provider()
        volumes = [
            _make_volume(volume_id="vol-1", state="in-use", attached_to="i-1"),
        ]
        unattached = p.find_unattached_volumes(volumes)
        assert len(unattached) == 0

    def test_all_unattached(self):
        p = self._get_provider()
        volumes = [
            _make_volume(volume_id="vol-1", state="available", attached_to=""),
        ]
        unattached = p.find_unattached_volumes(volumes)
        assert len(unattached) == 1

    def test_empty_list(self):
        p = self._get_provider()
        unattached = p.find_unattached_volumes([])
        assert unattached == []
