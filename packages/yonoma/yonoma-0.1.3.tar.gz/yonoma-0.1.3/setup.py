from setuptools import setup, find_packages

setup(
    name="yonoma",
    version="0.1.3",
    packages=find_packages(),
    install_requires=["requests"],
    author="Yonoma",
    author_email="yonoma.email@example.com",
    description="A Python client for the Yonoma API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SuthishTwinarcus/yonoma",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13.2",
)
