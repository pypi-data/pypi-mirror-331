import pytest
from src.raw_docx.raw_table import RawTable
from src.raw_docx.raw_table_row import RawTableRow
from src.raw_docx.raw_table_cell import RawTableCell
from src.raw_docx.raw_paragraph import RawParagraph
from src.raw_docx.raw_run import RawRun


@pytest.fixture
def table():
    return RawTable()


@pytest.fixture
def table_row():
    return RawTableRow()


def test_table_initialization(table):
    """Test table initialization"""
    assert table.rows == []


def test_add_row(table, table_row):
    """Test adding a row to the table"""
    table.add(table_row)
    assert len(table.rows) == 1
    assert table.rows[0] == table_row


def test_add_multiple_rows(table):
    """Test adding multiple rows"""
    rows = [RawTableRow(), RawTableRow(), RawTableRow()]
    for row in rows:
        table.add(row)
    assert len(table.rows) == 3


def test_to_dict():
    """Test converting table to dictionary"""
    table = RawTable()
    row = RawTableRow()
    cell = RawTableCell(1, 1, True)
    cell.add(RawParagraph([RawRun("Test content", "", "", "Normal")]))
    row.add(cell)
    table.add(row)

    result = table.to_dict()
    assert result["type"] == "table"
    assert len(result["rows"]) == 1

    # Check row
    row_dict = result["rows"][0]
    assert row_dict["type"] == "table_row"
    assert len(row_dict["cells"]) == 1

    # Check cell
    cell_dict = row_dict["cells"][0]
    assert cell_dict["type"] == "table_cell"
    assert cell_dict["row_span"] == 1
    assert cell_dict["col_span"] == 1
    assert cell_dict["first"] is True

    # Check cell content
    assert len(cell_dict["content"]) == 1
    content = cell_dict["content"][0]
    assert content["type"] == "paragraph"
    assert content["text"] == "Test content"


def test_row_access(table):
    """Test accessing rows by index"""
    row1 = RawTableRow()
    row2 = RawTableRow()
    table.add(row1)
    table.add(row2)

    assert table.row(0) == row1
    assert table.row(1) == row2
    assert table.row(2) is None


def test_next_row(table):
    """Test getting next row"""
    row1 = RawTableRow()
    row2 = RawTableRow()
    table.add(row1)
    table.add(row2)

    next_row, next_index = table.next(0)
    assert next_row == row2
    assert next_index == 1

    # Test getting next row at end of table
    next_row, next_index = table.next(1)
    assert next_row is None
    assert next_index == -1


def test_find_row(table):
    """Test finding row by text content"""
    row1 = RawTableRow()
    cell1 = RawTableCell(1, 1, True)
    cell1.add(RawParagraph([RawRun("Test Content", "", "", "Normal")]))
    row1.add(cell1)

    row2 = RawTableRow()
    cell2 = RawTableCell(1, 1, True)
    cell2.add(RawParagraph([RawRun("Other Content", "", "", "Normal")]))
    row2.add(cell2)

    table.add(row1)
    table.add(row2)

    # Test finding existing row
    found_row, found_index = table.find_row("Test")
    assert found_row == row1
    assert found_index == 0

    # Test case insensitivity
    found_row, found_index = table.find_row("TEST")
    assert found_row == row1
    assert found_index == 0

    # Test non-existent text
    found_row, found_index = table.find_row("NonExistent")
    assert found_row is None
    assert found_index == -1


def test_table_classes(table):
    """Test table class management"""
    # Check default class
    assert table.klasses == ["ich-m11-table"]

    # Test adding class
    table.add_class("new-class")
    assert "new-class" in table.klasses

    # Test replacing class
    table.replace_class("ich-m11-table", "replacement-class")
    assert "ich-m11-table" not in table.klasses
    assert "replacement-class" in table.klasses

    # Test HTML output with classes
    row = RawTableRow()
    cell = RawTableCell(1, 1, True)
    cell.add(RawParagraph([RawRun("Test", "", "", "Normal")]))
    row.add(cell)
    table.add(row)

    html = table.to_html()
    assert 'class="new-class replacement-class"' in html
    assert "<table" in html
    assert "</table>" in html
