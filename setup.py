from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="trade-simulator",
    version="0.1.0",
    author="Abhijeet Yadav",
    author_email="rabhi.official@gmail.com",
    description="A cryptocurrency trade simulator with market impact and slippage modeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thecodeblood/trade-simulator",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "websocket-client",
        "PyQt6",
        "pytest",
        "pytest-asyncio",
    ],
    entry_points={
        "console_scripts": [
            "trade-simulator=main:main",
        ],
    },
)