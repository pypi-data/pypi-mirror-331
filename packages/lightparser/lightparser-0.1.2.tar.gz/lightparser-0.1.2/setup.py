from setuptools import setup, find_packages
import pathlib

# Read the README file
HERE = pathlib.Path(__file__).parent
LONG_DESCRIPTION = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="lightparser",
    version="0.1.2",
    packages=find_packages(),
    install_requires=["lxml"],
    entry_points={"console_scripts": ["lightparser=lightparser.output:setup_output"]},
    description="A lightweight parser with XPath support, Scrapy-like Items, and flexible output options.",
    long_description=LONG_DESCRIPTION,  # Add this
    long_description_content_type="text/markdown",  # Specify Markdown format
    author="Abdul Nazar",
    # author_email="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
