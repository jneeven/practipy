import os

from setuptools import find_packages, setup


def requires(filename: str):
    return open(filename).read().splitlines()


extras_require = {
    "dev": requires("dev-requirements.txt"),
    "cache": requires("requirements/cache.txt"),
    "gcloud": requires("requirements/gcloud.txt"),
    "math": requires("requirements/math.txt"),
    "tensorflow": requires("requirements/tensorflow.txt"),
}
# Add an extra install option to install ALL requirements.
extras_require["all"] = [requirement for requirement in extras_require.values()]

setup(
    name="practipy",
    version=os.getenv("PACKAGE_VERSION"),
    author="Jelmer Neeven",
    author_email="jelmer@neeven.tech",
    license="MIT",
    description="Python convenience functions and classes",
    keywords="python utility practical convenience",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    platforms=["Linux"],
    packages=find_packages(),
    install_requires=[],
    extras_require=extras_require,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
