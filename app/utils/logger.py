import logging


def config_logger():
    logging_level = logging.INFO
    logging_fmt = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d: %(message)s"  # the default
    try:
        root_logger = logging.getLogger()
        root_logger.setLevel(logging_level)
        root_handler = root_logger.handlers[0]
        root_handler.setFormatter(logging.Formatter(logging_fmt))
    except IndexError:
        logging.basicConfig(level=logging_level, format=logging_fmt)
