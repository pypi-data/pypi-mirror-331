import pytest
from raw_section import RawSection
from raw_paragraph import RawParagraph
from raw_list import RawList
from raw_image import RawImage
from raw_table import RawTable
from raw_table_row import RawTableRow
from raw_table_cell import RawTableCell
from raw_list_item import RawListItem
from raw_run import RawRun


@pytest.fixture
def section():
    return RawSection("Test Section", "Test Content", 1)


@pytest.fixture
def paragraph():
    run = RawRun("Test paragraph", "", "", "Normal")
    return RawParagraph([run])


@pytest.fixture
def image(tmp_path):
    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(b"dummy image content")
    return RawImage(str(image_path))


def test_section_initialization(section):
    """Test section initialization"""
    assert section.title == "Test Section"
    assert section.number == "Test Content"
    assert section.level == 1
    assert section.items == []


def test_section_initialization_strip(section):
    """Test section initialization"""
    section = RawSection(" Test Section    ", "     Test Content ", 1)
    assert section.title == "Test Section"
    assert section.number == "Test Content"
    assert section.level == 1
    assert section.items == []


def test_add_paragraph(section, paragraph):
    """Test adding a paragraph to section"""
    section.add(paragraph)
    assert len(section.items) == 1
    assert section.items[0] == paragraph


def test_add_image(section, image):
    """Test adding an image to section"""
    section.add(image)
    assert len(section.items) == 1
    assert section.items[0] == image


def test_is_in_list_empty_section(section):
    """Test is_in_list with empty section"""
    assert not section.is_in_list()


def test_is_in_list_with_list(section):
    """Test is_in_list with a list"""
    section.add(RawList())
    assert section.is_in_list()


def test_current_list_no_list(section):
    """Test current_list with no list"""
    assert section.current_list() is None


def test_current_list_with_list(section):
    """Test current_list with existing list"""
    test_list = RawList()
    section.add(test_list)
    assert section.current_list() == test_list


def test_to_html(section, paragraph):
    """Test converting section to HTML"""
    section.add(paragraph)
    result = section.to_html()
    assert "<p>Test paragraph</p>" in result


def test_to_html_between(section):
    """Test converting section to HTML between indices"""
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    run3 = RawRun("Third", "", "", "Normal")

    section.add(RawParagraph([run1]))
    section.add(RawParagraph([run2]))
    section.add(RawParagraph([run3]))
    result = section.to_html_between(1, 2)
    assert "<p>Second</p>" in result
    assert "<p>First</p>" not in result
    assert "<p>Third</p>" not in result


def test_paragraphs(section):
    """Test getting all paragraphs"""
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")

    p1 = RawParagraph([run1])
    p2 = RawParagraph([run2])

    section.add(p1)
    section.add(RawList())  # Add non-paragraph item
    section.add(p2)

    paragraphs = section.paragraphs()
    assert len(paragraphs) == 2
    assert all(isinstance(p, RawParagraph) for p in paragraphs)


def test_tables(section):
    """Test getting all tables"""
    run = RawRun("Test", "", "", "Normal")
    table = RawTable()
    section.add(RawParagraph([run]))
    section.add(table)
    tables = section.tables()
    assert len(tables) == 1
    assert all(isinstance(t, RawTable) for t in tables)


def test_lists(section):
    """Test getting all lists"""
    run = RawRun("Test", "", "", "Normal")
    list1 = RawList()
    section.add(RawParagraph([run]))
    section.add(list1)
    lists = section.lists()
    assert len(lists) == 1
    assert all(isinstance(list, RawList) for list in lists)


def test_items_between(section):
    """Test getting items between indices"""
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    run3 = RawRun("Third", "", "", "Normal")

    section.add(RawParagraph([run1]))
    section.add(RawParagraph([run2]))
    section.add(RawParagraph([run3]))
    items = section.items_between(1, 2)
    assert len(items) == 1
    assert items[0].text == "Second"


