from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().splitlines()


setup(
    name="emoatlas",
    version="0.0.1",
    description="A Python library for the detection and visualization of emotions in texts",
    long_description=long_description,
    license="",
    url="https://github.com/alfonsosemeraro/emoatlas",
    author="",
    author_email="",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        # e.g. "Intended Audience :: Developers",
        # e.g. "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish (should match "license" above)
        # e.g. "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Other",
        "Operating System :: MacOS",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    keywords="",

    install_requires=requirements,
    python_requires='>=3.7.00',
    include_package_data=True,
    package_data={
        '': ['langs/*', 'baseline_tables/*'],
    },

    packages=find_packages(
        exclude=["docs/*", "demo/*", "tests/*", "sample_data/*"]
    ),
)
