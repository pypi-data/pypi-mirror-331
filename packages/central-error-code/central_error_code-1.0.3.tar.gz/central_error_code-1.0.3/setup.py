from setuptools import setup, find_packages

setup(
    name="central-error-code",  # Use hyphens instead of underscores for PyPI
    version="1.0.3",            # Your version
    description="A module to handle error codes loaded from JSON files",  # Description
    author="Your Name",         # Your name
    author_email="your.email@example.com",  # Your email
    packages=find_packages(where='src'),  # Tell setuptools where to find packages
    package_dir={'': 'src'},         # Tells setuptools where the source code is
    install_requires=[              # Dependencies (if any)
        # 'requests',  # Example dependency
    ],
    include_package_data=True,      # Include non-Python files (like JSON)
    classifiers=[                   # PyPI classifiers
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
