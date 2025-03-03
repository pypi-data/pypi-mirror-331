from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name="nanows",
    version="2.0.1",
    packages=find_packages(),
    install_requires=["websockets>=15.0,<16.0"],
    author="gr0vity-dev",
    author_email="iq.cc@pm.me",
    python_requires=">=3.9",  # Keep this one
    description="A robust, type-safe Python client for interacting with Nano cryptocurrency nodes via WebSockets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gr0vity-dev/nanows-v2",
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
    # Remove the second python_requires line that was here
)
