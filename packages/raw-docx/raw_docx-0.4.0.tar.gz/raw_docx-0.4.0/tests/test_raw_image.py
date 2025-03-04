import pytest
from raw_image import RawImage


@pytest.fixture
def temp_image_jpg(tmp_path):
    """Create a temporary JPG image file"""
    image_path = tmp_path / "test.jpg"
    image_path.write_bytes(b"dummy jpg content")
    return str(image_path)


@pytest.fixture
def temp_image_png(tmp_path):
    """Create a temporary PNG image file"""
    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"dummy png content")
    return str(image_path)


@pytest.fixture
def temp_image_unsupported(tmp_path):
    """Create a temporary unsupported image file"""
    image_path = tmp_path / "test.gif"
    image_path.write_bytes(b"dummy gif content")
    return str(image_path)


def test_image_initialization_jpg(temp_image_jpg):
    """Test image initialization with JPG"""
    image = RawImage(temp_image_jpg)
    assert image.filepath == temp_image_jpg


def test_image_initialization_png(temp_image_png):
    """Test image initialization with PNG"""
    image = RawImage(temp_image_png)
    assert image.filepath == temp_image_png


def test_to_html_jpg(temp_image_jpg):
    """Test getting HTML for JPG image"""
    image = RawImage(temp_image_jpg)
    html = image.to_html()
    assert "data:image/jpg;base64," in html
    assert '<img alt="alt text" src=' in html


def test_to_html_png(temp_image_png):
    """Test getting HTML for PNG image"""
    image = RawImage(temp_image_png)
    html = image.to_html()
    assert "data:image/png;base64," in html
    assert '<img alt="alt text" src=' in html


def test_to_html_unsupported_format(temp_image_unsupported):
    """Test getting HTML for unsupported image format"""
    image = RawImage(temp_image_unsupported)
    html = image.to_html()
    assert "Unable to process embedded image" in html
    assert "color:red" in html


def test_to_html_missing_file(tmp_path):
    """Test getting HTML for missing image file"""
    missing_file = str(tmp_path / "missing.jpg")
    image = RawImage(missing_file)
    html = image.to_html()
    assert "Error encountered processing image" in html
    assert "color:red" in html


def test_supported_file_types():
    """Test supported file type mapping"""
    assert RawImage.FILE_TYPE_MAP[".png"] == "png"
    assert RawImage.FILE_TYPE_MAP[".jpg"] == "jpg"
    assert RawImage.FILE_TYPE_MAP[".jpeg"] == "jpg"


def test_to_dict_jpg(temp_image_jpg):
    """Test converting JPG image to dictionary"""
    image = RawImage(temp_image_jpg)
    result = image.to_dict()
    assert result["type"] == "image"
    assert result["filepath"] == temp_image_jpg
    assert result["extension"] == ".jpg"
    assert result["file_type"] == "jpg"


def test_to_dict_png(temp_image_png):
    """Test converting PNG image to dictionary"""
    image = RawImage(temp_image_png)
    result = image.to_dict()
    assert result["type"] == "image"
    assert result["filepath"] == temp_image_png
    assert result["extension"] == ".png"
    assert result["file_type"] == "png"


def test_to_dict_unsupported(temp_image_unsupported):
    """Test converting unsupported image to dictionary"""
    image = RawImage(temp_image_unsupported)
    result = image.to_dict()
    assert result["type"] == "image"
    assert result["filepath"] == temp_image_unsupported
    assert result["extension"] == ".gif"
    assert result["file_type"] == "unknown"
