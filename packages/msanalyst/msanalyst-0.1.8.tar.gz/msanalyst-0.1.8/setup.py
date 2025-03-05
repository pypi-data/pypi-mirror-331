import os
import zipfile
import requests
from setuptools import setup, find_packages


setup(
    name="msanalyst",
    version="0.1.8",
    author="Wenchao Yu",
    author_email="2540856059@qq.com",
    description="A tool for molecular networking and annotation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/WenchYu/MSanalyst",
    packages=find_packages(),
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "msanalyst-main=msanalyst.main:main",
            "msanalyst-mn_merging=msanalyst.mn_merging:mn_merging",
            "msanalyst-customized_db=msanalyst.customized_db:customized_db",
            "msanalyst-ms2search=msanalyst.ms2search:ms1search",
            "msanalyst-ms1search=msanalyst.ms1search:ms2search",
            "msanalyst-re_networking=msanalyst.re_networking:re_networking",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
)