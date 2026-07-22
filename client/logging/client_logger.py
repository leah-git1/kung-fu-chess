import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

_logger = logging.getLogger("client")
_logger.setLevel(logging.DEBUG)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                          datefmt="%Y-%m-%d %H:%M:%S")

_fh = RotatingFileHandler(
    os.path.join(_LOG_DIR, "client.log"),
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
)
_fh.setFormatter(_fmt)
_logger.addHandler(_fh)

_ch = logging.StreamHandler()
_ch.setFormatter(_fmt)
_logger.addHandler(_ch)


def log(msg: str, level: str = "info") -> None:
    getattr(_logger, level)(msg)
