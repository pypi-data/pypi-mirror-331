from setuptools import setup, find_packages
import subprocess
import os
import inspect

# Generate protocol libs for python
generate_cmd = f'python3 -m grpc_tools.protoc --proto_path=./ --grpc_python_out=pylevers' \
               f' --python_out=pylevers proto/*.proto'

subprocess.check_output(generate_cmd, shell=True)

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pylevers",
    version="0.1.0",  # This will be overridden by setuptools_scm
    packages=find_packages(),
    use_scm_version={
        "root": "../../..",
        "relative_to": __file__,
        'write_to': 'pylevers/version.py',
        'write_to_template': '__version__ = "{version}"',
        'version_scheme': 'post-release',
    },
    setup_requires=['setuptools_scm'],
    install_requires=[
        'grpcio<=1.67.1,>=1.49.1',
        'grpcio-tools<=1.67.1,>=1.49.1',
        'numpy',
    ],
    author="Zhou liwei",
    author_email="zhoulw1@lenovo.com",
    description="A Python client for Levers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    include_package_data=True,
)

