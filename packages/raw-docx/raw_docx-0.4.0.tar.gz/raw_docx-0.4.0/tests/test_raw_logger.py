import json
import logging
import pytest
from pathlib import Path
from raw_logger import RawLogger


@pytest.fixture
def logger_instance():
    """Fixture to provide a fresh logger instance for each test"""
    # Reset the singleton state
    RawLogger._instance = None
    RawLogger._initialized = False

    # Clear any existing handlers
    logger = logging.getLogger("raw_docx")
    logger.handlers.clear()

    return RawLogger()


@pytest.fixture
def temp_log_dir(tmp_path):
    """Fixture to provide a temporary directory for log files"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return str(log_dir)


def test_singleton_pattern():
    """Test that RawLogger implements singleton pattern correctly"""
    logger1 = RawLogger()
    logger2 = RawLogger()
    assert logger1 is logger2


def test_default_initialization(logger_instance):
    """Test default logger initialization"""
    assert logger_instance.logger.level == logging.INFO
    assert len(logger_instance.logger.handlers) == 1
    assert isinstance(logger_instance.logger.handlers[0], logging.StreamHandler)


def test_file_logging_setup(logger_instance, temp_log_dir):
    """Test setting up file logging"""
    logger_instance.setup_file_logging(temp_log_dir)

    # Check that a file handler was added
    assert len(logger_instance.logger.handlers) == 2
    assert any(
        isinstance(h, logging.FileHandler) for h in logger_instance.logger.handlers
    )

    # Check that log file was created
    log_file = Path(temp_log_dir) / "raw_docx.log"
    assert log_file.exists()


def test_log_message_format(logger_instance, temp_log_dir, caplog):
    """Test that log messages are properly formatted as JSON"""
    logger_instance.setup_file_logging(temp_log_dir)

    test_message = "Test log message"
    logger_instance.info(test_message)

    # Read the log file
    log_file = Path(temp_log_dir) / "raw_docx.log"
    with open(log_file) as f:
        log_entry = json.loads(f.readline())

    # Check JSON structure
    assert "asctime" in log_entry
    assert "name" in log_entry
    assert "levelname" in log_entry
    assert "message" in log_entry
    assert log_entry["message"] == test_message
    assert log_entry["levelname"] == "INFO"


def test_log_levels(logger_instance, caplog):
    """Test different log levels"""
    test_message = "Test message"

    logger_instance.info(test_message)
    assert "INFO" in caplog.text

    logger_instance.warning(test_message)
    assert "WARNING" in caplog.text

    logger_instance.error(test_message)
    assert "ERROR" in caplog.text


def test_exception_logging(logger_instance, caplog):
    """Test exception logging"""
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        logger_instance.exception("Error occurred", e)

    assert "ERROR" in caplog.text
    assert "Test exception" in caplog.text


def test_invalid_log_directory(logger_instance, tmp_path):
    """Test handling of invalid log directory"""
    invalid_dir = tmp_path / "nonexistent" / "logs"
    logger_instance.setup_file_logging(str(invalid_dir))

    # Check that the directory was created
    assert invalid_dir.exists()
    assert invalid_dir.is_dir()
