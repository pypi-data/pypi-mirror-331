# __init__.py

"""Package initialization for TidyFlow."""

from .preprocessing.clean_missing import clean_missing
from .preprocessing.encode_categoricals import encode_categoricals
from .preprocessing.scale_features import scale_features
from .preprocessing.feature_engineer import feature_engineer
from .preprocessing.handle_outliers import handle_outliers
from .preprocessing.auto_dtype import auto_dtype
from .preprocessing.suggest_pipeline import suggest_pipeline
from .preprocessing.build_pipeline import build_pipeline

__all__ = [
    "clean_missing",
    "encode_categoricals",
    "scale_features",
    "feature_engineer",
    "handle_outliers",
    "auto_dtype",
    "suggest_pipeline",
    "build_pipeline"
]
