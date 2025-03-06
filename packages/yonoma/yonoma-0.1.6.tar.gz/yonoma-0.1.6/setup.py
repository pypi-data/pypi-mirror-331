from setuptools import setup, find_packages

setup(
    name="yonoma",
    version="0.1.6",
    # packages=find_packages(),
    package_dir={'': 'src'}, 
    packages=find_packages(where='src'),
    install_requires=["requests"],
    author="YONOMAHQ",
    author_email="tools@yonoma.io",
    description="A Python client for the Yonoma API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YonomaHQ/yonoma-email-marketing-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13.2",
)
