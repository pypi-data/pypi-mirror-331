# auto_dtype.py
import pandas as pd
from tidyflow.utils.logger import log_action



def auto_dtype(df: pd.DataFrame) -> pd.DataFrame:
    """Automatically detects and converts data types in a DataFrame."""
    log_action("Automatically detecting and converting data types")

    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                try:
                    df[col] = pd.to_datetime(df[col])
                except ValueError:
                    pass

    return df
