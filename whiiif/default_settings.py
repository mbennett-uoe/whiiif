DEBUG = True  # make sure DEBUG is off unless enabled explicitly otherwise
FLASK_ENV = 'development'
SERVER_NAME = 'localhost:5000'
LOG_DIR = '.'  # create log files in current working directory
SOLR_URL = 'http://localhost:8983/solr' # assume local solr instance
SOLR_CORE = 'whiiif' # default core name
XML_LOCATION  = '../xml' # location to store ascii-escaped XML files. must be same as PathFieldLoader in solr config