import numpy as np
import pandas as pd

df = pd.DataFrame()

# ************************************************************
# My Python package, file 1 - Data_generation. To be added to the other 2 files and pertinent init & Setup.py
def load_iris_dataset_into_dataframe ():
    from sklearn.datasets import load_iris
    iris = load_iris()
    iris_dataframe = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    iris_dataframe['species'] = iris.target
    return iris_dataframe


def load_iris_data ():
    import sklearn.datasets
    iris = sklearn.datasets.load_iris()
    iris_data = iris.data
    iris_target = iris.target

    print(type(iris_data))  # It will show <class 'numpy.ndarray'>
    print(type(iris_target))  # It will show <class 'numpy.ndarray'>
    print(iris_data.shape)  # It will show (150, 4)
    print(iris_target.shape)  # It will show (150,)
    print(iris_data[0])  # It will show [5.1 3.5 1.4 0.2]
    print(iris_target[0])

    return iris_data, iris_target

# *****************************

def load_california_dataframe():
    from sklearn.datasets import fetch_california_housing

    calhouse = fetch_california_housing()
    calhouse_dataframe = pd.DataFrame(data=calhouse.data, columns=calhouse.feature_names)
    calhouse_dataframe['target'] = calhouse.target
    return calhouse_dataframe


# *****************************

def load_wine_dataframe():
    from sklearn.datasets import load_wine

    wino = load_wine()
    wino_dataframe = pd.DataFrame(data=wino.data, columns=wino.feature_names)
    wino_dataframe['target'] = wino.target
    return wino_dataframe


def generate_random_dataframe (num_rows, num_cols, random_state=42):
    """
    Generate a random dataframe with 'num_rows' rows and 'num_cols' columns.
    """
    np.random.seed(random_state)
    df = np.random.random((num_rows, num_cols))
    return pd.DataFrame(df)


# *****************************

# *******************************
#** Basic (but Efficient) Sparse Data Generation
#********************************
def generate_sparse_dataframe(num_rows, num_cols, sparsity, random_state=42):
    """
**      Generate a sparse dataframe with 'num_rows' rows and 'num_cols' columns, with given 'sparsity'.
** """
    from scipy.sparse import random as sparse_random
    sparse_matrix = sparse_random(num_rows, num_cols, density=1-sparsity, random_state=random_state, format='csr')
    return pd.DataFrame.sparse.from_spmatrix(sparse_matrix)


# *****************************

def generate_sparse_outliers_dataframe (num_rows, num_cols, sparsity, random_state=42):
    """
    Generate a sparse dataframe with 'num_rows' rows and 'num_cols' columns, with given 'sparsity'.
    """
    from scipy.sparse import random as sparse_random

    sparse_matrix = sparse_random(num_rows, num_cols, density=1-sparsity, random_state=random_state, format='coo')
    sparse_matrix[sparse_matrix > 0.9] = 1000000
    return pd.DataFrame.sparse.from_spmatrix(sparse_matrix)

# *****************************
def generate_random_outliers_dataframe (num_rows, num_cols, random_state=42):
    """
    Generate a random dataframe with 'num_rows' rows and 'num_cols' columns.
    """
    np.random.seed(random_state)
    df = np.random.random((num_rows, num_cols))
    df[df > 0.9] = 1000000
    return pd.DataFrame(df)


# *****************************

def generate_dataframe_with_missing_values (shape, sparsity, random_state=42):
    """
    Generate a dataframe with missing values of given 'shape', with given 'sparsity'.
    """
    np.random.seed(random_state)
    df = np.random.random(shape)
    df[df < sparsity] = np.nan
    return pd.DataFrame(df)

# *****************************

def generate_random_missing_outliers_dataframe (num_rows, num_cols, random_state=42):
    """
    Generate a random dataframe with 'num_rows' rows and 'num_cols' columns.
    """
    np.random.seed(random_state)
    df = np.random.random((num_rows, num_cols))
    df[df < 0.2] = np.nan
    df[df > 0.9] = 1000000
    return pd.DataFrame(df)

# ************************************************************

