from setuptools import setup, find_packages

setup(
    name="mysql-connector-pkg",  # 你的包名（PyPI上唯一）
    version="0.1.0",
    author="easyconnectpkg",
    author_email="easyconnectpkg@gmail.com",
    description="A simple MySQL connector package",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/easyconnectpkg/mysql-connector-pkg",  # GitHub 仓库
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
