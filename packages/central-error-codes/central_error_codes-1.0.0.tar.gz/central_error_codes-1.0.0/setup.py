from setuptools import setup, find_packages

setup(
    name="central-error-codes",  # Package name
    version="1.0.0",             # Version
    packages=find_packages(where="src/python"),  # Find Python packages in src/python
    package_dir={"": "src/python"},  # Specify the root of the Python source code
    include_package_data=True,   # Include non-Python files (e.g., JSON)
    package_data={
        "your_module": ["../errors/*.json"],  # Include JSON files
    },
    install_requires=[],         # List of dependencies (if any)
    author="Your Name",
    author_email="your.email@example.com",
    description="A centralized error code library for microservices",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/central-error-codes",  # Project URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",     # Python version requirement
)