import pytest
from unittest.mock import patch
from raw_list import RawList
from raw_list_item import RawListItem
from raw_run import RawRun


@pytest.fixture
def raw_list():
    return RawList()


@pytest.fixture
def list_item():
    run = RawRun("Test paragraph", "", None, "Normal")
    return RawListItem([run], 1)


def test_list_initialization(raw_list):
    """Test list initialization"""
    assert raw_list.items == []


def test_add_item(list_item):
    """Test adding an item to the list"""
    list = RawList(1)
    list.add(list_item)
    assert len(list.items) == 1
    assert list.items[0] == list_item


def test_to_text():
    """Test to text"""
    list = RawList(1)
    items = [
        RawListItem([RawRun("Item 1", "", None, "Normal")], 1),
        RawListItem([RawRun("Item 1.1", "", None, "Normal")], 2),
        RawListItem([RawRun("Item 2", "", None, "Normal")], 1),
    ]
    for item in items:
        list.add(item)
    assert item.to_text() == "  Item 2"


def test_add_multiple_items():
    """Test adding multiple items with different levels"""
    list = RawList(1)
    items = [
        RawListItem([RawRun("Item 1", "", None, "Normal")], 1),
        RawListItem([RawRun("Item 1.1", "", None, "Normal")], 2),
        RawListItem([RawRun("Item 2", "", None, "Normal")], 1),
    ]
    for item in items:
        list.add(item)
    assert len(list.items) == 3
    assert [item.level for item in list.items] == [1, 2, 1]


def test_add_multiple_items_level_error():
    """Test adding multiple items with different levels with level error"""
    with patch("raw_list.logger") as mock_logger:
        list = RawList(1)
        items = [
            RawListItem([RawRun("Item 1", "", None, "Normal")], 1),
            RawListItem([RawRun("Item 1.1.1", "", None, "Normal")], 3),
            RawListItem([RawRun("Item 2", "", None, "Normal")], 1),
        ]
        for item in items:
            list.add(item)
        assert len(list.items) == 3
        assert [item.level for item in list.items] == [1, 3, 1]
        mock_logger.warning.assert_called_once()
        error_msg = mock_logger.warning.call_args[0][0]
        assert "Adding list item" in error_msg
        assert "to item but level jump greater than 1" in error_msg


def test_to_html(raw_list):
    """Test converting list to HTML format"""
    items = [
        RawListItem([RawRun("Item 1", "", None, "Normal")], 0),
        RawListItem([RawRun("Item 2", "", None, "Normal")], 0),
    ]
    for item in items:
        raw_list.add(item)

    expected_html = "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>"
    assert raw_list.to_html() == expected_html


def test_nested_list_to_html():
    """Test converting nested list to HTML format"""
    root_list = RawList(0)
    items = [
        RawListItem([RawRun("Item 1", "", None, "Normal")], 1),
        RawListItem([RawRun("Subitem 1.1", "", None, "Normal")], 2),
        RawListItem([RawRun("Item 2", "", None, "Normal")], 1),
    ]
    for item in items:
        root_list.add(item)

    expected_html = "<ul>\n<li><ul>\n<li>Item 1</li>\n<li><ul>\n<li>Subitem 1.1</li>\n</ul></li>\n<li>Item 2</li>\n</ul></li>\n</ul>"
    assert root_list.to_html() == expected_html


def test_add_item_lower_level_logs_error():
    """Test that adding an item with lower level than list level logs an error"""
    with patch("raw_list.logger") as mock_logger:
        list_obj = RawList(2)  # List with level 2
        item = RawListItem(
            [RawRun("Test Item", "", None, "Normal")], 1
        )  # Item with lower level 1
        list_obj.add(item)

        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Failed to add list item" in error_msg
        assert "levels are in error" in error_msg


def test_to_dict():
    """Test converting list to dictionary"""
    list_obj = RawList(1)
    item1 = RawListItem([RawRun("Item 1", "", None, "Normal")], 1)
    item2 = RawListItem([RawRun("Item 2", "", None, "Normal")], 1)
    sublist = RawList(2)
    sublist.add(RawListItem([RawRun("Subitem 1", "", None, "Normal")], 2))

    list_obj.add(item1)
    list_obj.add(sublist)
    list_obj.add(item2)

    result = list_obj.to_dict()
    assert result["type"] == "list"
    assert result["level"] == 1
    assert len(result["items"]) == 3

    # Check first item
    assert result["items"][0]["type"] == "list_item"
    assert result["items"][0]["text"] == "Item 1"

    # Check nested list
    assert result["items"][1]["type"] == "list"
    assert result["items"][1]["level"] == 2
    assert len(result["items"][1]["items"]) == 1
    assert result["items"][1]["items"][0]["items"][0]["text"] == "Subitem 1"

    # Check last item
    assert result["items"][2]["type"] == "list_item"
    assert result["items"][2]["text"] == "Item 2"


def test_all_items():
    list_obj = RawList(1)
    item1 = RawListItem([RawRun("Item 1", "", None, "Normal")], 1)
    item2 = RawListItem([RawRun("Item 2", "", None, "Normal")], 1)
    sublist = RawList(2)
    item3 = RawListItem([RawRun("Subitem 1", "", None, "Normal")], 2)
    sublist.add(item3)
    list_obj.add(item1)
    list_obj.add(sublist)
    list_obj.add(item2)
    result = list_obj.all_items()
    assert result == [item1, item3, item2]
