from setuptools import setup, find_packages
from version_util import get_version

version_publish = get_version("0.0.1", "dev")
print(f"version_publish: {version_publish}")
setup(
    name="dev-nectarpy",
    version="0.0.22",
    packages=find_packages(),
    include_package_data=True,
    license="Apache License 2.0",
    description="A Python API module designed to run queries on Nectar",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/NectarProtocol/python-nectar-module",
    author="Tamarin Health",
    author_email="phil@tamarin.health",
    package_data={
        "": ["*.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8, <4",
    install_requires=["web3<7.0.0", "python-dotenv", "hpke"],
)
