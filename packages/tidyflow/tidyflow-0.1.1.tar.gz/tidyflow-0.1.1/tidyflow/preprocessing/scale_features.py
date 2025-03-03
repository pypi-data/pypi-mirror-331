# scale_features.py
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from tidyflow.utils.logger import log_action



def scale_features(df: pd.DataFrame, method: str = 'standard') -> pd.DataFrame:
    """Scales numerical features using the specified method."""
    log_action(f"Scaling features using method: {method}")

    scaler_dict = {
        'standard': StandardScaler(),
        'minmax': MinMaxScaler(),
        'robust': RobustScaler()
    }

    scaler = scaler_dict.get(method)
    if scaler:
        num_cols = df.select_dtypes(include=['number']).columns
        df[num_cols] = scaler.fit_transform(df[num_cols])
    return df
