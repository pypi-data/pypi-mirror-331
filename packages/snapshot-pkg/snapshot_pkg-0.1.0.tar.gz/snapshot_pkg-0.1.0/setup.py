from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snapshot_pkg",
    version="0.1.0",
    author="Baptiste FERRAND",
    author_email="bferrand.maths@gmail.com",
    description="A utility to create, manage, and restore snapshots of Python packages and directory structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B4PT0R/snapshot_pkg",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pathspec",
    ],
    entry_points={
        "console_scripts": [
            "snapshot-pkg=snapshot_pkg.__main__:main",
        ],
    },
    keywords="snapshot, backup, restore, versioning, documentation, ai-collaboration, development-tools",
    project_urls={
        "Bug Reports": "https://github.com/B4PT0R/snapshot_pkg/issues",
        "Source": "https://github.com/B4PT0R/snapshot_pkg",
    },
)