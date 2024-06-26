from setuptools import find_packages, setup

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("VERSION", "r", encoding="utf-8") as f:
    version = f.read()

setup(
    name="sportsipy",
    version=version,
    author="Robert Clark",
    author_email="robdclark@outlook.com",
    description="A free sports API written for python",
    long_description=long_description,
    license="MIT",
    url="https://github.com/roclark/sportsipy",
    packages=find_packages(),
    python_requires=">=3.7",
    keywords="stats sports api sportsipy machine learning",
    install_requires=[
        "numpy >= 2.0.0",
        "pandas >= 2.2.2",
        "pyquery >= 2.0.0",
        "requests >= 2.32.3",
    ],
    classifiers=(
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ),
)
