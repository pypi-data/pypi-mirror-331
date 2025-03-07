from setuptools import setup, find_packages

setup(
    name="central_error_codes",  # The name of your module
    version="1.0.2",            # The version of your package
    description="A module to handle error codes loaded from JSON files",  # Description
    author="Your Name",         # Your name
    author_email="your.email@example.com",  # Your email
    packages=find_packages(where='src'),  # Specify the source folder for packages
    package_dir={'': 'src'},         # Tells setuptools where the source code is
    install_requires=[              # Dependencies (if any)
        # 'requests',  # Example dependency
    ],
    include_package_data=True,      # Ensure non-Python files like JSON are included
    classifiers=[                   # Classifiers for PyPI (optional)
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
