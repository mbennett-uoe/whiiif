import unittest
from unittest import mock
from unittest.mock import patch
from whiiif import app
import os.path


class FakeResponse(object):
    status_code = 200

    def json(self):
        return {}


def fake_request(url):
    return FakeResponse()


class BaseAppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SERVER_NAME'] = 'localhost:5000'
        app.config['SOLR_URL'] = 'http://test/solr'
        app.config['SOLR_CORE'] = 'whiiiftest'
        app.config['OCR_TEXT_FIELD'] = 'ocr_text'
        app.config['MANIFEST_URL_FIELD'] = 'manifest_url'
        app.config['DOCUMENT_ID_FIELD'] = 'id'
        self.app = app.test_client()

    def test_index(self):
        # Can we get the homepage?
        rv = self.app.get('/')
        self.assertIn('Welcome to Whiiif', rv.data.decode())

    def test_search(self):
        with patch("requests.get") as mock_request:
            mock_request.return_value = FakeResponse()
            rv = self.app.get('/search/test-manifest?q=myquery')
            mock_request.assert_called_once_with("http://test/solr/whiiiftest/select?hl=on&"
                                                 "hl.ocr.absoluteHighlights=true&hl.weightMatches=true"
                                                 "&hl.ocr.limitBlock=page&hl.ocr.contextSize=1"
                                                 "&hl.ocr.contextBlock=word&df=ocr_text&hl.ocr.fl=ocr_text"
                                                 "&hl.snippets=4096&fq=id:test-manifest&q=myquery")
        print(rv.data)


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