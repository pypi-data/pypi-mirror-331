# tests/test_suggest_pipeline.py
import pandas as pd
import pytest
from tidyflow.preprocessing.suggest_pipeline import suggest_pipeline

def test_suggest_pipeline():
    df = pd.DataFrame({'A': [None, None, 3, 4], 'B': [1, 2, 3, 4]})
    result = suggest_pipeline(df)
    assert any("missing values" in suggestion for suggestion in result)
