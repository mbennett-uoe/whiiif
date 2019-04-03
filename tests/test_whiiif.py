import unittest

import whiiif


class WhiiifTestCase(unittest.TestCase):

    def setUp(self):
        self.app = whiiif.app.test_client()

    def test_index(self):
        rv = self.app.get('/')
        self.assertIn('Welcome to Whiiif', rv.data.decode())


if __name__ == '__main__':
    unittest.main()
