from setuptools import setup, find_packages

setup(
    name='whiiif',
    version='2.0.0',
    long_description=" ",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'requests',
        'lxml',
        'bleach'
    ],
    author="Mike Bennett",
    author_email="mike.bennett@ed.ac.uk",
    description="Whiiif - Word Highlighting (in) IIIF. Whiiif is an implementation of the IIIF Search API designed to provide full-text search with granular, word-level Annotation results to enable front-end highlighting.",
    url="https://mbennett-uoe.github.io/whiiif/", 
    project_urls={
        "Bug Tracker": "https://github.com/mbennett-uoe/whiiif/issues",
        "Documentation": "https://mbennett-uoe.github.io/whiiif/",
        "Source Code": "https://github.com/mbennett-uoe/whiiif",
    },
    license="LGPL v3",
    license_file="LICENSE.md",
    platforms=["linux","windows"]
)
