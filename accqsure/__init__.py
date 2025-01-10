import logging
from .accqsure import AccQsure

logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


__version__ = "0.1.5"
__all__ = "AccQsure"
