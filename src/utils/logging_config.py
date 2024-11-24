import logging
import os
from pythonjsonlogger import jsonlogger
from datetime import datetime
import sys

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['service'] = 'duckdb-spawn-api'
        log_record['logger'] = record.name
        
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

def setup_logging(default_level=logging.INFO):
    # Define the log directory and file
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    log_file = os.path.join(log_dir, 'duckdb_spawn.log')
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Get the root logger
    logger = logging.getLogger('data_product')
    logger.setLevel(default_level)
    
    # Remove existing handlers if any
    if logger.handlers:
        logger.handlers.clear()
    
    # Create file handler with JSON formatting
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(default_level)
    json_formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    file_handler.setFormatter(json_formatter)
    
    # Create console handler with standard formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(default_level)
    standard_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(standard_formatter)
    
    # Add the handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Set propagate to False to avoid duplicate logs
    logger.propagate = False
    
    return logger 