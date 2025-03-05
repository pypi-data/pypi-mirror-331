from setuptools import setup, find_packages

setup(
    name="iimi",
    version="0.1.11",
    description="identifying plant infection with machine intelligence.",
    keywords="bioinformatics, plant-virus, machine-learning, diagnostics",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license='MIT',
    author="Jaspreet S",
    url="https://github.com/jaspreetks/iimi",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "joblib",
        "xgboost",
        "pysam",
    ],
    include_package_data=True,
    package_data={
        'iimi.data': ['*.pkl', '*.model'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