def generate_random_dataset(shape, random_state=42):
    """
    Generate a random dataset of given 'shape'.
    """
    np.random.seed(random_state)  # Ensure reproducibility
    return np.random.random(shape)


# ************************************************************

def generate_random_outliers_dataset(shape, outlier_value=1000000, random_state=42):
    """
    Generate a random dataset with outliers.

    Any value > 0.9 is set as an outlier (default: 1,000,000).
    """
    np.random.seed(random_state)  # Ensure reproducibility
    data = np.random.random(shape)
    data[data > 0.9] = outlier_value  # Allow customization of outlier values
    return data


# ************************************************************

def generate_dataset_with_missing_values(shape, sparsity, random_state=42):
    """
    Generate a dataset with missing values.

    Any value < sparsity is set to NaN.
    """
    np.random.seed(random_state)  # Ensure reproducibility
    data = np.random.random(shape)
    data[data < sparsity] = np.nan
    return data


# ************************************************************

def generate_random_missing_outliers_dataset(shape, missing_threshold=0.2, outlier_threshold=0.9, outlier_value=1000000,
                                             random_state=42):
    """
    Generate a random dataset with missing values and outliers.

    Any value < missing_threshold is set to NaN.
    Any value > outlier_threshold is set as an outlier (default: 1,000,000).
    """
    np.random.seed(random_state)  # Ensure reproducibility
    data = np.random.random(shape)
    data[data < missing_threshold] = np.nan
    data[data > outlier_threshold] = outlier_value  # Allow customization of outlier values
    return data

# ****************************

# *******************************
#** ML Data Generation - Sklearn’s Synthetic Dataset Generators
#********************************


def generate_classification(num_samples: int, num_features: int, num_classes: int, random_state: int = 42) -> tuple[
    np.ndarray, np.ndarray]:
    """
    Generate a synthetic classification dataset with given parameters. The function internally uses
    `make_sparse_coded_signal` to create the dataset. The generated dataset includes feature data
    and corresponding target labels.

    :param num_samples: The number of data samples to generate.
    :param num_features: The number of features for each sample.
    :param num_classes: The number of distinct classes in the target labels.
    :param random_state: Random state for reproducibility. Defaults to 42.
    :return: A tuple containing the feature dataset as a numpy ndarray and
             the target labels as a numpy ndarray.
    """
    from sklearn.datasets import make_sparse_coded_signal
    x, y = make_sparse_coded_signal(n_samples=num_samples, n_components=num_features, n_features=num_classes,
                                    random_state=random_state)
    return x, y


def generate_classification_dataset(n_samples: int, n_features: int, n_classes: int, random_state: int = 42) -> tuple[
    pd.DataFrame, pd.Series]:
    """
    Generate a synthetic classification dataset.

    This function generates a randomly created classification dataset that is
    commonly used for tasks like testing and benchmarking machine learning
    algorithms. The dataset contains a specified number of samples, features,
    and classes, as well as a random state for reproducibility.

    :param n_samples: The total number of samples in the dataset.
    :type n_samples: int
    :param n_features: The total number of features for each sample.
    :type n_features: int
    :param n_classes: The total number of distinct classes in the dataset.
    :type n_classes: int
    :param random_state: The random seed for reproducibility.
        Default value is 42.
    :type random_state: int
    :return: A tuple where the first element is an array of feature data
        of shape `(n_samples, n_features)` and the second element is an
        array of labels of shape `(n_samples,)`.
    :rtype: tuple
    """
    from sklearn.datasets import make_classification

    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=int(n_features * 0.6),  # % of informative features
        n_classes=n_classes,
        flip_y=0.01,  # Add slight label noise
        random_state=random_state
    )
    return pd.DataFrame(X), pd.Series(y)


