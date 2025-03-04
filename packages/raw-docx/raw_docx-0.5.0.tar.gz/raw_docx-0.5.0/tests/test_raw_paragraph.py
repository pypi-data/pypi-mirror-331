import pytest
from src.raw_docx.raw_paragraph import RawParagraph
from src.raw_docx.raw_run import RawRun


@pytest.fixture
def raw_paragraph():
    run = RawRun("Test paragraph", "", None, "Normal")
    return RawParagraph([run])


def test_initialization():
    """Test paragraph initialization with whitespace handling"""
    run = RawRun("  Test paragraph with spaces  ", "", None, "Normal")
    paragraph = RawParagraph([run])
    assert paragraph.text == "  Test paragraph with spaces  "
    assert paragraph.klasses == []


def test_to_html_no_classes(raw_paragraph):
    """Test converting paragraph to HTML without classes"""
    assert raw_paragraph.to_html() == "<p>Test paragraph</p>"


def test_to_html_with_classes():
    """Test converting paragraph to HTML with classes"""
    run = RawRun("Test paragraph", "", None, "Normal")
    paragraph = RawParagraph([run])
    paragraph.add_class("class1")
    paragraph.add_class("class2")
    assert paragraph.to_html() == '<p class="class1 class2">Test paragraph</p>'


def test_find():
    """Test finding text in paragraph"""
    run = RawRun("This is a test paragraph", "", None, "Normal")
    paragraph = RawParagraph([run])
    assert paragraph.find("test") is True
    assert paragraph.find("not present") is False


def test_find_at_start():
    """Test finding text at start of paragraph with case insensitivity"""
    run = RawRun("Test paragraph", "", None, "Normal")
    paragraph = RawParagraph([run])
    assert paragraph.find_at_start("test") is True
    assert paragraph.find_at_start("TEST") is True
    assert paragraph.find_at_start("paragraph") is False


def test_add_class():
    """Test adding classes to paragraph"""
    run = RawRun("Test paragraph", "", None, "Normal")
    paragraph = RawParagraph([run])
    paragraph.add_class("class1")
    assert "class1" in paragraph.klasses
    paragraph.add_class("class2")
    assert "class2" in paragraph.klasses


def test_to_dict():
    """Test converting paragraph to dictionary"""
    run1 = RawRun("Test ", "FF0000", None, "Normal")
    run2 = RawRun("paragraph", "0000FF", None, "Bold")
    paragraph = RawParagraph([run1, run2])
    paragraph.add_class("test-class")

    result = paragraph.to_dict()
    assert result["type"] == "paragraph"
    assert result["text"] == "Test paragraph"
    assert result["classes"] == ["test-class"]
    assert len(result["runs"]) == 2
    assert result["runs"][0]["text"] == "Test "
    assert result["runs"][0]["color"] == "FF0000"
    assert result["runs"][1]["text"] == "paragraph"
    assert result["runs"][1]["color"] == "0000FF"


def test_multiple_runs():
    """Test paragraph with multiple runs"""
    run1 = RawRun("Hello ", "FF0000", None, "Normal")
    run2 = RawRun("World", "0000FF", None, "Bold")
    paragraph = RawParagraph([run1, run2])

    assert paragraph.text == "Hello World"
    assert len(paragraph.runs) == 2
    assert paragraph.runs[0].text == "Hello "
    assert paragraph.runs[0].color == "FF0000"
    assert paragraph.runs[1].text == "World"
    assert paragraph.runs[1].color == "0000FF"


def test_empty_paragraph():
    """Test paragraph with no runs"""
    paragraph = RawParagraph([])
    assert paragraph.text == ""
    assert len(paragraph.runs) == 0
