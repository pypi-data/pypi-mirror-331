from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pd_to_sheet",  # 包名（PyPI 中唯一，不能重复）
    version="1.0.0",  # 版本号（遵循语义化版本规范）
    author="sgg",
    author_email="police@foxmail.com",
    description="一个将pandas数据框输出到Excel并美化表格的工具。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Python 版本要求
    install_requires=['pandas', 'xlsxwriter', 'openpyxl'],  # 依赖的其他包（如 ["requests>=2.25.1"]）
)
