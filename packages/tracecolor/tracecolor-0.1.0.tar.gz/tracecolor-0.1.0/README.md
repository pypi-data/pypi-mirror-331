# TraceColor

A lightweight, colorized Python logger with TRACE level support.

## Features

- Custom TRACE logging level (lower than DEBUG)
- Colorized output for different log levels
- Rate-limiting for TRACE messages
- Simple and clean API

## Installation

```bash
pip install tracecolor
```

## Usage

```python
from tracecolor import MLog

# Create a logger
logger = MLog(__name__)

# Log at different levels
logger.trace("Detailed tracing information")
logger.debug("Debugging information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

## Color Scheme

- TRACE: White
- DEBUG: Cyan
- INFO: Green
- WARNING: Yellow
- ERROR: Red
- CRITICAL: Bold Red

## License

MIT