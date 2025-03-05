import pandas as pd
from tidyflow.preprocessing.clean_missing import clean_missing

def test_clean_missing():
    df = pd.DataFrame({
        'A': [1, 2, None, 4],  # Numerical column
        'B': [None, 'cat', 'dog', 'mouse']  # Categorical column
    })

    # Apply the function
    result = clean_missing(df, strategy='mode')  # Mode fills both numeric and categorical

    # Assert no missing values
    assert result.isnull().sum().sum() == 0, f"Expected 0 missing values, found {result.isnull().sum().sum()}"
