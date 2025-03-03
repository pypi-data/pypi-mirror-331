from setuptools import setup, find_packages

setup(
    name="jsbucket",
    version="1.0.2",
    author="Mortaza Behesti Al Saeed",
    author_email="saeed.ctf@gmail.com",
    description="A tool to discover S3 buckets from subdomains by analyzing JavaScript files.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/saeed0xf/jsbucket",
    packages=find_packages(),
    install_requires=[
        "requests",
        "tqdm",
        "rich",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version required
    entry_points={
        "console_scripts": [
            "jsbucket=jsbucket.jsbucket:main",  # Allows users to run the tool as `jsbucket` from the CLI
        ],
    },
)