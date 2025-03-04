import pytest
from src.raw_docx.raw_list_item import RawListItem
from src.raw_docx.raw_run import RawRun


@pytest.fixture
def list_item():
    run = RawRun("Test item", "", None, "Normal")
    return RawListItem([run], 2)


def test_list_item_initialization(list_item):
    """Test list item initialization"""
    assert list_item.text == "Test item"
    assert list_item.level == 2


def test_list_item_with_empty_text():
    """Test list item with empty text"""
    item = RawListItem("", 1)
    assert item.text == ""
    assert item.level == 1


def test_list_item_with_different_levels():
    """Test list items with different levels"""
    levels = [1, 2, 3]
    items = [
        RawListItem([RawRun("Test item", "", None, "Normal")], level)
        for level in levels
    ]
    assert [item.level for item in items] == levels


def test_to_text(list_item):
    """Test to text"""
    assert list_item.to_text() == "    Test item"
