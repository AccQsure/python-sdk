import logging
from .accqsure import AccQsure

TRACE = 5
logging.addLevelName(TRACE, "TRACE")


# Create a custom logger class or function to support TRACE
def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)


logging.Logger.trace = trace

logging.basicConfig(
    format="%(asctime)s.%(msecs)03dZ  %(levelname)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logger.propagate = False

__version__ = "0.2.7"
__all__ = ("AccQsure",)
