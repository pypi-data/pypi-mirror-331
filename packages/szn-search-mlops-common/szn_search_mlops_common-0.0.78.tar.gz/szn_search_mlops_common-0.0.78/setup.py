from setuptools import setup, find_packages

setup(
    name="szn-search-mlops-common",
    version="0.0.78",
    packages=find_packages(),
    description="Common utilities for MLOps applications, including tracking functionality.",
    author="Pen Test",
    author_email="test.skvara@seznam.cz",
    url="https://example.com/szn-search-mlops-common",
    entry_points={
        "console_scripts": [
            "szn_search_mlops_common=szn_search_mlops_common:main",
        ],
    },
)
