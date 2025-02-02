from setuptools import find_packages, setup

# Read the version from the version file
version = {}
with open("ofx_generator/__version__.py") as fp:
    exec(fp.read(), version)

setup(
    name="ofx-generator",
    version=version["__version__"],
    author="Marcos Bressan",
    author_email="bressan@dee.ufc.br",
    description="A library for generating OFX files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bressanmarcos/ofx-generator",
    packages=find_packages(include=["ofx-generator*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