def test_find(section):
    """Test finding paragraphs containing text"""
    run1 = RawRun("First test", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    run3 = RawRun("Third test", "", "", "Normal")

    section.add(RawParagraph([run1]))
    section.add(RawParagraph([run2]))
    section.add(RawParagraph([run3]))
    found = section.find("test")
    assert len(found) == 2
    assert all("test" in p.text for p in found)


def test_find_at_start(section):
    """Test finding paragraphs starting with text"""
    run1 = RawRun("Test first", "", "", "Normal")
    run2 = RawRun("Second test", "", "", "Normal")
    run3 = RawRun("Test third", "", "", "Normal")

    section.add(RawParagraph([run1]))
    section.add(RawParagraph([run2]))
    section.add(RawParagraph([run3]))
    found = section.find_at_start("Test")
    assert len(found) == 2
    assert all(p.text.startswith("Test") for p in found)


def test_find_first_at_start(section):
    """Test finding first paragraph starting with text"""
    run1 = RawRun("Test first", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    run3 = RawRun("Test third", "", "", "Normal")

    section.add(RawParagraph([run1]))
    section.add(RawParagraph([run2]))
    section.add(RawParagraph([run3]))
    found, index = section.find_first_at_start("Test")
    assert found.text == "Test first"
    assert index == 0


def test_find_first_at_start_not_found(section):
    """Test finding first paragraph starting with non-existent text"""
    run1 = RawRun("Test", "", "", "Normal")
    section.add(RawParagraph([run1]))
    found, index = section.find_first_at_start("XXX")
    assert found is None
    assert index == -1


def test_has_lists(section):
    """Test checking if section has lists"""
    assert not section.has_lists()
    section.add(RawList())
    assert section.has_lists()


def test_has_content_and_is_empty(section):
    """Test checking if section has content"""
    assert section.is_empty()
    assert not section.has_content()
    run = RawRun("Test content", "", "", "Normal")
    section.add(RawParagraph([run]))
    assert not section.is_empty()
    assert section.has_content()


def test_next(section):
    """Test getting next item"""
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    run3 = RawRun("Third", "", "", "Normal")

    p1 = RawParagraph([run1])
    p2 = RawParagraph([run2])
    p3 = RawParagraph([run3])

    section.add(p1)
    section.add(p2)
    section.add(p3)

    assert section.next(0) == p2
    assert section.next(1) == p3
    assert section.next(2) is None


def test_next_paragraph(section):
    """Test getting next paragraph"""
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")

    p1 = RawParagraph([run1])
    p2 = RawParagraph([run2])

    section.add(p1)
    section.add(RawList())  # Add non-paragraph item
    section.add(p2)

    assert section.next_paragraph(0) == p1
    assert section.next_paragraph(1) == p2
    assert section.next_paragraph(2) == p2


def test_next_table(section):
    """Test getting next table"""
    table1 = RawTable()
    table2 = RawTable()

    section.add(table1)
    section.add(RawParagraph([RawRun("Test", "", "", "Normal")]))  # Add non-table item
    section.add(table2)

    assert section.next_table(0) == table1
    assert section.next_table(1) == table2
    assert section.next_table(3) is None


def test_format_heading(section):
    """Test formatting section heading"""
    assert section._format_heading() == "<h1>Test Content Test Section</h1>"

    # Test with only title
    section_title_only = RawSection("Title Only", "", 1)
    assert section_title_only._format_heading() == "<h1>Title Only</h1>"

    # Test with only number
    section_number_only = RawSection("", "1.1", 1)
    assert section_number_only._format_heading() == "<h1>1.1</h1>"

    # Test with neither
    section_empty = RawSection("", "", 1)
    assert section_empty._format_heading() == ""


def test_to_dict(section):
    """Test converting section to dictionary"""
    # Add various types of content
    run = RawRun("Test paragraph", "", "", "Normal")
    section.add(RawParagraph([run]))

    list_obj = RawList(1)
    list_obj.add(RawListItem([RawRun("Test item", "", None, "Normal")], 1))
    section.add(list_obj)

    table = RawTable()
    row = RawTableRow()
    cell = RawTableCell(1, 1, True)
    run = RawRun("Table content", "", "", "Normal")
    para = RawParagraph([run])
    cell.add(para)
    row.add(cell)
    table.add(row)
    section.add(table)

    result = section.to_dict()
    assert result["type"] == "section"
    assert result["title"] == "Test Section"
    assert result["number"] == "Test Content"
    assert result["level"] == 1
    assert len(result["items"]) == 3

    # Check paragraph
    assert result["items"][0]["type"] == "paragraph"
    assert result["items"][0]["text"] == "Test paragraph"

    # Check list
    assert result["items"][1]["type"] == "list"
    assert len(result["items"][1]["items"]) == 1
    assert result["items"][1]["items"][0]["text"] == "Test item"

    # Check table
    assert result["items"][2]["type"] == "table"
    assert len(result["items"][2]["rows"]) == 1
    cell_content = result["items"][2]["rows"][0]["cells"][0]["content"][0]
    assert cell_content["text"] == "Table content"


def test_section_navigation(section):
    """Test section navigation methods"""
    # Add test items
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    para1 = RawParagraph([run1])
    para2 = RawParagraph([run2])
    table1 = RawTable()

    section.add(para1)
    section.add(table1)
    section.add(para2)

    # Test next item
    assert section.next(0) == table1
    assert section.next(1) == para2
    assert section.next(2) is None

    # Test next paragraph
    assert section.next_paragraph(0) == para1
    assert section.next_paragraph(1) == para2
    assert section.next_paragraph(3) is None

    # Test next table
    assert section.next_table(0) == table1
    assert section.next_table(2) is None


def test_section_search(section):
    """Test section search methods"""
    # Add test paragraphs
    run1 = RawRun("Test Content", "", "", "Normal")
    run2 = RawRun("Another Test", "", "", "Normal")
    run3 = RawRun("Test at start", "", "", "Normal")

    para1 = RawParagraph([run1])
    para2 = RawParagraph([run2])
    para3 = RawParagraph([run3])

    section.add(para1)
    section.add(para2)
    section.add(para3)

    # Test general find
    found = section.find("Test")
    assert len(found) == 3
    assert para1 in found
    assert para2 in found
    assert para3 in found

    # Test find at start
    found_at_start = section.find_at_start("Test")
    assert len(found_at_start) == 2
    assert para1 in found_at_start
    assert para3 in found_at_start
    assert para2 not in found_at_start

    # Test find first at start
    found_first, index = section.find_first_at_start("Test")
    assert found_first == para1
    assert index == 0

    # Test find with no matches
    found_none = section.find("NonExistent")
    assert len(found_none) == 0

    found_none_first, index = section.find_first_at_start("NonExistent")
    assert found_none_first is None
    assert index == -1


def test_section_list_operations(section):
    """Test list-related operations"""
    # Test empty section
    assert not section.is_in_list()
    assert section.current_list() is None
    assert not section.has_lists()

    # Add a list
    list1 = RawList(1)
    section.add(list1)

    # Test with list
    assert section.is_in_list()
    assert section.current_list() == list1
    assert section.has_lists()

    # Add non-list item
    run = RawRun("Text", "", "", "Normal")
    section.add(RawParagraph([run]))
    assert not section.is_in_list()
    assert section.current_list() is None
    assert section.has_lists()  # Still has a list, just not current


def test_section_html_formatting(section):
    """Test HTML formatting with different title/number combinations"""
    # Test with both title and number
    section = RawSection("Test Title", "1.1", 2)
    assert section._format_heading() == "<h2>1.1 Test Title</h2>"

    # Test with only number
    section = RawSection(None, "1.1", 2)
    assert section._format_heading() == "<h2>1.1</h2>"

    # Test with only title
    section = RawSection("Test Title", None, 2)
    assert section._format_heading() == "<h2>Test Title</h2>"

    # Test with neither
    section = RawSection(None, None, 2)
    assert section._format_heading() == ""

    # Test HTML between specific indices
    section = RawSection("Test", "1", 1)
    run1 = RawRun("First", "", "", "Normal")
    run2 = RawRun("Second", "", "", "Normal")
    run3 = RawRun("Third", "", "", "Normal")

    section.add(RawParagraph([run1]))
    section.add(RawParagraph([run2]))
    section.add(RawParagraph([run3]))

    html = section.to_html_between(1, 3)
    assert "First" not in html
    assert "Second" in html
    assert "Third" in html
