from setuptools import setup, find_packages

setup(
    name="mkdocs-author-plugin",
    version="0.1.0",
    description="Add manually defined authors to MkDocs pages.",
    author="Jakob Klotz",
    author_email="jakob.klotz@mci.edu",
    url="https://github.com/mciwing/mkdocs-author-plugin",
    packages=find_packages(),
    install_requires=["mkdocs>=1.6.1", "pyyaml"],
    python_requires=">=3.11,<3.13",
    entry_points={
        "mkdocs.plugins": [
            "authors = mkdocs_author_plugin.plugin:AuthorsPlugin",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
    ],
)
