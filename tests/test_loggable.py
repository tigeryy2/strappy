import logging
from logging.handlers import RotatingFileHandler

from strappy.util.loggable import Loggable


def test_loggable_setup_adds_handlers(tmp_path):
    root_logger = logging.getLogger()
    prev_handlers = list(root_logger.handlers)
    prev_level = root_logger.level

    for handler in prev_handlers:
        root_logger.removeHandler(handler)

    try:
        Loggable.setup(log_path=tmp_path / "bootstrap.log")

        assert any(
            isinstance(handler, RotatingFileHandler)
            for handler in root_logger.handlers
        )
        assert any(
            isinstance(handler, logging.StreamHandler)
            for handler in root_logger.handlers
        )
    finally:
        for handler in list(root_logger.handlers):
            root_logger.removeHandler(handler)
        for handler in prev_handlers:
            root_logger.addHandler(handler)
        root_logger.setLevel(prev_level)
