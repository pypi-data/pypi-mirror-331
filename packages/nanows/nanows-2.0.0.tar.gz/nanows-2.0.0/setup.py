from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="nanows",
    version="2.0.0",
    author="Nano WebSocket Client Contributors",
    author_email="info@example.com",
    description="A robust, type-safe Python client for interacting with Nano cryptocurrency nodes via WebSockets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/nanows",
    packages=find_packages(),
    package_dir={"nanows": "nanows"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
)
