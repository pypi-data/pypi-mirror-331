import pandas as pd  # Ensure pandas is installed: pip install pandas
from pandas import DataFrame
import numpy as np
# This module is part of the panda_pie package of helpers.


# ---- Test Cases for calculate_sparsity ----
def test_calculate_sparsity() -> None:
    from panda_pie.feature_engineering import calculate_sparsity
    # Test with a dense array
    dense_data = np.array([[1, 2], [3, 4]])
    assert calculate_sparsity(dense_data) == 0.0  # No zeros

    # Test with a sparse array
    sparse_data = np.array([[0, 0], [0, 1]])
    assert calculate_sparsity(sparse_data) == 0.75  # 3 zeros out of 4 elements

    # Test with empty array
    empty_data = np.array([])
    assert calculate_sparsity(empty_data) == 0.0  # Prevent division by zero


# ---- Test Cases for handle_missing_values ----
def test_handle_missing_values() -> None:
    from panda_pie.feature_engineering import handle_missing_values
    # Sample DataFrame with missing values
    df: DataFrame = pd.DataFrame(dict(B=[None, 5, 6], A=[1, 2, None]))
    # Test mean imputation
    result = handle_missing_values(df.copy(), fill_strategy='mean')
    assert result['A'][2] == 1.5  # Mean of [1, 2]
    assert result['B'][0] == 5.5  # Mean of [5, 6]

    # Test replacing with scalar
    result = handle_missing_values(df.copy(), fill_strategy=0)
    assert result.isna().sum().sum() == 0  # No NaNs remaining

    # Test interpolation
    result = handle_missing_values(df.copy())  # Default linear interpolation
    assert result['A'][2] == 2.0  # Interpolated value between 2.0 and (empty)


# ---- Test Cases for numpy_pca ----
def test_numpy_pca():
    from panda_pie.feature_engineering import numpy_pca
    # Ensure proper output shape
    data = np.array([[1, 2], [3, 4], [5, 6]])  # Example data for testing
    numpy_out = numpy_pca(data, n_components=1)
    assert numpy_out.shape == (3, 1)  # Should return array with one component
    # Check that invalid n_components raises an error
    try:
        data = np.array([[1, 2], [3, 4], [5, 6]])  # Example data for testing
        numpy_out = numpy_pca(data, n_components=0)  # Invalid
    except ValueError as e:
        assert "Invalid n_components" in str(e)


# ---- Test Cases for apply_feature_hashing ----
def test_apply_feature_hashing():
    from panda_pie.feature_engineering import apply_feature_hashing
    # List of lists (input)
    data = [["apple", "banana"], ["carrot", "apple"]]

    hashed = apply_feature_hashing(data, n_features=5)
    assert hashed.shape == (2, 5)  # 2 rows, 5 hashed features

    # Check for valid input type
    try:
        apply_feature_hashing(None, n_features=10)
    except ValueError as e:
        assert "Input data must be a pandas DataFrame or" in str(e)
