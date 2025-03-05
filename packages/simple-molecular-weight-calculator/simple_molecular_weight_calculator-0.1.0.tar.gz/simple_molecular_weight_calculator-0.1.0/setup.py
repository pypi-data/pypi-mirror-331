from setuptools import setup, find_packages

setup(
    name="simple-molecular-weight-calculator",
    version="0.1.0",
    data_files=[('bin', ['mm'])],  # Use the compiled Rust binary
    description="A simple molecular weight calculator implemented in Rust",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="Zimeng Xiong",
    url="https://github.com/zxzimeng/cli-molecular-weight-calculator",
    classifiers=[
        "Programming Language :: Rust",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Chemistry",
    ],
    python_requires=">=3.6",
)