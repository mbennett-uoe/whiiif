# Whiiif - Word Highlighting (in) IIIF

Whiiif is an implementation of the [IIIF Search API](https://iiif.io/api/search/1.0/) designed to provide full-text
search with granular, word-level Annotation results to enable front-end highlighting.

OCR transcriptions are ingested from word-level [ALTO](https://www.loc.gov/standards/alto/) format and indexed in 
[SOLR](http://lucene.apache.org/solr/).

Please note this is a work in development and therefore is offered with no guarantees as to stability, usefulness,
security etc.

## Prerequisites

Whiiif is designed for Python 3, but may work under Python 2, however no testing of this has been done. To use py2, 
please edit `Makefile`

Whiiif requires a preinstalled SOLR instance (any version 8.0+) and installation of the [`solr-ocrhighlighting` plugin v0.3.1]
(https://github.com/dbmdz/solr-ocrhighlighting/releases/tag/0.3.1).

SOLR configuration files are provided in the `solrconf` directory and you can use these if you just want to get up and
running quickly. Otherwise, please refer to the documentation for more detailed instructions.

Some Flask dependencies are compiled during installation, so `gcc` and Python header files need to be present.
For example, on Ubuntu:

    apt install build-essential python3-dev


## Development environment and release process

 - create virtualenv with Flask and Whiiif installed into it (latter is installed in
   [develop mode](http://setuptools.readthedocs.io/en/latest/setuptools.html#development-mode) which allows
   modifying source code directly without a need to re-install the app): `make venv`

 - run development server in debug mode: `make run`; Flask will restart if source code is modified

 - run tests: `make test` (see also: [Testing Flask Applications](http://flask.pocoo.org/docs/0.12/testing/))

 - create source distribution: `make sdist` (will run tests first)

 - to remove virtualenv and built distributions: `make clean`

 - to add more python dependencies: add to `install_requires` in `setup.py`

 - to modify configuration in development environment: edit file `settings.cfg`; this is a local configuration file
   and it is *ignored* by Git - make sure to put a proper configuration file to a production environment when
   deploying


## Deployment

In either case, generally the idea is to build a package (`make sdist`), deliver it to a server (`scp ...`),
install it (`pip install whiiif.tar.gz`), ensure that configuration file exists and
`WHIIIF_SETTINGS` environment variable points to it, ensure that user has access to the
working directory to create and write log files in it, and finally run a
[WSGI container](http://flask.pocoo.org/docs/1.0/deploying/wsgi-standalone/) with the application.
And, most likely, it will also run behind a
[reverse proxy](http://flask.pocoo.org/docs/1.0/deploying/wsgi-standalone/#proxy-setups).


## Acknowledgements

This project takes inspiration from Glen Robson's 
[Simple Annotation Server](https://github.com/glenrobson/SimpleAnnotationServer) and the 
[Ocracoke](https://github.com/NCSU-Libraries/ocracoke) project at NCSU.

[A cookiecutter flask template](https://github.com/candidtim/cookiecutter-flask-minimal) was used for the initial 
application framework.

## License

This project is released under the terms of the GNU LGPL v3. For more information, please see `LICENSE.md` 
