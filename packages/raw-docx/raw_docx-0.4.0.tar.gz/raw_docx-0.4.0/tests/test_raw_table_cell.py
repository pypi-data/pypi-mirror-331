import pytest
from raw_table_cell import RawTableCell
from raw_paragraph import RawParagraph
from raw_list import RawList
from raw_table import RawTable
from raw_run import RawRun


@pytest.fixture
def list():
    return RawList()


@pytest.fixture
def table_cell():
    return RawTableCell(2, 3, True)


@pytest.fixture
def table_cell_not_first():
    return RawTableCell(2, 3, False)


@pytest.fixture
def paragraph():
    """Create a test paragraph"""
    return RawParagraph([RawRun("Test paragraph", "", None, "Normal")])


@pytest.fixture
def table():
    return RawTable()


def test_cell_initialization(table_cell):
    """Test cell initialization"""
    assert table_cell.h_span == 2
    assert table_cell.v_span == 3
    assert table_cell.first is True
    assert table_cell.h_merged is True
    assert table_cell.v_merged is True


def test_add_paragraph(table_cell, paragraph):
    """Test adding a paragraph to cell"""
    table_cell.add(paragraph)
    assert len(table_cell.items) == 1
    assert table_cell.items[0] == paragraph


def test_is_text(table_cell, paragraph):
    """Test adding a paragraph to cell is a text cell"""
    table_cell.add(paragraph)
    assert table_cell.is_text() is True


def test_is_not_text(table_cell, table):
    """Test cell is not text"""
    table_cell.add(table)
    assert table_cell.is_text() is False


def test_is_in_list_empty_cell(table_cell):
    """Test is_in_list with empty cell"""
    assert not table_cell.is_in_list()


def test_is_in_list_with_list(table_cell, list):
    """Test is_in_list with a list"""
    table_cell.add(list)
    assert table_cell.is_in_list()


def test_current_list_no_list(table_cell):
    """Test current_list with no list"""
    assert table_cell.current_list() is None


def test_current_list_with_list(table_cell, list):
    """Test current_list with existing list"""
    table_cell.add(list)
    assert table_cell.current_list() == list


def test_merged_cell_properties():
    """Test properties of merged cells"""
    cell1 = RawTableCell(2, 2, True)  # First cell in merge
    cell2 = RawTableCell(1, 1, False)  # Non-first cell in merge

    assert cell1.merged is True
    assert cell1.first is True
    assert cell2.merged is False
    assert cell2.first is False


def test_to_html(table_cell):
    assert table_cell.to_html() == '<td colspan="2">\n</td>'


def test_to_html_not_first(table_cell_not_first):
    assert table_cell_not_first.to_html() == ""
