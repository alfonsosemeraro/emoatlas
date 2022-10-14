import setuptools

setuptools.setup(
    name="emolib",
    version="0.0.1",
    description="installable version of emolib to improve usability",
    packages=["."],
    install_requires=[
        'matplotlib>=3.5.31',
        'spacy>=3.4.1',
        'networkx>=2.6.3',
        'nltk>=3.7',
        'shapely>=1.8.4',
        'descartes>=1.1.0',
        'pandas>=1.3.5',
        'community>=1.0.0b1',
        'python-louvain>=0.16'
        ],
    python_requires='>=3.7.00',
)