def generate_regression_dataset(
        n_samples: int,
        n_features: int,
        random_state: int = 42
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Generates a synthetic regression dataset comprising input features and target values.

    The function creates a dataset suitable for training and testing regression models
    by producing a specified number of features and samples. A random seed can be
    provided for reproducibility.

    :param n_samples: The number of samples (rows) in the dataset.
    :type n_samples: int
    :param n_features: The number of features (columns) in the dataset.
    :type n_features: int
    :param random_state: The seed for random number generation, default is 42.
    :type random_state: int
    :return: A tuple containing a DataFrame of features and a Series of target values.
    :rtype: tuple[pd.DataFrame, pd.Series]
    """
    from sklearn.datasets import make_regression

    X, y = make_regression(
        n_samples=n_samples,
        n_features=n_features,
        noise=10.0,  # Inject some noise
        random_state=random_state
    )
    return pd.DataFrame(X), pd.Series(y)


def generate_blobs_dataset(
        n_samples: int, n_features: int, n_clusters: int, random_state: int = 42
) -> tuple[pd.DataFrame, pd.Series]:

    """
    Clustering Data: Useful for creating well-separated clusters,
    typically used for unsupervised learning tasks like k-means clustering etc.
    :rtype: object
    """
    from sklearn.datasets import make_blobs

    X, y = make_blobs(
        n_samples=n_samples,
        n_features=n_features,
        centers=n_clusters,
        random_state=random_state
    )
    return pd.DataFrame(X), pd.Series(y)

# Manifold Learning / Non-Linear Datasets
# Semi-complex 2D datasets often used for visualization tasks or testing algorithms’
# ability to separate non-linear classes.




def generate_moons_dataset(n_samples, noise=0.1, random_state=42):
    """
    Generates a two-dimensional dataset in the shape of two interleaving moons.
    This function is commonly used for demonstrating the performance of machine
    learning algorithms, especially in classification tasks. It allows control
    over the number of samples, the level of noise added to the data, and the
    random seed for reproducibility.

    :param n_samples: Number of data points to generate.
    :type n_samples: int
    :param noise: Standard deviation of Gaussian noise applied to the data.
    :type noise: float, optional
    :param random_state: Seed for the random number generator (for reproducibility).
    :type random_state: int, optional
    :return: Tuple containing the features array (X) and target labels array (y).
    :rtype: tuple(numpy.ndarray, numpy.ndarray)
    """
    from sklearn.datasets import make_moons

    X, y = make_moons(n_samples=n_samples, noise=noise, random_state=random_state)
    return pd.DataFrame(X), pd.Series(y)

def generate_circles_dataset(n_samples, noise=0.1, random_state=42):
    """
    Generates a synthetic dataset of points in the shape of concentric circles.
    This function creates a two-dimensional dataset consisting of points arranged
    in two concentric circles. The circles may be perturbed with Gaussian noise
    to make them less regular. It is commonly used for testing clustering or
    classification algorithms.

    :param n_samples: Number of samples to generate, which must be an integer. The
        total number of generated data points will be equal to this value.
    :param noise: Standard deviation of Gaussian noise added to the data. Must be
        a non-negative float or integer.
    :param random_state: Determines random number generation for dataset shuffling
        and noise. Use an integer for reproducibility, or None for random behavior.
    :return: A tuple containing two elements. The first is a 2D NumPy array of shape
        (n_samples, 2) containing the generated points. The second is a 1D NumPy
        array of length n_samples containing labels (0 or 1) for each point,
        indicating on which circle the point lies.
    :rtype: tuple(numpy.ndarray, numpy.ndarray)
    """
    from sklearn.datasets import make_circles

    X, y = make_circles(n_samples=n_samples, noise=noise, random_state=random_state)
    return pd.DataFrame(X), pd.Series(y)

#******************************
#*** Custom Data Generators for ML Applications
#*****************************

# Generate Time-Series Datasets - Ideal for testing algorithms for trend detection,
# anomaly detection, or forecasting.

def generate_time_series(n_samples, n_features, noise=0.1, random_state=42):
    """
    Generates a synthetic time series dataset with specified number of samples,
    features, noise, and random seed. The time series is useful for experiments
    and modeling, providing controlled variability in data.

    :param n_samples: The number of samples (timesteps) in the generated time
        series dataset.
    :type n_samples: int
    :param n_features: The number of features (dimensions) for each sample in
        the time series.
    :type n_features: int
    :param noise: The standard deviation of Gaussian noise added to the data
        for variability. Default is 0.1.
    :type noise: float, optional
    :param random_state: Determines the random seed for reproducibility.
        Default is 42. Use an integer for consistent outputs,
        or None for true randomness.
    :type random_state: int, optional
    :return: A tuple containing two numpy arrays - the generated time series
        data of shape (n_samples, n_features) and the target labels or values
        associated with the dataset if applicable.
    :rtype: Tuple[numpy.ndarray, numpy.ndarray]
    """
    np.random.seed(random_state)
    data = np.sin(np.linspace(0, 20, n_samples)).reshape(-1, 1)  # Sinusoidal trend
    noise_matrix = np.random.random((n_samples, n_features)) * noise
    timeseries = np.hstack([data] * n_features) + noise_matrix
    assert isinstance(timeseries, object)

    return pd.DataFrame(timeseries)

def generate_sparse_correlated_dataset(n_samples, n_features, sparsity, correlation_factor=0.7, random_state=42):
    """
    Generates a sparse correlated dataset suitable for various machine learning and
    statistical tasks. Sparse datasets contain a large proportion of zero values,
    making them efficient for storage and computation. The correlation between
    features is controlled, enabling experiments with multicollinearity.

    The function creates a dataset where samples are independently generated, and
    features are structured to include sparsity (presence of many zero values)
    while maintaining inter-feature correlations.

    :param n_samples:
        The number of samples (rows) in the generated dataset.

    :param n_features:
        The number of features (columns) in the generated dataset.

    :param sparsity:
        The fraction of zero values in the dataset. Must be a value between 0 and 1,
        where 0 represents no sparsity and 1 means all values are zero.

    :param correlation_factor:
        A float value indicating the degree of correlation between features.
        Defaults to 0.7. Higher values indicate stronger positive correlation, with
        1 representing complete correlation.

    :param random_state:
        Random seed for reproducibility. Accepts an integer or None. Default value
        is 42.

    :return:
        A tuple containing:
        - A NumPy array with shape (n_samples, n_features), representing the
          generated dataset. The array will include sparse and correlated features.
        - A NumPy array representing the labels (or target values) corresponding to
          generated data.
    """

    np.random.seed(random_state)
    base = np.random.random(n_samples)
    data = np.array([base + np.random.random(n_samples) * (1 - correlation_factor) for _ in range(n_features)]).T
    data[data < sparsity] = 0  # Apply sparsity
    return pd.DataFrame(data)


  # Datasets for Natural Language Processing (NLP)



def generate_fake_text_dataset(n_samples):
    # Ensure the 'faker' library is installed. If not, install it using:
    # pip install faker
    from faker import Faker
    fake = Faker()
    text_data = [fake.sentence() for _ in range(n_samples)]
    return pd.DataFrame(text_data, columns=['text'])

# TF-IDF Sparse Matrices - Directly create sparse representations for NLP tasks.
from pandas import DataFrame

def generate_tfidf_matrix(corpus) -> DataFrame:
    """
    Generates a TF-IDF matrix for a given corpus using sklearn's TfidfVectorizer and
    returns it as a sparse DataFrame.

    The method uses the TfidfVectorizer to compute the Term Frequency-Inverse Document
    Frequency (TF-IDF) scores for all terms in the provided textual corpus. The resulting
    matrix is transformed into a pandas sparse DataFrame with terms as columns.

    :param corpus: A list of strings where each string represents a document in the text corpus.
                   The TF-IDF matrix will encode the frequency and importance of terms from
                   this corpus.
    :type corpus: list[str]
    :return: A sparse DataFrame where rows represent documents, columns represent terms,
             and values store the TF-IDF weight of the respective term for the document.
    :rtype: pandas.DataFrame
    """
    from sklearn.feature_extraction.text import TfidfVectorizer

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return pd.DataFrame.sparse.from_spmatrix(tfidf_matrix, columns=vectorizer.get_feature_names_out())

# Kaggle API integration to fetch
# competition datasets: [https://github.com/Kaggle/kaggle-api](https://github.com/Kaggle/kaggle-api).



# ************************************************************


