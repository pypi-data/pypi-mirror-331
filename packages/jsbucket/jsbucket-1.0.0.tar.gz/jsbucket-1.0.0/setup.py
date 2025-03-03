from setuptools import setup, find_packages

setup(
    name="jsbucket",  # Name of your package (must be unique on PyPI)
    version="1.0.0",  # Version number (use semantic versioning: MAJOR.MINOR.PATCH)
    author="Mortaza Behesti Al Saeed",  # Your name or organization
    author_email="saeed.ctf@gmail.com",  # Your email
    description="A tool to discover S3 buckets from subdomains by analyzing JavaScript files.",
    long_description=open("README.md", encoding="utf-8").read(),  # Long description from README.md
    long_description_content_type="text/markdown",  # Specify Markdown format
    url="https://github.com/saeed0xf/jsbucket",  # Link to your repository
    packages=find_packages(),  # Automatically find packages in your project
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