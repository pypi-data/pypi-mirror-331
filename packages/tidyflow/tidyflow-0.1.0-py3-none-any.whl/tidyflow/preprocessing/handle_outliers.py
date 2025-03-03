import pandas as pd
from tidyflow.utils.logger import log_action


def handle_outliers(df: pd.DataFrame, method: str = 'iqr', strategy: str = 'clip') -> pd.DataFrame:
    """
    Detects and handles outliers in numerical data using the specified method.

    Parameters:
        df (pd.DataFrame): The input dataframe.
        method (str): The method for outlier detection ('iqr').
        strategy (str): How to handle outliers ('clip' or 'drop').

    Returns:
        pd.DataFrame: The dataframe with outliers handled.
    """
    log_action(f"Handling outliers using method: {method}, strategy: {strategy}")

    num_cols = df.select_dtypes(include=['number']).columns  # Select numerical columns

    if not num_cols.empty:  # Check if there are any numerical columns
        if method == 'iqr':
            Q1 = df[num_cols].quantile(0.25)
            Q3 = df[num_cols].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            if strategy == 'clip':
                # Apply clipping column-by-column with explicit scalar bounds
                for col in num_cols:
                    df[col] = df[col].clip(lower=float(lower_bound[col]), upper=float(upper_bound[col]))

            elif strategy == 'drop':
                mask = (df[num_cols] >= lower_bound) & (df[num_cols] <= upper_bound)
                df = df[mask.all(axis=1)]

    return df
