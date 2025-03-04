"""
Julius Tokenizer - Setup Configuration

This setup.py file configures the package for distribution via PyPI and installation via pip.
It defines metadata about the package, dependencies, and installation requirements.
"""

from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # Basic package information
    name="julius-nlp-tokenizer",
    version="0.1.0",
    author="Julius Tokenizer Team",
    author_email="contact@novaintelligence.tech",
    description="A production-grade tokenizer for LLMs with perfect roundtrip accuracy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/julius_tokenizer",
    
    # Only include specific packages needed for the pretrained model
    packages=[
        "julius_tokenizer",
        "julius_tokenizer.tokenizer",
    ],
    
    # Package classifiers for PyPI
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Development Status :: 4 - Beta",
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Core dependencies required for the package to function
    install_requires=[
        "numpy>=1.20.0",      # For numerical operations
        "tokenizers>=0.13.0",     # For fast tokenization
        "huggingface-hub>=0.10.0", # For model loading from HF Hub
        "torch>=1.10.0",       # For tensor operations and model integration
    ],
    
    # Include non-Python files specified in MANIFEST.in
    include_package_data=True,
) 