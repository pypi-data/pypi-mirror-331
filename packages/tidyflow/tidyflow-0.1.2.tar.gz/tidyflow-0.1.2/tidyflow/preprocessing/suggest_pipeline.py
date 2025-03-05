# suggest_pipeline.py
import pandas as pd
from tidyflow.utils.logger import log_action



def suggest_pipeline(df: pd.DataFrame) -> list:
    """Generates preprocessing suggestions based on dataset characteristics."""
    log_action("Generating preprocessing suggestions")

    suggestions = []

    # Check for missing values
    missing_info = df.isnull().sum() / len(df) * 100
    high_missing = missing_info[missing_info > 40].index.tolist()
    if high_missing:
        suggestions.append(f"Columns {high_missing} have more than 40% missing values—consider dropping or imputing.")

    # Detect highly skewed numerical columns
    skewed = df.select_dtypes(include=['number']).skew()
    high_skew = skewed[abs(skewed) > 1].index.tolist()
    if high_skew:
        suggestions.append(f"Columns {high_skew} are highly skewed—consider log transformation.")

    # Detect low variance categorical columns
    cat_cols = df.select_dtypes(include=['object']).nunique()
    low_variance_cats = cat_cols[cat_cols / len(df) < 0.05].index.tolist()
    if low_variance_cats:
        suggestions.append(f"Columns {low_variance_cats} have low variance—consider dropping.")

    return suggestions
