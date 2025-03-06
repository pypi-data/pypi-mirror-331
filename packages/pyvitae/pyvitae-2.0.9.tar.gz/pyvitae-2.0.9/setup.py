import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyvitae",
    version="2.0.9",
    author="Jin-Hong Du",
    author_email="jinhongd@andrew.cmu.edu",
    packages=["VITAE"],
    description="Joint Trajectory Inference for Single-cell Genomics Using Deep Learning with a Mixture Prior",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaydu1/VITAE",
    install_requires=[
        "tensorflow >= 2.4",
        "tensorflow_probability >= 0.12",
        "pandas", 
        "jupyter", 
        "umap-learn >= 0.5.0", 
        "matplotlib", 
        "numpy ==1.23",
        "numba", 
        "seaborn", 
        "leidenalg", 
        "scikit-learn",
        "networkx",
        "statsmodels",
        "scanpy>=1.9.2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)