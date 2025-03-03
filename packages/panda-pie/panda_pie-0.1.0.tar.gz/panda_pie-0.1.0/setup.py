from setuptools import setup, find_packages

setup(
    name="panda_pie",
    version="0.1.0",  # This must exactly match the version specified in meta.yaml.
    description="A Python library for simplifying ML workflows",
    author="David",
    url="https://github.com/David-Barnes-Data-Imaginations/panda_pie",
    packages=find_packages(),
    install_requires=[
        "numpy==1.23.5",
        "pandas==2.2.3",
        "scikit-learn==1.6.1",
        "scipy==1.15.1",
        "pyarrow==19.0.0",
        "umap-learn==0.5.4",
        "faker==30.8.1",
        "pytest==8.3.4"
    ],
)

