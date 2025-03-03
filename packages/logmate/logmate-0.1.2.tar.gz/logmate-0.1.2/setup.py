from setuptools import setup, find_packages

setup(
    name="logmate",
    version="0.1.2",  # Increment version for the new release
    author="Atul Verma",
    author_email="atul.sv@icloud.com",
    description="A smart log management tool with rich text output, filtering, and export options.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Verma-Labs/logmate",
    packages=find_packages(),
    install_requires=[
        "rich",  # For rich-text logging
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "logmate=logmate.logmate:main",  # <--- This makes `logmate` a CLI command
        ],
    },
)
