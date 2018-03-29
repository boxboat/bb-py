import logging


def setup_logging(logger_name, log_level=logging.INFO):
    format_string = '%(asctime)s %(name)s [%(levelname)s] %(message)s'
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    set_stream_handler(log_level, format_string)


def set_stream_handler(log_level, format_string=None):
    if format_string is None:
        format_string = '%(asctime)s %(name)s [%(levelname)s] %(message)s'

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger(__name__).addHandler(NullHandler())
