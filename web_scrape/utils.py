import logging

logging.basicConfig(
    filename="web_scrape.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',  # Formats time up to seconds
    level=logging.INFO,
    encoding="utf-8" #TODO: Look into if SQL can do this encoding
)

def log(message, level="info"):
    """
    Args:
        message (str): The message to log.
        level (str): The logging level ('info', 'debug', 'warning', 'error', 'critical').
    """
    if level == "debug":
        logging.debug(message)
    elif level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "critical":
        logging.critical(message)
    else:
        logging.info(message)
