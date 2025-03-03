# utils/helpers.py
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(action: str):
    """Logs the preprocessing step."""
    logging.info(action)

def validate_dataframe(df):
    """Validates if input is a valid pandas DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
