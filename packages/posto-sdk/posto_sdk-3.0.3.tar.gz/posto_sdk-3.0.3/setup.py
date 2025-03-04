from setuptools import setup, find_packages

setup(
    name="posto-sdk",
    version="3.0.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
        "python-dateutil",  # For advanced date parsing
        "pytz",            # For timezone handling
        "tzlocal",            # For detecting local timezone
    ],
    python_requires=">=3.6",  # Specify minimum Python version
    author="Your Name",
    author_email="your.email@example.com",
    description="Posto SDK for social media management",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/posto-sdk",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)

