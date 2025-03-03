from mlog import MLog

if __name__ == "__main__":
    logger = MLog(__name__)

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.trace("This is a trace message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")