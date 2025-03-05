import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="loyalicos",
    version="1.0.0alpha7-15",
    author="Alex Sánchez Vega",
    author_email="alex@loyalicos.com",
    description="SDK for easy integration with Loyalicos API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loyalicos/python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/loyalicos/python-sdk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=['requests'],
)