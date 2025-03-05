from setuptools import setup, find_packages

setup(
    name="sizeforemir",
    version="0.1.0",
    author="Emir",
    description="Boy ve ayak uzunluğuna göre özel hesaplama yapan bir kütüphane.",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
