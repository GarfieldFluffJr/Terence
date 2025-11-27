from setuptools import setup, find_packages

setup(
    # Package metadata
    name="terrence",
    version="0.1.0",
    author="GarfieldFluffJr",  # Update with your name
    author_email="louieyin6@gmail.com",  # Update with your email
    description="Give Terrence your GitHub developer token and a public GitHub repo url and he will tell you everything that repo",
    long_description=open("LICENSE").read() if open("LICENSE").read() else "",
    long_description_content_type="text/plain",
    url="https://github.com/GarfieldFluffJr/Terrence",  # Update with your GitHub URL

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

    # Package classifiers (optional, for PyPI)
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
