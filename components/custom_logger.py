import logging
from logging.handlers import MemoryHandler, RotatingFileHandler


def get_logger(name: str, log_file: str = 'app.log', max_bytes: int = 10 * 1024 * 1024, backup_count: int = 10,
               memory_capacity: int = 10000):
    """
    Sets up and returns a logger instance.

    Args:
        name (str): The name of the logger.
        log_file (str): Path to the log file.
        max_bytes (int): Maximum size of the log file before rotation (default 10MB).
        backup_count (int): Number of backup files to keep (default 10).
        memory_capacity (int): Maximum number of log entries to keep in memory (default 10,000).

    Returns:
        logging.Logger: Configured logger instance.
    """

    # Set up the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Configure a RotatingFileHandler that keeps the last 10,000 log rows
    log_file_handler = RotatingFileHandler(
        log_file,  # The log file path
        maxBytes=max_bytes,  # Maximum log file size (10MB by default)
        backupCount=backup_count  # Number of backup log files to keep
    )

    # Set up the MemoryHandler to buffer logs and flush when full or upon critical events
    memory_handler = MemoryHandler(
        capacity=memory_capacity,  # Save only the last 10,000 log records in memory
        flushLevel=logging.ERROR,  # Automatically flush on ERROR or higher level logs
        target=log_file_handler  # Output to rotating file handler
    )

    # Formatter for the logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file_handler.setFormatter(formatter)
    memory_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(memory_handler)
    logger.addHandler(log_file_handler)

    return logger