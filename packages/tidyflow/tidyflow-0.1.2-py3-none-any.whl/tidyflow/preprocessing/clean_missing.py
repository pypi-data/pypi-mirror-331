import pandas as pd
from tidyflow.utils.logger import log_action

def clean_missing(df: pd.DataFrame, strategy: str = 'mean', threshold: float = 0.5) -> pd.DataFrame:
    """
    Handles missing values in a DataFrame by imputing or dropping.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        strategy (str): The imputation strategy ('mean', 'median', 'mode', 'ffill', 'bfill', 'drop').
        threshold (float): Threshold for dropping columns with excessive missing values.

    Returns:
        pd.DataFrame: The cleaned DataFrame.
    """
    log_action(f"Handling missing values using strategy: {strategy}")

    # Drop columns with missing values above the threshold
    missing_percent = df.isnull().mean()
    df = df.drop(columns=missing_percent[missing_percent > threshold].index)

    num_cols = df.select_dtypes(include=['number']).columns
    cat_cols = df.select_dtypes(include=['object']).columns

    if strategy in ['mean', 'median']:
        if not num_cols.empty:
            df[num_cols] = df[num_cols].fillna(df[num_cols].agg(strategy))
    elif strategy == 'mode':
        for col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])
    elif strategy in ['ffill', 'bfill']:
        df = df.fillna(method=strategy)
    elif strategy == 'drop':
        df = df.dropna()
    else:
        raise ValueError(f"Invalid strategy '{strategy}' for handling missing values.")

    return df
