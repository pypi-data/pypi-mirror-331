"""
@author: Ethan
@contact: email:
@Created on: 2025/1/1 11:17
@Remark:
"""
import setuptools

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="lelu_admin_test",
    version="1.0.3",
    author="DVAdmin",
    author_email="",
    description="插件测试",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/FireworksWD/lelu-admin-plugin",
    packages=setuptools.find_packages(),
    python_requires='>=3.9, <4',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)