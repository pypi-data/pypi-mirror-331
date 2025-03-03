# encode_categoricals.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from tidyflow.utils.logger import log_action



def encode_categoricals(df: pd.DataFrame, method: str = 'onehot') -> pd.DataFrame:
    """Encodes categorical variables using the specified method."""
    df = df.copy()
    log_action(f"Encoding categorical variables using method: {method}")

    if method == 'onehot':
        return pd.get_dummies(df, drop_first=True)
    elif method == 'label':
        le = LabelEncoder()
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = le.fit_transform(df[col])
    return df
