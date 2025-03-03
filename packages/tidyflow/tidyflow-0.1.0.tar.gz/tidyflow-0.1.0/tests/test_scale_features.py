# tests/test_scale_features.py
import pandas as pd
import pytest
from tidyflow.preprocessing.scale_features import scale_features

def test_scale_features():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    result = scale_features(df, method='minmax')
    assert result.min().min() == 0 and result.max().max() == 1
