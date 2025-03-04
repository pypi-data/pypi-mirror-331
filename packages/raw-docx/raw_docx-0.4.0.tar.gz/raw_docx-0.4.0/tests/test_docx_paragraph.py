from unittest.mock import Mock, PropertyMock
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx_paragraph import (
    extract_runs,
    _tidy_runs_color,
    _get_highlight_color,
    _run_style_color,
    _get_font_colour,
)


def create_mock_run(text="", color=None, highlight=None, style=None):
    """Helper function to create a mock run"""
    run = Mock(spec=Run)
    run.text = text

    # Setup font color
    run.font = Mock()
    run.font.color = Mock()
    if color:
        type(run.font.color).rgb = PropertyMock(return_value=color)
    else:
        run.font.color.rgb = None

    # Setup highlight color
    if highlight:
        type(run.font).highlight_color = PropertyMock(return_value=highlight)
    else:
        run.font.highlight_color = None

    # Setup style
    if style:
        run.style = Mock()
        run.style.name = style
        run.style.font = Mock()
        run.style.font.color = Mock()
        type(run.style.font.color).rgb = PropertyMock(return_value=None)
        run.style.base_style = None
    else:
        run.style = None

    return run


def create_mock_paragraph(text="", style_name="Normal"):
    """Helper function to create a mock paragraph"""
    paragraph = Mock(spec=Paragraph)
    paragraph.text = text
    paragraph.style = Mock()
    paragraph.style.name = style_name
    paragraph.style.font = Mock()
    paragraph.style.font.color = Mock()
    type(paragraph.style.font.color).rgb = PropertyMock(return_value=None)
    return paragraph


def test_get_font_colour():
    """Test getting font color from a run"""
    # Test with no color
    run = create_mock_run()
    assert _get_font_colour(run) is None

    # Test with color
    run = create_mock_run(color="FF0000")
    assert _get_font_colour(run) == "FF0000"

    # Test with exception
    run = Mock(spec=Run)
    run.font = (
        None  # This should cause an AttributeError when code tries to access color
    )
    assert _get_font_colour(run) is None


def test_get_highlight_color():
    """Test getting highlight color from a run"""
    # Test with no highlight
    run = Mock(spec=Run)
    run.font = None
    assert _get_highlight_color(run) is None

    # Test with highlight
    run = create_mock_run(highlight="yellow")
    assert _get_highlight_color(run) == "yellow"


def test_run_style_color():
    """Test getting color from run style"""
    # Test with no style
    run = create_mock_run()
    assert _run_style_color(run) is None

    # Test with direct style color
    run = create_mock_run(style="Normal")
    type(run.style.font.color).rgb = PropertyMock(return_value="FF0000")
    assert _run_style_color(run) == "FF0000"

    # Test with base style color
    run = create_mock_run(style="Normal")
    base_style = Mock()
    base_style.font = Mock()
    base_style.font.color = Mock()
    type(base_style.font.color).rgb = PropertyMock(return_value="0000FF")
    base_style.base_style = None
    run.style.base_style = base_style
    assert _run_style_color(run) == "0000FF"


def test_tidy_runs_color():
    """Test tidying up runs with colors"""
    # Test with different colors - should not merge
    data = [
        {
            "text": "Test",
            "color": "FF0000",
            "highlight": None,
            "style": "Normal",
            "keep": True,
        },
        {
            "text": "More",
            "color": "0000FF",
            "highlight": None,
            "style": "Normal",
            "keep": True,
        },
    ]
    result = _tidy_runs_color(data)
    assert len(result) == 2
    assert all(item["keep"] for item in result)

    # Test with same colors and styles - should merge
    data = [
        {
            "text": "Test",
            "color": "FF0000",
            "highlight": None,
            "style": "Normal",
            "keep": True,
        },
        {
            "text": " ",
            "color": "FF0000",
            "highlight": None,
            "style": "Normal",
            "keep": True,
        },
        {
            "text": "More",
            "color": "FF0000",
            "highlight": None,
            "style": "Normal",
            "keep": True,
        },
    ]
    result = _tidy_runs_color(data)
    assert len(result) == 1
    assert result[0]["text"] == "Test More"


def test_extract_runs_mixed_styles():
    """Test extracting runs with different styles"""
    paragraph = create_mock_paragraph()
    runs = [
        create_mock_run("Bold", "FF0000", None, "Bold"),
        create_mock_run("Normal", "FF00FF", None, "Normal"),
        create_mock_run("Italic", "0000FF", None, "Italic"),
    ]
    paragraph.runs = runs

    result = extract_runs(paragraph)
    assert len(result) == 3
    assert [r.style for r in result] == ["Normal", "Normal", "Normal"]


def test_extract_runs_with_mixed_colors():
    """Test extracting runs with different colors and highlights"""
    paragraph = create_mock_paragraph()
    runs = [
        create_mock_run("Red", "FF0000", "yellow", "Normal"),
        create_mock_run("Blue", "0000FF", "green", "Normal"),
        create_mock_run("Red2", "FF0000", "yellow", "Normal"),
    ]
    paragraph.runs = runs

    result = extract_runs(paragraph)
    assert len(result) == 3
    assert [r.color for r in result] == ["FF0000", "0000FF", "FF0000"]
