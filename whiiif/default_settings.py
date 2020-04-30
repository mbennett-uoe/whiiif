# General Whiiif Settings
DEBUG = False  # make sure DEBUG is off unless enabled explicitly otherwise
FLASK_ENV = 'production'
SERVER_NAME = 'localhost:5000'
LOG_DIR = '.'  # create log files in current working directory

# SOLR Configuration
SOLR_URL = 'http://localhost:8983/solr'  # assume local solr instance
SOLR_CORE = 'whiiif'  # default core name

# Common Search options
OCR_TEXT_FIELD = 'ocr_text'  # the name of the field in the SOLR schema that contains the Whiiif-ingested XML data
MANIFEST_URL_FIELD = 'manifest_url'  # name of the field containing the URL of the manifest
DOCUMENT_ID_FIELD = 'id'  # the id field used for search urls
# Search within
WITHIN_MAX_RESULTS = 4096  # Max results when searching inside using IIIF Search, so should be quite high
# Snippet search
SNIPPETS_MAX_RESULTS = 10  # Max results when retrieving snippets for an individual document
SNIPPET_CONTEXT = 'word'  # context for the returned snippets - can be one of word, line or block
SNIPPET_CONTEXT_SIZE = 5  # number of context objects to return either side of the result
SNIPPET_CONTEXT_LIMIT = 'block'  # don't extend the context beyond this container object
# Collection search
COLLECTION_MAX_RESULTS = 5  # Max results per document, *not* overall
COLLECTION_SNIPPET_CONTEXT = 'word'  # context for the returned snippets - can be one of word, line or block
COLLECTION_SNIPPET_CONTEXT_SIZE = 5  # number of context objects to return either side of the result
COLLECTION_SNIPPET_CONTEXT_LIMIT = 'block'  # don't extend the context beyond this container object

# External files
XML_LOCATION = '../resources/xml'  # location to store ALTO-XML files. must be same as PathFieldLoader in solr config
MANIFEST_LOCATION = '../resources/manifests'  # location of the IIIF manifests
