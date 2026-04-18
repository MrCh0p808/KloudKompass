# tests/test_aws_networking.py
# ----------------------------
# © 2026 TTox.Tech. Licensed under MIT.
# Kloud Kompass is open-source software.
#
# AWS networking provider tests — VPCs, subnets, SGs with tags and edge cases.

import pytest
from kloudkompass.core.networking_base import VPCRecord, SubnetRecord, SecurityGroupRecord


def _make_vpc(**overrides) -> VPCRecord:
    defaults = dict(
        vpc_id="vpc-test1",
        name="test-vpc",
        cidr_block="10.0.0.0/16",
        state="available",
        region="us-east-1",
        is_default=False,
        tags={"Name": "test-vpc"},
    )
    defaults.update(overrides)
    return VPCRecord(**defaults)


def _make_subnet(**overrides) -> SubnetRecord:
    defaults = dict(
        subnet_id="subnet-test1",
        name="test-subnet",
        vpc_id="vpc-test1",
        cidr_block="10.0.1.0/24",
        availability_zone="us-east-1a",
        available_ips=250,
        is_public=False,
        tags={"Name": "test-subnet"},
    )
    defaults.update(overrides)
    return SubnetRecord(**defaults)


def _make_sg(**overrides) -> SecurityGroupRecord:
    defaults = dict(
        group_id="sg-test1",
        name="test-sg",
        description="Test SG",
        vpc_id="vpc-test1",
        inbound_rules=[],
        outbound_rules=[],
        tags={"Name": "test-sg"},
    )
    defaults.update(overrides)
    return SecurityGroupRecord(**defaults)


class TestVPCRecord:
    def test_create_vpc(self):
        vpc = _make_vpc()
        assert vpc.vpc_id == "vpc-test1"
        assert vpc.cidr_block == "10.0.0.0/16"

    def test_vpc_is_default(self):
        vpc = _make_vpc(is_default=True)
        assert vpc.is_default is True

    def test_vpc_tags_access(self):
        vpc = _make_vpc(tags={"env": "prod", "Name": "prod-vpc"})
        assert vpc.tags["env"] == "prod"

    def test_vpc_default_not_default(self):
        vpc = _make_vpc()
        assert vpc.is_default is False

    def test_vpc_to_dict(self):
        vpc = _make_vpc()
        d = vpc.to_dict()
        assert "vpc_id" in d
        assert d["state"] == "available"


class TestSubnetRecord:
    def test_create_subnet(self):
        sub = _make_subnet()
        assert sub.subnet_id == "subnet-test1"
        assert sub.available_ips == 250

    def test_subnet_is_public(self):
        sub = _make_subnet(is_public=True)
        assert sub.is_public is True

    def test_subnet_belongs_to_vpc(self):
        sub = _make_subnet(vpc_id="vpc-abc")
        assert sub.vpc_id == "vpc-abc"

    def test_subnet_az(self):
        sub = _make_subnet(availability_zone="eu-west-1b")
        assert sub.availability_zone == "eu-west-1b"


class TestSecurityGroupRecord:
    def test_create_sg(self):
        sg = _make_sg()
        assert sg.group_id == "sg-test1"
        assert sg.description == "Test SG"

    def test_sg_empty_rules(self):
        sg = _make_sg()
        assert len(sg.inbound_rules) == 0
        assert len(sg.outbound_rules) == 0

    def test_sg_with_inbound_rules(self):
        rule = {"protocol": "tcp", "port_range": "443", "source": "0.0.0.0/0", "description": "HTTPS"}
        sg = _make_sg(inbound_rules=[rule])
        assert len(sg.inbound_rules) == 1
        assert sg.inbound_rules[0]["port_range"] == "443"

    def test_sg_with_outbound_rules(self):
        rule = {"protocol": "-1", "port_range": "All", "source": "0.0.0.0/0"}
        sg = _make_sg(outbound_rules=[rule])
        assert len(sg.outbound_rules) == 1

    def test_sg_belongs_to_vpc(self):
        sg = _make_sg(vpc_id="vpc-xyz")
        assert sg.vpc_id == "vpc-xyz"

    def test_sg_tags_access(self):
        sg = _make_sg(tags={"env": "staging"})
        assert sg.tags["env"] == "staging"

    def test_sg_to_dict(self):
        sg = _make_sg()
        d = sg.to_dict()
        assert "group_id" in d
        assert "inbound_rules" in d

    def test_sg_multiple_inbound_rules(self):
        rules = [
            {"protocol": "tcp", "port_range": "80", "source": "0.0.0.0/0"},
            {"protocol": "tcp", "port_range": "443", "source": "0.0.0.0/0"},
            {"protocol": "tcp", "port_range": "22", "source": "10.0.0.0/8"},
        ]
        sg = _make_sg(inbound_rules=rules)
        assert len(sg.inbound_rules) == 3
