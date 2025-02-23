import logging
import os

LOG_DIR=os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "execution_logs.log")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)


if not logger.handlers:
    file_handler = logging.FileHandler(LOG_FILE, mode='a')
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S"))
    
    # Add handlers
    logger.addHandler(file_handler)

def log_message(id: str, message: str, level="info"):
    """
    Log a message with a specified log level.

    Parameters:
    id (str): A unique identifier for the message, such as a request ID or session ID or uuid.
    message (str): The message to log.
    level (str, optional): The log level for the message. Default is "info". 
                           Can be one of "info", "warning", "error", "debug".

    Logs the message at the specified log level. If an unrecognized log level is provided,
    logs the message at the "info" level by default.
    """

    formatted_message = f"{id} - {message}"
    
    if level.lower() == "info":
        logger.info(formatted_message)
    elif level.lower() == "warning":
        logger.warning(formatted_message)
    elif level.lower() == "error":
        logger.error(formatted_message)
    elif level.lower() == "debug":
        logger.debug(formatted_message)
    else:
        logger.info(formatted_message) 