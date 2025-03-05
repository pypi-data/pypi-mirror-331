from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="vouchervision-go-client",
    version="0.1.2",
    author="Will",
    author_email="willwe@umich.edu",
    description="Client for VoucherVisionGO API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gene-Weaver/VoucherVisionGO-client",
    project_urls={
        "Bug Tracker": "https://github.com/Gene-Weaver/VoucherVisionGO/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    py_modules=["client"],  # Use py_modules for single file modules
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "pandas",
        "termcolor",
        "tabulate",
        "tqdm",
    ],
    entry_points={
        "console_scripts": [
            "vouchervision=client:main",  # Changed to point to client.py in root
        ],
    },
)