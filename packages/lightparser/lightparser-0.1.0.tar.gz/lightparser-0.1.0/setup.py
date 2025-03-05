from setuptools import setup, find_packages

setup(
    name="lightparser",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["lxml"],
    entry_points={"console_scripts": ["lightparser=lightparser.output:setup_output"]},
    description="A lightweight parser with XPath support, Scrapy-like Items, and flexible output options.",
    author="Abdul Nazar",
    author_email="nazaradn@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
