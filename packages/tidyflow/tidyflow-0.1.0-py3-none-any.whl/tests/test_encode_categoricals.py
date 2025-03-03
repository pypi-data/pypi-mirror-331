# tests/test_encode_categoricals.py
import pandas as pd
import pytest
from tidyflow.preprocessing.encode_categoricals import encode_categoricals

def test_encode_categoricals():
    df = pd.DataFrame({'Category': ['A', 'B', 'A', 'C']})
    result = encode_categoricals(df, method='onehot')
    assert 'Category_B' in result.columns and 'Category_C' in result.columns
