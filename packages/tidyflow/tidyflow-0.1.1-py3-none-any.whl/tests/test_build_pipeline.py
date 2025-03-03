# tests/test_build_pipeline.py
import pandas as pd
import pytest
from tidyflow.preprocessing.build_pipeline import build_pipeline

def test_build_pipeline():
    df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})
    pipeline = build_pipeline(df)
    assert pipeline is not None
