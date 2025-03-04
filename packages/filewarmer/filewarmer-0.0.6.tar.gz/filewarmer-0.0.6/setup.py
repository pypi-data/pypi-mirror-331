from setuptools import setup, find_packages

setup(
    name="filewarmer",
    version="0.0.6",
    description="Library to read file blocks as fast as possible",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={
        "filewarmer": ["lib/*.h", "lib/*.so"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
)
