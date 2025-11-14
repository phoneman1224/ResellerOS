from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="reselleros",
    version="1.0.0",
    author="ResellerOS Team",
    description="Production-ready desktop application for eBay resellers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reselleros/reselleros",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "reselleros=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.qss", "*.png", "*.jpg"],
    },
)
