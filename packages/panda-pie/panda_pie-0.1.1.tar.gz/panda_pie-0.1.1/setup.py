from setuptools import setup, find_packages

setup(
    name="panda_pie",
    version="0.1.1",
    description="A Python library for simplifying ML workflows",
    author="David",
    url="https://github.com/David-Barnes-Data-Imaginations/panda_pie",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "scipy",
    ],
    extras_require = {
        'full': ['faker', 'imbalanced-learn', 'pyarrow', 'umap-learn'],
        "dev": [
            "pytest",
            "pip",
        ],
    },
)


