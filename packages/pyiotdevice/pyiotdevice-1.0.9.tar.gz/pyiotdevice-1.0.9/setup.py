from setuptools import setup, find_packages

setup(
    name="pyiotdevice",
    version="1.0.9",
    packages=find_packages(),
    install_requires=[
        "pycryptodome",  # Required for AES encryption (Crypto.Cipher, Crypto.Random, Crypto.Util.Padding)
    ],
    author="iota Labs",
    author_email="info@iotalabs.co.in",
    description="A Python library for IoT device security and communication",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyiotdevice",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
