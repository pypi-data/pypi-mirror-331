# build_pipeline.py
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from tidyflow.utils.logger import log_action



def build_pipeline(df: pd.DataFrame, target_column: str = None, drop_threshold: float = 0.4) -> Pipeline:
    """Creates a Scikit-learn pipeline for preprocessing numerical and categorical features."""
    log_action("Building preprocessing pipeline")

    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Define transformations
    num_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='mean')),
                                      ('scaler', StandardScaler())])

    cat_transformer = Pipeline(steps=[('imputer', SimpleImputer(strategy='most_frequent')),
                                      ('encoder', OneHotEncoder(handle_unknown='ignore'))])

    # Combine transformations
    preprocessor = ColumnTransformer(transformers=[
        ('num', num_transformer, num_cols),
        ('cat', cat_transformer, cat_cols)
    ])

    pipeline = Pipeline(steps=[('preprocessor', preprocessor)])

    return pipeline