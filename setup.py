import os
import re
from setuptools import setup, find_packages

# Function to read the version
def get_version():
    version_file = os.path.join("dbuper", "__init__.py")
    with open(version_file) as f:
        for line in f:
            match = re.match(r"^__version__ = ['\"]([^'\"]*)['\"]", line)
            if match:
                return match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
 name="dbuper",
    version=get_version(),
    description="A tool for automated database backups and scheduling.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Josiah Ben",
    author_email="benjosiah90@gmail.com",
    url="https://github.com/benjosiah/dbuper",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "dropbox",
        "boto3",
        "pydrive2",
        "python-crontab",
        "setuptools"
    ],
    entry_points={
        'console_scripts': [
            'dbuper=dbuper.dbuper:cli',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
