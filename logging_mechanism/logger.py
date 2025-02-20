import logging
import os

logging.basicConfig(
    filename="logging.txt",
    level=logging.INFO,
    format="%(levelname)s %(asctime)s %(message)s",  # Log format
    datefmt="%Y-%m-%d %H:%M:%S"  # Date format

)

logger = logging.getLogger("app_logger")