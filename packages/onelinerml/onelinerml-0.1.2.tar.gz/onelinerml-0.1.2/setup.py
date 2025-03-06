from setuptools import setup, find_packages

setup(
    name="onelinerml",
    version="0.1.2",
    description="A one-liner ML training and deployment library",
    author="Alexis Jean Baptiste",
    author_email="your.email@example.com",
    url="https://github.com/alexiisjbaptiste/easyml",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "scikit-learn",
        "xgboost",
        "fastapi",
        "uvicorn",
        "joblib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
