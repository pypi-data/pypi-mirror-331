import setuptools


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="rtests",
    version="0.1.6",
    author="BlindForReview.com",
    author_email="mail@blindforreview.com",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://blindforreview.com",
    packages=setuptools.find_packages(include=['rtests']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=parse_requirements('requirements.txt')
)
