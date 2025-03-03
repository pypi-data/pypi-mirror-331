from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as req_file:
    requirements = req_file.readlines()

setup(
    name="eralibpy-mp",
    version="0.4.0",
    description="ERa Python/Micropython library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eoh-jsc/era-lib-py",
    license="MIT",
    author="EoH Ltd",
    author_email="info@eoh.io",
    setup_requires=["pytest-runner"],
    tests_require=["pytest>=6.2.5", "pytest-mock>=3.6.1"],
    py_modules=["era.era", "era.era_micro", "era.era_protocol", "era.era_const", "era.era_wifi", "era.era_timer"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
)
