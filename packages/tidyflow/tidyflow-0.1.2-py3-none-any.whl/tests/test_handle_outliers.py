# tests/test_handle_outliers.py
import pandas as pd
import pytest
from tidyflow.preprocessing.handle_outliers import handle_outliers

def test_handle_outliers():
    df = pd.DataFrame({'A': [1, 2, 100, 3, 4]})
    result = handle_outliers(df, method='iqr', strategy='clip')
    assert result['A'].max() < 100
