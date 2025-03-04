from setuptools import setup, find_packages

setup(
    name="bunnycdn-storage-handler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "aiohttp>=3.8.0",  # For async support
        "tqdm>=4.65.0",  # For progress bars
    ],
    author="Ahmed Waleed",
    author_email="work@ahmedwaleed.net",
    description="A Python client for BunnyCDN Storage API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ahmedwaleed22/bunnycdn-storage-handler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 