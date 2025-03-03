# main.py

"""Entry point for package execution."""

import pandas as pd
from tidyflow import (
    clean_missing,
    encode_categoricals,
    scale_features,
    feature_engineer,
    handle_outliers,
    auto_dtype,
    suggest_pipeline,
    build_pipeline
)


def main():
    """Example usage of TidyFlow package."""
    df = pd.DataFrame({
        'A': [1, 2, None, 4],
        'B': ['cat', 'dog', 'mouse', None],
        'C': [100, 200, 300, 400]
    })

    print("Original DataFrame:")
    print(df)

    df = clean_missing(df)
    df = encode_categoricals(df)
    df = scale_features(df)
    df = feature_engineer(df, method='poly', degree=2)
    df = handle_outliers(df)
    df = auto_dtype(df)
    suggestions = suggest_pipeline(df)
    pipeline = build_pipeline(df)

    print("Processed DataFrame:")
    print(df)
    print("Suggestions:", suggestions)


if __name__ == "__main__":
    main()
