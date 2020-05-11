import unittest
from unittest.mock import patch, mock_open
from whiiif import app
import solr_responses
import manifests
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
        elif test == "collection":
            self.json_data = solr_responses.COLLECTION
        elif test == "snippet":
            self.json_data = solr_responses.SNIPPET
        elif test == "snippet_scaled":
            self.json_data = solr_responses.SNIPPET_SCALED

    def json(self):
        if self.test == "connection_failure":
            raise ConnectionError
        return self.json_data


class FakeManifests:
    """Class to simulate the data returned from reading manifest JSON files"""

    manifests = None

    def __init__(self):
        self.m1 = mock_open(read_data=manifests.COLLECTION_ONE)
        self.m2 = mock_open(read_data=manifests.COLLECTION_TWO)
        self.m1.side_effect = [self.m1.return_value, self.m2.return_value]
        self.manifests = self.m1


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
        app.config['MANIFEST_LOCATION'] = '/test/manifests'
        app.config['COLLECTION_MAX_DOCUMENT_RESULTS'] = 2
        app.config['COLLECTION_MAX_RESULTS'] = 20
        app.config['COLLECTION_SNIPPET_CONTEXT'] = 'word'
        app.config['COLLECTION_SNIPPET_CONTEXT_SIZE'] = 5
        app.config['COLLECTION_SNIPPET_CONTEXT_LIMIT'] = 'page'
        self.app = app.test_client()

    def test_collection_search_query(self):
        # Does the Collection Search endpoint generate the right SOLR query?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            mock_request.assert_called_once_with("http://testserver/solr/whiiiftest/select?hl=on"
                                                 "&hl.weightMatches=true&rows=20&df=ocr_text&hl.ocr.fl=ocr_text"
                                                 "&hl.snippets=2&hl.ocr.contextBlock=word&hl.ocr.contextSize=5"
                                                 "&hl.ocr.limitBlock=page&q=myquery")

    def test_collection_search_result_counts(self):
        # Does the Collection Search endpoint response contain correct numbers of items?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(len(json_response), 2)  # Two hits
            self.assertEqual(json_response[0]["total_results"], 8)  # First manifest has 8 results
            self.assertEqual(json_response[1]["total_results"], 2)  # Second manifest has 2 results
            self.assertEqual(len(json_response[0]["canvases"]), 2)
            self.assertEqual(len(json_response[1]["canvases"]), 2)

    def test_collection_search_manifest_url(self):
        # Does the Collection Search endpoint response contain correct manifest_urls?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["manifest_url"], "http://mytestserver/manifests/collection-manifest")
            self.assertEqual(json_response[1]["manifest_url"], "http://mytestserver/manifests/collection-another")

    def test_collection_search_canvas_id(self):
        # Does the Collection Search endpoint response contain correct canvas ids?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["canvas"], "page_0")
            self.assertEqual(json_response[0]["canvases"][1]["canvas"], "page_1")
            self.assertEqual(json_response[1]["canvases"][0]["canvas"], "page_1")
            self.assertEqual(json_response[1]["canvases"][1]["canvas"], "page_1")

    def test_collection_search_region(self):
        # Does the Collection Search endpoint response contain correct regions?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["region"], "1752,2897,3022,210")
            self.assertEqual(json_response[0]["canvases"][1]["region"], "951,3626,3018,226")
            self.assertEqual(json_response[1]["canvases"][0]["region"], "697,2690,3132,1220")
            self.assertEqual(json_response[1]["canvases"][1]["region"], "881,4194,2312,226")

    def test_collection_search_url(self):
        # Does the Collection Search endpoint response contain correct a correct image URL?
        # https://test-iiif-endpoint/iiif/collectionimage0/full/full/0/default.jpg",
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["url"], "https://test-iiif-endpoint/iiif/collectionimage0"
                                                                     "/1752,2897,3022,210/755,/0/default.jpg")
            self.assertEqual(json_response[0]["canvases"][1]["url"], "https://test-iiif-endpoint/iiif/collectionimage1"
                                                                     "/951,3626,3018,226/754,/0/default.jpg")
            self.assertEqual(json_response[1]["canvases"][0]["url"], "https://test-iiif-endpoint/iiif/collectionimage3"
                                                                     "/697,2690,3132,1220/783,/0/default.jpg")
            self.assertEqual(json_response[1]["canvases"][1]["url"], "https://test-iiif-endpoint/iiif/collectionimage3"
                                                                     "/881,4194,2312,226/578,/0/default.jpg")

    def test_collection_search_coords_single(self):
        # Does the Collection Search endpoint response have correct coords block for a single part result?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][1]["highlights"][0]["coords"], "185,23,226,33")
            self.assertEqual(json_response[0]["canvases"][1]["highlights"][0]["chars"], "test response")
            self.assertEqual(json_response[1]["canvases"][0]["highlights"][0]["coords"], "257,33,193,27")
            self.assertEqual(json_response[1]["canvases"][0]["highlights"][0]["chars"], "test response")
            self.assertEqual(json_response[1]["canvases"][1]["highlights"][0]["coords"], "80,25,204,27")
            self.assertEqual(json_response[1]["canvases"][1]["highlights"][0]["chars"], "test response")

    def test_collection_search_coords_multi(self):
        # Does the Collection Search endpoint response have correct coords block for a multiple part result?
        with patch("requests.get") as mock_request, patch("builtins.open", FakeManifests().manifests):
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][0]["coords"], "715,1,40,20")
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][0]["chars"], "test")
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][1]["coords"], "0,25,199,25")
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][1]["chars"], "response")

    def test_collection_search_connection_failure(self):
        # Does the Collection Search endpoint register the error and return gracefully when SOLR doesn't respond?
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="connection_failure")
            rv = self.app.get('/collection/search?q=myquery')
            self.assertIn("ERROR:whiiif:Error occurred with SOLR query: <class 'requests.exceptions.ConnectionError'>",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertEqual(json_response, [])

    def test_collection_search_solr_error(self):
        # Does the Collection Search endpoint register the error and return gracefully when SOLR returns an error?
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="solr_error")
            rv = self.app.get('/collection/search?q=myquery')
            self.assertIn("ERROR:whiiif:Error occurred with SOLR query: <class 'KeyError'>",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertEqual(json_response, [])

    def test_collection_search_missing_manifests(self):
        # Does the Collection Search endpoint register the error and skip the result if the manifest JSON is missing?
        # TODO: Add a third manifest to the response, and have only two "missing"
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="collection")
            rv = self.app.get('/collection/search?q=myquery')
            self.assertIn("ERROR:whiiif:Missing manifest JSON file: /test/manifests/collection-manifest.json",
                          log_catcher.output)
            self.assertIn("ERROR:whiiif:Missing manifest JSON file: /test/manifests/collection-another.json",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertEqual(json_response, [])


class SnippetSearchTestCase(unittest.TestCase):
    """Tests for the Snippet Search endpoint"""
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        app.config['SERVER_NAME'] = 'testserver:5000'
        app.config['SOLR_URL'] = 'http://testserver/solr'
        app.config['SOLR_CORE'] = 'whiiiftest'
        app.config['OCR_TEXT_FIELD'] = 'ocr_text'
        app.config['MANIFEST_URL_FIELD'] = 'manifest_url'
        app.config['DOCUMENT_ID_FIELD'] = 'id'
        app.config['MANIFEST_LOCATION'] = '/test/manifests'
        app.config['SNIPPETS_MAX_RESULTS'] = 3
        app.config['SNIPPET_CONTEXT'] = 'word'
        app.config['SNIPPET_CONTEXT_SIZE'] = 5
        app.config['SNIPPET_CONTEXT_LIMIT'] = 'line'
        self.app = app.test_client()

    def test_snippet_search_query(self):
        # Does the Snippet Search endpoint generate the right SOLR query?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            mock_request.assert_called_once_with("http://testserver/solr/whiiiftest/select?hl=on"
                                                 "&hl.weightMatches=true&hl.snippets=3&df=ocr_text&hl.ocr.fl=ocr_text"
                                                 "&hl.ocr.contextBlock=word&hl.ocr.contextSize=5&hl.ocr.limitBlock=line"
                                                 "&fq=id:test-manifest&q=myquery")

    def test_snippet_search_result_counts(self):
        # Does the Snippet Search endpoint response contain correct numbers of items?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(len(json_response), 1)
            self.assertEqual(json_response[0]["total_results"], 4)
            self.assertEqual(len(json_response[0]["canvases"]), 3)

    def test_snippet_search_id(self):
        # Does the Snippet Search endpoint response contain the correct id?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["id"], "test-manifest")

    def test_snippet_search_canvas_id(self):
        # Does the Snippet Search endpoint response contain correct canvas ids?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["canvas"], "page_224")
            self.assertEqual(json_response[0]["canvases"][1]["canvas"], "page_537")
            self.assertEqual(json_response[0]["canvases"][2]["canvas"], "page_537")

    def test_snippet_search_region(self):
        # Does the Snippet Search endpoint response contain correct regions?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["region"], "2124,3672,2557,154")
            self.assertEqual(json_response[0]["canvases"][1]["region"], "622,1279,2814,301")
            self.assertEqual(json_response[0]["canvases"][2]["region"], "1313,2983,2797,156")

    def test_snippet_search_coords_single(self):
        # Does the Snippet Search endpoint response have correct coords block for a single part result?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][0]["coords"], "1673,0,773,97")
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][0]["chars"], "test response")
            self.assertEqual(json_response[0]["canvases"][2]["highlights"][0]["coords"], "1324,33,771,100")
            self.assertEqual(json_response[0]["canvases"][2]["highlights"][0]["chars"], "test response")

    def test_snippet_search_coords_multi(self):
        # Does the Snippet Search endpoint response have correct coords block for a multiple part result?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][1]["highlights"][0]["coords"], "2511,40,303,123")
            self.assertEqual(json_response[0]["canvases"][1]["highlights"][0]["chars"], "test")
            self.assertEqual(json_response[0]["canvases"][1]["highlights"][1]["coords"], "0,140,544,161")
            self.assertEqual(json_response[0]["canvases"][1]["highlights"][1]["chars"], "response")

    def test_snippet_search_connection_failure(self):
        # Does the Snippet Search endpoint register the error and return gracefully when SOLR doesn't respond?
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="connection_failure")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            self.assertIn("ERROR:whiiif:Error occurred with SOLR query: <class 'requests.exceptions.ConnectionError'>",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertEqual(json_response, [])

    def test_snippet_search_solr_error(self):
        # Does the Snippet Search endpoint register the error and return gracefully when SOLR returns an error?
        with patch("requests.get") as mock_request, self.assertLogs(level='ERROR') as log_catcher:
            mock_request.return_value = FakeResponse(test="solr_error")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            self.assertIn("ERROR:whiiif:Error occurred with SOLR query: <class 'KeyError'>",
                          log_catcher.output)
            json_response = rv.get_json()
            self.assertEqual(json_response, [])

    def test_snippet_search_snips(self):
        # Does the Snippet Search endpoint correctly handle the snips parameter?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet")
            rv = self.app.get('/snippets/test-manifest?q=myquery&snips=1')
            mock_request.assert_called_once_with("http://testserver/solr/whiiiftest/select?hl=on"
                                                 "&hl.weightMatches=true&hl.snippets=1&df=ocr_text&hl.ocr.fl=ocr_text"
                                                 "&hl.ocr.contextBlock=word&hl.ocr.contextSize=5&hl.ocr.limitBlock=line"
                                                 "&fq=id:test-manifest&q=myquery")

    def test_snippet_search_scaled(self):
        # Does the Snippet Search endpoint response correctly apply scaling when present in SOLR response?
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse(test="snippet_scaled")
            rv = self.app.get('/snippets/test-manifest?q=myquery')
            json_response = rv.get_json()
            self.assertEqual(json_response[0]["canvases"][0]["region"], "7434,12852,8949,539")
            self.assertEqual(json_response[0]["canvases"][0]["highlights"][0]["coords"], "5855,0,2705,339")

if __name__ == '__main__':
    unittest.main()