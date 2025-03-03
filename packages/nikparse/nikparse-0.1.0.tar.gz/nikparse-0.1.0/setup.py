from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nikparse",
    version="0.1.0",
    author="NIK Parser",
    author_email="author@example.com",
    description="Parser for Indonesian National Identity Number (NIK)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nikparse",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "nikparse=nikparse.cli:main",
        ],
    },
)

