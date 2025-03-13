import logging
import logging.handlers
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Get current date for log file name
current_date = datetime.now().strftime('%Y-%m-%d')

def setup_logger():
    # Create logger
    logger = logging.getLogger('StreamlitApp')
    logger.setLevel(logging.DEBUG)

    # Create handlers
    # File handler for all logs
    all_logs_file = os.path.join('logs', f'app_{current_date}.log')
    file_handler = logging.FileHandler(all_logs_file)
    file_handler.setLevel(logging.DEBUG)

    # File handler for errors only
    error_logs_file = os.path.join('logs', f'error_{current_date}.log')
    error_file_handler = logging.FileHandler(error_logs_file)
    error_file_handler.setLevel(logging.ERROR)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatters and add it to the handlers
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    file_handler.setFormatter(file_formatter)
    error_file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
    logger.addHandler(console_handler)

    return logger

# Create a function to log Streamlit events
def log_streamlit_event(logger, event_type, message, extra_data=None):
    log_message = f"Streamlit {event_type}: {message}"
    if extra_data:
        log_message += f" | Additional Data: {extra_data}"
    logger.info(log_message)