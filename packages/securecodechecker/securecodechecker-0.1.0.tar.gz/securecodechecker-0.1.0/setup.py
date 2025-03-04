from setuptools import setup, find_packages

setup(
    name="securecodechecker",
    version="0.1.0",
    author="raayan",
    author_email="your.email@example.com",
    description="A Python module to scan code for common insecure coding patterns (for ethical and educational use).",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/securecodechecker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
