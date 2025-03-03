from setuptools import setup, find_packages
from pathlib import Path

VERSION = '0.1.0'
DESCRIPTION = 'Pathik - Advanced web path discovery tool'

# Read long description from README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="pathik",
    version=VERSION,
    author="Rach Pradhan",
    author_email="me@rachit.ai",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'requests',
        'beautifulsoup4',
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'pathik=pathik.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
    ],
    python_requires='>=3.6',
    include_package_data=True,
)