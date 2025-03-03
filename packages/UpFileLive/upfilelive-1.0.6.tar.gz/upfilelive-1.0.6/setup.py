from setuptools import setup, find_packages

setup(
    name="UpFileLive",
    version="1.0.6",
    license="MIT",
    author="MoeN791",
    author_email="a15345506127@gmail.com",
    description="A Python tool for interacting with upfile.live for file sharing.",
    url="https://github.com/N791/UpFileLive",
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    install_requires=["playwright","loguru"],
)
