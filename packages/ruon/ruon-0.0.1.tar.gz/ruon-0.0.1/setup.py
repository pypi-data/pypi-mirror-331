import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ruon",
    version="0.0.1",
    author="wangzhen0518",
    author_email="wangzhen0518@126.com",
    description="Implement some data structures and algorithms used in Rust for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wangzhen0518/ruon",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
