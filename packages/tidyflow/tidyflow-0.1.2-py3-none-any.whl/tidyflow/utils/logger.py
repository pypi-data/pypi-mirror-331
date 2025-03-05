# utils/logger.py

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(action: str):
    """Logs the preprocessing step."""
    logging.info(action)
