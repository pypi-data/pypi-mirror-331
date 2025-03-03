from setuptools import setup, find_packages

setup(
    name="urlf",
    version="1.1",
    author="Bobby",
    author_email="rule-entry-0d@icloud.com",
    description="A script to remove duplicate URLs based on query parameters and base URL.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Boopath1/urlf",  # Replace with your repo
    packages=find_packages(),
    install_requires=[
        "art",
        "colorlog",
        "tqdm"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "urlf=urlf.urlf:main"
        ]
    },
    python_requires=">=3.6",
)