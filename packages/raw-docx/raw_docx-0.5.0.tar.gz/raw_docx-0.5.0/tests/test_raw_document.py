import pytest
from src.raw_docx.raw_document import RawDocument
from src.raw_docx.raw_section import RawSection
from src.raw_docx.raw_paragraph import RawParagraph
from src.raw_docx.raw_run import RawRun


@pytest.fixture
def document():
    return RawDocument()


@pytest.fixture
def sample_section():
    return RawSection("Test Section", "Test Section Content", 1)


def test_document_initialization(document):
    """Test document initialization"""
    assert len(document.sections) == 1
    assert document.current_section() is not None


def test_add_section(document, sample_section):
    """Test adding a section to the document"""
    document.add(sample_section)
    assert len(document.sections) == 2
    assert document.sections[1] == sample_section


def test_current_section_empty_document(document):
    """Test current_section with empty document"""
    current = document.current_section()
    assert isinstance(current, RawSection)
    assert current.level == 1


def test_current_section_with_sections(document, sample_section):
    """Test current_section with existing sections"""
    document.add(sample_section)
    current = document.current_section()
    assert current == sample_section


def test_to_dict(document):
    """Test converting document to dictionary"""
    # Add sections with content
    section1 = RawSection("Section 1", "1", 1)
    section1.add(RawParagraph([RawRun("Content 1", "", "", "Normal")]))
    document.add(section1)

    section2 = RawSection("Section 2", "2", 1)
    section2.add(RawParagraph([RawRun("Content 2", "", "", "Normal")]))
    document.add(section2)

    result = document.to_dict()
    assert result["type"] == "document"
    assert len(result["sections"]) == 3  # Including initial empty section
    assert result["levels"] == [0, 2, 0, 0, 0, 0]

    # Check sections
    section1_dict = result["sections"][1]  # Skip initial empty section
    assert section1_dict["title"] == "Section 1"
    assert section1_dict["number"] == "1"
    assert section1_dict["items"][0]["text"] == "Content 1"

    section2_dict = result["sections"][2]
    assert section2_dict["title"] == "Section 2"
    assert section2_dict["number"] == "2"
    assert section2_dict["items"][0]["text"] == "Content 2"

    # Check mappings
    assert "1" in result["section_number_mapping"]
    assert "2" in result["section_number_mapping"]
    assert "Section 1" in result["section_title_mapping"]
    assert "Section 2" in result["section_title_mapping"]
