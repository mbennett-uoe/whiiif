import unittest
from unittest.mock import patch
from whiiif import app
import solr_responses
from requests.exceptions import ConnectionError


class FakeResponse(object):
    """Class to simulate the responses from SOLR via monkeypatching the request.get calls"""

    status_code = 200

    def __init__(self, test):
        self.test = test
        self.json_data = {}
        if test == "iiif":
            self.json_data = solr_responses.IIIF
        elif test == "solr_error":
            self.json_data = solr_responses.SOLR_ERROR
        elif test == "iiif_scaled":
            self.json_data = solr_responses.IIIF_SCALED

    def json(self):
        if self.test == "connection_failure":
            raise ConnectionError
        return self.json_data


class BaseAppTestCase(unittest.TestCase):
    """Tests for the functionality of the base application"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def test_index(self):
        # Can we get the homepage?
        rv = self.app.get('/')
        self.assertIn('Welcome to Whiiif', rv.data.decode())


class IIIFSearchTestCase(unittest.TestCase):
    """Tests for the IIIF Search API endpoint"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SERVER_NAME'] = 'testserver:5000'
        app.config['SOLR_URL'] = 'http://testserver/solr'
        app.config['SOLR_CORE'] = 'whiiiftest'
        app.config['OCR_TEXT_FIELD'] = 'ocr_text'
        app.config['MANIFEST_URL_FIELD'] = 'manifest_url'
        app.config['DOCUMENT_ID_FIELD'] = 'id'
        self.app = app.test_client()

    def test_iiif_search_query(self):
        # Does the IIIF endpoint generate the right SOLR query?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            mock_request.assert_called_once_with("http://testserver/solr/whiiiftest/select?hl=on&"
                                                 "hl.ocr.absoluteHighlights=true&hl.weightMatches=true"
                                                 "&hl.ocr.limitBlock=page&hl.ocr.contextSize=1"
                                                 "&hl.ocr.contextBlock=word&df=ocr_text&hl.ocr.fl=ocr_text"
                                                 "&hl.snippets=4096&fq=id:test-manifest&q=myquery")

    def test_iiif_search_context(self):
        # Does the IIIF endpoint response contain the correct @context block?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertListEqual(json_response["@context"], ['http://iiif.io/api/presentation/2/context.json',
                                                             'http://iiif.io/api/search/1/context.json'])

    def test_iiif_search_id(self):
        # Does the IIIF endpoint response contain the correct @id?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response["@id"], "http://testserver:5000/search/test-manifest?q=myquery")

    def test_iiif_search_result_counts(self):
        # Does the IIIF endpoint response contain correct numbers of items?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response["within"]["total"], 3)  # Three hits
            self.assertEqual(len(json_response["hits"]), 3)
            self.assertEqual(len(json_response["resources"]), 4)  # One is multi-line, so has two resources

    def test_iiif_search_resources_single(self):
        # Does the IIIF endpoint response have a correct resources block for single annotation results?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response["resources"][0]["@id"], 'uun:whiiif:test-manifest:page_1069:0')
            self.assertEqual(json_response["resources"][0]["on"],
                             'http://mytestserver/manifests/test-manifest/canvas/page_1069#xywh=466,1206,31,66')
            self.assertEqual(json_response["resources"][0]["resource"], {'@type': 'cnt:ContentAsText',
                                                                         'chars': 'test response'})
            self.assertEqual(json_response["resources"][1]["@id"], 'uun:whiiif:test-manifest:page_1073:1')
            self.assertEqual(json_response["resources"][1]["on"],
                             'http://mytestserver/manifests/test-manifest/canvas/page_1073#xywh=5099,3600,9,56')
            self.assertEqual(json_response["resources"][1]["resource"], {'@type': 'cnt:ContentAsText',
                                                                         'chars': 'test response'})

    def test_iiif_search_hits_single(self):
        # Does the IIIF endpoint response have a correct hits block for single annotation results?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response["hits"][0]["annotations"], ['uun:whiiif:test-manifest:page_1069:0'])
            self.assertEqual(json_response["hits"][0]["match"], 'test response')
            self.assertEqual(json_response["hits"][1]["annotations"], ['uun:whiiif:test-manifest:page_1073:1'])
            self.assertEqual(json_response["hits"][1]["match"], 'test response')

    def test_iiif_search_resources_multiple(self):
        # Does the IIIF endpoint response have a correct resources block for multiple annotation results?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response["resources"][2]["@id"], 'uun:whiiif:test-manifest:page_537:2')
            self.assertEqual(json_response["resources"][2]["on"],
                             'http://mytestserver/manifests/test-manifest/canvas/page_537#xywh=3133,1319,303,123')
            self.assertEqual(json_response["resources"][2]["resource"], {'@type': 'cnt:ContentAsText',
                                                                         'chars': 'test'})
            self.assertEqual(json_response["resources"][3]["@id"], 'uun:whiiif:test-manifest:page_537:2b')
            self.assertEqual(json_response["resources"][3]["on"],
                             'http://mytestserver/manifests/test-manifest/canvas/page_537#xywh=622,1419,544,161')
            self.assertEqual(json_response["resources"][3]["resource"], {'@type': 'cnt:ContentAsText',
                                                                         'chars': 'response'})

    def test_iiif_search_hits_multiple(self):
        # Does the IIIF endpoint response have a correct hits block for multiple annotation results?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response["hits"][2]["annotations"], ['uun:whiiif:test-manifest:page_537:2',
                                                                       'uun:whiiif:test-manifest:page_537:2b'])
            self.assertEqual(json_response["hits"][2]["match"], 'test response')

    def test_iiif_search_ignored(self):
        # Does the IIIF endpoint response correctly add the ignored value?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif")
            rv = self.app.get('/search/test-manifest?q=myquery&motivation=tagging')
            json_response = rv.get_json()
            self.assertEqual(json_response["within"]["ignored"], ["motivation"])

    def test_iiif_search_connection_failure(self):
        # Does the IIIF endpoint register the error and return gracefully when SOLR doesn't respond?
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="connection_failure")
            rv = self.app.get('/search/test-manifest')
            self.assertIn("ERROR:whiiif:Error occurred with SOLR query: <class 'requests.exceptions.ConnectionError'>",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertListEqual(json_response["@context"], ['http://iiif.io/api/presentation/2/context.json',
                                                             'http://iiif.io/api/search/1/context.json'])
            self.assertEqual(json_response["@id"], "http://testserver:5000/search/test-manifest")
            self.assertEqual(json_response["within"]["total"], 0)

    def test_iiif_search_solr_error(self):
        # Does the IIIF endpoint register the error and return gracefully when SOLR returns an error?
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="solr_error")
            rv = self.app.get('/search/test-manifest')
            self.assertIn("ERROR:whiiif:Error occurred with SOLR query: <class 'KeyError'>",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertListEqual(json_response["@context"], ['http://iiif.io/api/presentation/2/context.json',
                                                             'http://iiif.io/api/search/1/context.json'])
            self.assertEqual(json_response["@id"], "http://testserver:5000/search/test-manifest")
            self.assertEqual(json_response["within"]["total"], 0)

    def test_iiif_search_scaled(self):
        # Does the IIIF endpoint correctly apply scaling when present in SOLR results?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="iiif_scaled")
            rv = self.app.get('/search/test-scaled-manifest?q=test')
            json_response = rv.get_json()
            self.assertEqual(json_response["resources"][0]["on"],
                             'http://mytestserver/manifests/test-scaled-manifest/canvas/1#xywh=316,363,93,46')


class CollectionSearchTestCase(unittest.TestCase):
    """Tests for the Collection Search endpoint"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SERVER_NAME'] = 'testserver:5000'
        app.config['SOLR_URL'] = 'http://testserver/solr'
        app.config['SOLR_CORE'] = 'whiiiftest'
        app.config['OCR_TEXT_FIELD'] = 'ocr_text'
        app.config['MANIFEST_URL_FIELD'] = 'manifest_url'
        app.config['DOCUMENT_ID_FIELD'] = 'id'
        self.app = app.test_client()

if __name__ == '__main__':
    unittest.main()

#               'DEBUG': True,
#


#               'XML_LOCATION': '/test/xml',
#               'MANIFEST_LOCATION': '/test/manifests',
#               'WITHIN_MAX_RESULTS': 128,
#               'SNIPPETS_MAX_RESULTS': 3,
#               'SNIPPET_CONTEXT': 'word',
#               'SNIPPET_CONTEXT_SIZE': 5,
#               'SNIPPET_CONTEXT_LIMIT': 'line',
#               'COLLECTION_MAX_DOCUMENT_RESULTS': 2,
#               'COLLECTION_MAX_RESULTS': 20,
#               'COLLECTION_SNIPPET_CONTEXT': 'word',
#               'COLLECTION_SNIPPET_CONTEXT_SIZE': 5,
#               'COLLECTION_SNIPPET_CONTEXT_LIMIT': 'page',
#                }