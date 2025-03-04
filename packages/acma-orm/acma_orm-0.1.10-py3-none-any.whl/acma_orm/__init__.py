import logging

# Create a package-level logger.
logger = logging.getLogger(__name__)
# By default, attach a NullHandler so that if the user doesn't configure logging, nothing is output.
logger.addHandler(logging.NullHandler())


def enable_debug_logging():
    """Enable logging to stdout for development."""
    import sys

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "[%(filename)-10s][%(funcName)-20.20s][%(levelname)-8s] %(message)s"
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
