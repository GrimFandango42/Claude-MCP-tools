import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging format
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def setup_logger(name):
    """Setup and return a logger with the given name"""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    timestamp = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(logs_dir, f'{timestamp}.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger
