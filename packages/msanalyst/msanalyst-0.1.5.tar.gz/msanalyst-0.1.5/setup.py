import os
import zipfile
import requests
from setuptools import setup, find_packages


MSDB_URL = "https://drive.google.com/file/d/1w6HF3w1KIJlTz_QaVqqtN1BzkGDhDgzw/view?usp=sharing"
MSDB_ZIP = "msdb.zip"
MSDB_DIR = "msanalyst/msdb"

def download_and_extract_msdb():
    # 如果 msdb 文件夹已经存在，跳过下载
    if os.path.exists(MSDB_DIR):
        print(f"{MSDB_DIR} already exists. Skipping download.")
        return

    print("Downloading msdb.zip...")
    response = requests.get(MSDB_URL)
    response.raise_for_status()  # 确保下载成功

    # 保存下载的文件
    with open(MSDB_ZIP, "wb") as f:
        f.write(response.content)

    print("Extracting msdb.zip...")
    with zipfile.ZipFile(MSDB_ZIP, "r") as zip_ref:
        zip_ref.extractall("msanalyst/")

    os.remove(MSDB_ZIP)
    print("msdb.zip extracted successfully.")

setup(
    name="msanalyst",
    version="0.1.5",
    author="Wenchao Yu",
    author_email="2540856059@qq.com",
    description="A tool for molecular networking and annotation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/WenchYu/MSanalyst",
    packages=find_packages(),  # 自动发现所有包
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