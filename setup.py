from setuptools import setup, find_packages

setup(
    name="valetia",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "spacy",
        "loguru",
        "pandas",
        "pypdf2",
        "python-docx",
        "openpyxl",
    ],
)
