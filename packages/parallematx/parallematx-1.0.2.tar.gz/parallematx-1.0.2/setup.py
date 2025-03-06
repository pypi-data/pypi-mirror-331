from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="parallematx",
    version="1.0.2",
    description="Parallel Matrix Multiplication with ProcessPoolExecutor",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jackyzaz/ParallelMatX",
    author="Jackyzaz",
    author_email="soravit.sukkarn@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["bson >= 0.5.10"],
    python_requires=">=3.10",
)
