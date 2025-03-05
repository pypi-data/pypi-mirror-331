import setuptools

setuptools.setup(
    name="file-io-utilities",
    version="0.0.14",
    author="Alida research team",
    author_email="salvatore.cipolla@eng.it",
    description="Utils for file IO operations in Alida.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires = [
        "hdfs>=2.0.0",
        "boto3>=1.17.92",
        "requests>=2.22.0",
        "alida-arg-parser>=0.0.21"
        ],
)
