import logging

def write(content):
    file_path = "./data.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)

logging.basicConfig(
    filename="web_scrape.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
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
