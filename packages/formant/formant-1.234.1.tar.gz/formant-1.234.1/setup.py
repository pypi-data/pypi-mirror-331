import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version_to_use = "1.234.1"


if '-' in version_to_use:
    # Split on the first occurrence of the hyphen
    core_version, local_version = version_to_use.split('-', 1)
    # Reconstruct with a + to be pep440 compliant.
    # Note here setuptools will normalize "_" and "-" to dots. Even though PEP440 says
    # it's not required.
    pep440_version=f"{core_version}+{local_version}"
    print(f"{core_version}+{local_version}")
else:
    pep440_version= version_to_use

setuptools.setup(
    name="formant",
    version=pep440_version,
    author="Formant",
    author_email="eng@formant.io",
    description="Formant python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://formant.io",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    install_requires=[
        ## IMPORTANT!! If you need to change any of this
        ## you will need to test the python SDK for every targets we support
        ## which means Ubuntu 18, 20, 22 and for both python 2 and python 3
        ## Specifically the protobuf versions need to account for
        ## Formant grpc protos generationa as well as external library dependencies
        ## sych the googleapis or grpcio own requirements.
        "grpcio==1.37.0",
        "grpcio-status==1.37.0",
        'googleapis-common-protos<=1.52.0; python_version<"3.0.0"',
        'googleapis-common-protos>=1.56.3, <1.57; python_version>="3.6" and python_version<"3.10"',
        'googleapis-common-protos>=1.57, <=1.63.1; python_version>="3.10" and python_version<"3.11"',
        'protobuf==3.17.3; python_version<"3.0.0"',
        'protobuf>=3.15.8, <=3.19.5; python_version>="3.0.0"',
        "typing-extensions>=3.7.4.2",
        "requests>=2.25.1",
        "python-lzf>=0.2.4",
        "jsonschema>=1.0.0",
        "python-dateutil",
        "httpx; python_version>='3.0.0'",
        "numpy>=1.16.6",
        "wheel>=0.37.1",
    ],
    python_requires=">=2.7",
)
