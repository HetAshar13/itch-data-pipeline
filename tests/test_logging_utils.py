from itch_data_pipeline.utils.logging_utils import get_logger


def test_get_logger_does_not_add_duplicate_handlers():
    logger = get_logger("test_logger_no_duplicate_handlers")
    handler_count = len(logger.handlers)

    same_logger = get_logger("test_logger_no_duplicate_handlers")

    assert same_logger is logger
    assert len(same_logger.handlers) == handler_count
