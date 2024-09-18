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


# import os
# import platform
# import logging
# from aiologger import Logger
# from logging.handlers import RotatingFileHandler
#
#
# def is_windows():
#     """Check if the system is Windows."""
#     return platform.system().lower() == "windows"
#
#
# class AsyncPrependFileHandler(logging.Handler):
#     """
#     Custom async-compatible log handler for prepending new log entries to the top of the log file.
#     For Windows, it will fall back to using synchronous logging.
#     """
#
#     def __init__(self, filename):
#         super().__init__()
#         self.filename = filename
#
#     def emit(self, record):
#         """Handle emitting the log record, prepend the log synchronously."""
#         log_entry = self.format(record)
#
#         # Read the current log file content
#         if os.path.exists(self.filename):
#             with open(self.filename, 'r', encoding='utf-8') as f:
#                 existing_content = f.read()
#         else:
#             existing_content = ''
#
#         # Write the new log entry at the top, followed by the old content
#         with open(self.filename, 'w', encoding='utf-8') as f:
#             f.write(log_entry + '\n' + existing_content)
#
#
# async def get_logger(name: str, log_file: str = 'app.log', max_bytes: int = 10 * 1024 * 1024, backup_count: int = 10):
#     """
#     Sets up and returns an asynchronous logger instance for non-Windows systems,
#     and falls back to synchronous logging on Windows.
#     """
#     if is_windows():
#         # Use synchronous logger on Windows to avoid NotImplementedError
#         logger = logging.getLogger(name)
#         logger.setLevel(logging.INFO)
#
#         file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
#         file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#
#         prepend_handler = AsyncPrependFileHandler(log_file)
#         prepend_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#
#         logger.addHandler(file_handler)
#         logger.addHandler(prepend_handler)
#
#         return logger
#     else:
#         # Use aiologger for non-Windows systems
#         logger = Logger.with_default_handlers(name=name)
#         prepend_handler = AsyncPrependFileHandler(log_file)
#         prepend_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#         await logger.add_handler(prepend_handler)
#         return logger