from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mrlee",
    version="0.1.0",  # Update this for new releases
    author="Kevin Lee",
    author_email="kevinlulee1@gmail.com",
    description="A collection of simple and useful utilities for file and string operations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kevinlulee/mrlee",
    packages=find_packages(),  # Automatically find packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Specify Python version compatibility
    install_requires=[],  # Add dependencies here
    extras_require={
        "dev": [
            "pytest>=6.0",  # Testing framework
        ],
    },
)
