from setuptools import setup

import letterparser

with open("README.md") as fp:
    readme = fp.read()

setup(
    name="letterparser",
    version=letterparser.__version__,
    description="Decision letter and author response document parser.",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=["letterparser"],
    license="MIT",
    install_requires=[
        "elifearticle",
        "elifetools",
        "pypandoc",
        "requests",
        "docker",
        "configparser",
    ],
    url="https://github.com/elifesciences/decision-letter-parser",
    maintainer="eLife Sciences Publications Ltd.",
    maintainer_email="tech-team@elifesciences.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
