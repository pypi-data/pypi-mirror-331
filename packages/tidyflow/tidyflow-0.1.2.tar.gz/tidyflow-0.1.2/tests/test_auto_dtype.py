# tests/test_auto_dtype.py
import pandas as pd
import pytest
from tidyflow.preprocessing.auto_dtype import auto_dtype

def test_auto_dtype():
    df = pd.DataFrame({'A': ['1', '2', '3'], 'B': ['2020-01-01', '2021-01-01', '2022-01-01']})
    result = auto_dtype(df)
    assert pd.api.types.is_numeric_dtype(result['A'])
    assert pd.api.types.is_datetime64_any_dtype(result['B'])
