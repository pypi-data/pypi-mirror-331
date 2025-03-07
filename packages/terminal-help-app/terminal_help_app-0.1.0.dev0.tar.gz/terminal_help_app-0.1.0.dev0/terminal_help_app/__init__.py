import os

if "LOGURU_LEVEL" not in os.environ:
    os.environ["LOGURU_LEVEL"] = "INFO"

__version__ = "0.1.0"
