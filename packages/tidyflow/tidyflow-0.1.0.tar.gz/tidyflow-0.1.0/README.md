# README.md

# TidyFlow: A Lightweight Data Preprocessing Toolbox

TidyFlow is a Python package designed to simplify and streamline data preprocessing. It provides modular, user-friendly functions for cleaning, encoding, scaling, and transforming data, making it easier for data scientists and machine learning practitioners to prepare datasets efficiently.

## Features
✅ **Modular & Customizable** – Use functions independently or build a full pipeline.
✅ **Automated Smart Suggestions** – Guides users on best preprocessing practices.
✅ **Seamless Integration** – Works with Pandas & Scikit-learn pipelines.
✅ **Scalability** – Designed to support additional preprocessing techniques in the future.

## Installation
```sh
pip install tidyflow
```

## Usage
```python
import pandas as pd
from tidyflow import clean_missing, encode_categoricals, scale_features, feature_engineer, handle_outliers, auto_dtype, suggest_pipeline, build_pipeline

df = pd.DataFrame({
    'A': [1, 2, None, 4],
    'B': ['cat', 'dog', 'mouse', None],
    'C': [100, 200, 300, 400]
})

df = clean_missing(df)
df = encode_categoricals(df)
df = scale_features(df)
df = feature_engineer(df, method='poly', degree=2)
df = handle_outliers(df)
df = auto_dtype(df)
suggestions = suggest_pipeline(df)
pipeline = build_pipeline(df)
```

## License
This project is licensed under the MIT License.
