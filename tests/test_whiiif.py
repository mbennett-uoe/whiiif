import unittest

import whiiif
import os.path


class BaseAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = whiiif.app.test_client()
        self.config = whiiif.app.config

    def test_index(self):
        # Can we get the homepage?
        rv = self.app.get('/')
        self.assertIn('Welcome to Whiiif', rv.data.decode())

    def test_config(self):
        # Do all the required config variables exist?
        self.assertIn("SERVER_NAME", self.config)
        self.assertIn("LOG_DIR", self.config)
        self.assertIn("SOLR_URL", self.config)
        self.assertIn("SOLR_CORE", self.config)
        self.assertIn("OCR_TEXT_FIELD", self.config)
        self.assertIn("MANIFEST_URL_FIELD", self.config)
        self.assertIn("DOCUMENT_ID_FIELD", self.config)
        self.assertIn("MANIFEST_LOCATION", self.config)
        self.assertIn("XML_LOCATION", self.config)

    def test_manifest_dir(self):
        # Does the manifest directory exist?
        manifest_path = self.config["MANIFEST_LOCATION"]
        self.assertTrue(os.path.isdir(manifest_path))

    def test_xml_dir(self):
        # Does the xml directory exist?
        xml_path = self.config["XML_LOCATION"]
        self.assertTrue(os.path.isdir(xml_path))


if __name__ == '__main__':
    unittest.main()
