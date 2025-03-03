# tests/test_feature_engineer.py
import pandas as pd
import pytest
from tidyflow.preprocessing.feature_engineer import feature_engineer

def test_feature_engineer():
    df = pd.DataFrame({'A': [1, 2, 3]})
    result = feature_engineer(df, method='poly', degree=2)
    assert result.shape[1] > df.shape[1]
