from setuptools import setup, find_packages

setup(
    name="dbuper",  # Your package name
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
        "click",
        "dropbox",
        "boto3",
        "pydrive2",
        "python-crontab"
    ],
    entry_points={
        'console_scripts': [
            'dbuper=dbuper:cli',
        ],
    },
)
