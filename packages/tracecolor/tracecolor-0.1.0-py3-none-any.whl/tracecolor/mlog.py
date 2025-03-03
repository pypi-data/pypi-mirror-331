import logging
import colorlog
import time

class _GrayLogFormatter(logging.Formatter):
    def format(self, record):
        # Prefix the message with the ANSI code for gray and suffix with reset
        original_message = super().format(record)
        gray_message = f'\033[90m{original_message}\033[0m'  # 90 is bright black, which looks gray
        return gray_message

class MLog(logging.Logger):
    """
    Enhanced logger with colorized output and TRACE level.
    
    Features:
    - Custom TRACE logging level (lower than DEBUG)
    - Colorized output for different log levels
    - Rate-limiting for TRACE messages (once per second)
    - Timestamped log format
    
    Usage:
    ```python
    from tracecolor import MLog
    
    logger = MLog(__name__)
    logger.trace("Detailed trace message")
    logger.debug("Debug information")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error")
    ```
    """
    TRACE_LEVEL = 5  # Define TRACE level

    def __init__(self, name):
        super().__init__(name)

        # Add custom TRACE level
        logging.addLevelName(self.TRACE_LEVEL, "TRACE")

        # Set up color formatter for standard log levels
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(levelname).1s%(reset)s |%(asctime)s.%(msecs)03d| %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
                'TRACE': 'white',
            }
        )

        # Console handler for standard log levels
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        # Set the logger level to the lowest to capture all messages
        self.setLevel(self.TRACE_LEVEL)
        self.propagate = False

        # Initialize last log time for rate-limiting
        self._last_trace_log_time = 0

    def trace(self, message, *args, **kwargs):
        """Log a message with severity 'TRACE'."""
        if self.isEnabledFor(self.TRACE_LEVEL):
            current_time = time.time()
            # Rate-limiting: Log only if a second has passed since the last log
            if current_time - self._last_trace_log_time >= 1:
                self._last_trace_log_time = current_time
                self.log(self.TRACE_LEVEL, message, *args, **kwargs)

# Monkey-patch the logging module to add TRACE level methods
def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(MLog.TRACE_LEVEL):
        self._log(MLog.TRACE_LEVEL, message, args, **kwargs)

logging.Logger.trace = trace