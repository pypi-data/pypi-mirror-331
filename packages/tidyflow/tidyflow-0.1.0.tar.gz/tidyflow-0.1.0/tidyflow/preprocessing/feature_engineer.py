# feature_engineer.py
import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
from tidyflow.utils.logger import log_action



def feature_engineer(df: pd.DataFrame, method: str = 'poly', degree: int = 2) -> pd.DataFrame:
    """Applies feature engineering techniques like polynomial features."""
    log_action(f"Applying feature engineering using method: {method}, degree: {degree}")

    if method == 'poly':
        poly = PolynomialFeatures(degree)
        num_cols = df.select_dtypes(include=['number']).columns
        df_poly = pd.DataFrame(poly.fit_transform(df[num_cols]), columns=poly.get_feature_names_out(num_cols))
        df = df.drop(columns=num_cols).join(df_poly)

    return df
