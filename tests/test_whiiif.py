import unittest

import whiiif
import os.path

class BaseAppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = whiiif.app.test_client()
        self.config = whiiif.app.config

    def test_index(self):
        rv = self.app.get('/')
        self.assertIn('Welcome to Whiiif', rv.data.decode())

    def test_manifest_dir(self):
        manifest_path = self.config["MANIFEST_LOCATION"]
        self.assertTrue(os.path.isdir(manifest_path))

    def test_xml_dir(self):
        xml_path = self.config["XML_LOCATION"]
        self.assertTrue(os.path.isdir(xml_path))


if __name__ == '__main__':
    unittest.main()
