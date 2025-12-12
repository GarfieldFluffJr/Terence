from setuptools import setup, find_packages

setup(
    # Package metadata
    name="terence",
    version="0.1.0",
    author="GarfieldFluffJr",
    author_email="louieyin6@gmail.com",
    description="Terence is a Python package that makes it easy to scan and analyze GitHub repositories. It simplifies the GitHub API and processes the repo contents into a simple flat dictionary that can be accessed by file path.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/GarfieldFluffJr/Terence",

    # Package discovery
    packages=find_packages(exclude=["tests", "tests.*"]),

    # Dependencies required to run the package
    install_requires=[
        "PyGithub>=2.1.1",
        "python-dotenv>=1.0.0",
    ],

    # Optional dependencies for development
    extras_require={
        "dev": [
            "pytest>=7.4.0",
        ]
    },

    # Python version requirement
    python_requires=">=3.8",

    # Package classifiers (helps users find your package on PyPI)
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control :: Git",
    ],

    # Keywords for PyPI search
    keywords="github api repository scanner code-analysis git python content decode",

    # Project URLs
    project_urls={
        "Source": "https://github.com/GarfieldFluffJr/Terence",
        "Documentation + Support": "https://github.com/GarfieldFluffJr/Terence#readme",
    },
)
