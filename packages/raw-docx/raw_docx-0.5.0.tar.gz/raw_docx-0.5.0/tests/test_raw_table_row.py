import pytest
from src.raw_docx.raw_table_row import RawTableRow
from src.raw_docx.raw_table_cell import RawTableCell
from src.raw_docx.raw_paragraph import RawParagraph
from src.raw_docx.raw_run import RawRun


@pytest.fixture
def table_row():
    return RawTableRow()


@pytest.fixture
def table_cell():
    return RawTableCell(1, 1, True)


def test_row_initialization(table_row):
    """Test row initialization"""
    assert table_row.cells == []


def test_add_cell(table_row, table_cell):
    """Test adding a cell to the row"""
    table_row.add(table_cell)
    assert len(table_row.cells) == 1
    assert table_row.cells[0] == table_cell


def test_add_multiple_cells(table_row):
    """Test adding multiple cells"""
    cells = [
        RawTableCell(1, 1, True),
        RawTableCell(2, 1, True),
        RawTableCell(1, 2, False),
    ]
    for cell in cells:
        table_row.add(cell)

    assert len(table_row.cells) == 3


def test_find_cell(table_row):
    """Test finding a cell by text content"""
    cell1 = RawTableCell(1, 1, True)
    cell1.add(RawParagraph([RawRun("Test Content", "", "", "Normal")]))
    cell2 = RawTableCell(1, 1, True)
    cell2.add(RawParagraph([RawRun("Other Content", "", "", "Normal")]))

    table_row.add(cell1)
    table_row.add(cell2)

    # Test finding existing cell
    found = table_row.find_cell("Test")
    assert found == cell1

    # Test case insensitivity
    found = table_row.find_cell("TEST")
    assert found == cell1

    # Test non-existent text
    found = table_row.find_cell("NonExistent")
    assert found is None


def test_find_cell_next_to(table_row):
    """Test finding a cell next to specific text"""
    cell1 = RawTableCell(1, 1, True)
    cell1.add(RawParagraph([RawRun("Test Content", "", "", "Normal")]))
    cell2 = RawTableCell(1, 1, True)
    cell2.add(RawParagraph([RawRun("Target Cell", "", "", "Normal")]))
    cell3 = RawTableCell(1, 1, True)
    cell3.add(RawParagraph([RawRun("Other Content", "", "", "Normal")]))

    table_row.add(cell1)
    table_row.add(cell2)
    table_row.add(cell3)

    # Test finding cell next to existing text
    found = table_row.find_cell_next_to("Test")
    assert found == cell2

    # Test case insensitivity
    found = table_row.find_cell_next_to("TEST")
    assert found == cell2

    # Test when no next cell exists
    found = table_row.find_cell_next_to("Other")
    assert found is None

    # Test with non-existent text
    found = table_row.find_cell_next_to("NonExistent")
    assert found is None


def test_to_html(table_row):
    """Test converting row to HTML"""
    cell1 = RawTableCell(1, 1, True)
    cell1.add(RawParagraph([RawRun("Cell 1", "", "", "Normal")]))
    cell2 = RawTableCell(1, 1, True)
    cell2.add(RawParagraph([RawRun("Cell 2", "", "", "Normal")]))

    table_row.add(cell1)
    table_row.add(cell2)

    html = table_row.to_html()
    assert html.startswith("<tr>")
    assert html.endswith("</tr>")
    assert "Cell 1" in html
    assert "Cell 2" in html


def test_next_cell(table_row):
    """Test getting next cell from index"""
    cell1 = RawTableCell(1, 1, True)
    cell2 = RawTableCell(1, 1, False)  # not first
    cell3 = RawTableCell(1, 1, True)

    table_row.add(cell1)
    table_row.add(cell2)
    table_row.add(cell3)

    # Test finding next first cell
    next_cell = table_row.next_cell(0)
    assert next_cell == cell3

    # Test when no next first cell exists
    next_cell = table_row.next_cell(2)
    assert next_cell is None

    # Test from middle of row
    next_cell = table_row.next_cell(1)
    assert next_cell == cell3
