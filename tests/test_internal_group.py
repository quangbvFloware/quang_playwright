"""
Test InternalGroup enum
"""
from framework.consts.consts_common import InternalGroup
from framework.utils.logging_util import logger


def test_internal_group_values():
    """Test that InternalGroup has correct values"""
    assert InternalGroup.WEB.id == 1
    assert InternalGroup.MAC.id == 2
    assert InternalGroup.IPHONE.id == 3
    assert InternalGroup.IPAD.id == 4
    assert InternalGroup.QA.id == 5
    assert InternalGroup.AUTO.id == 6


def test_internal_group_prefixes():
    """Test that InternalGroup has correct prefixes"""
    assert InternalGroup.WEB.prefix == "web763e90"
    assert InternalGroup.MAC.prefix == "mac763e90"
    assert InternalGroup.IPHONE.prefix == "ios763e90"
    assert InternalGroup.IPAD.prefix == "ipad763e90"
    assert InternalGroup.QA.prefix == "qa763e90"
    assert InternalGroup.AUTO.prefix == "auto763e90"


def test_internal_group_value_returns_tuple():
    """Test that .value returns the tuple (for backward compatibility if needed)"""
    assert InternalGroup.WEB.value == (1, "web763e90")
    assert InternalGroup.AUTO.value == (6, "auto763e90")


def test_internal_group_access_patterns():
    """Test different ways to access group info"""
    group = InternalGroup.WEB
    
    # Access via properties
    assert group.id == 1
    assert group.prefix == "web763e90"
    
    # Access via value tuple
    group_id, group_prefix = group.value
    assert group_id == 1
    assert group_prefix == "web763e90"
    
    logger.debug(f"✓ {group.name}: id={group.id}, prefix={group.prefix}")


def test_internal_group_iteration():
    """Test iterating over all groups"""
    groups = list(InternalGroup)
    assert len(groups) == 6
    
    # All should have id and prefix
    for group in groups:
        assert isinstance(group.id, int)
        assert isinstance(group.prefix, str)
        assert group.prefix.endswith("763e90")
        logger.debug(f"  {group.name}: id={group.id}, prefix={group.prefix}")


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v', '-s'])
