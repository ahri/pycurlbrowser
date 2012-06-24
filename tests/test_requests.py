from unittest import TestCase
from pycurlbrowser import RequestsBackend
from datetime import timedelta

class TestBackendApi(TestCase):

    """
    Test that the HttpBackend API is adhered-to.
    """

    def setUp(self):
        self.backend = RequestsBackend()

    def visit(self):
        url     = 'http://www.reddit.com/'
        method  = 'GET'
        data    = None
        headers = None
        auth    = None
        follow  = None
        agent   = "foo"
        retries = 1
        debug   = None
        self.backend.go(url, method, data, headers, auth, follow, agent, retries, debug)
        return url

    def test_go(self):
        _ = self.visit()

    def test_src(self):
        _ = self.visit()
        self.assertTrue(len(self.backend.src) > 0)

    def test_url(self):
        url = self.visit()
        self.assertEqual(self.backend.url, url)

    def test_roundtrip(self):
        _ = self.visit()
        self.assertTrue(self.backend.roundtrip > timedelta(0))

    def test_http_code(self):
        _ = self.visit()
        self.assertEqual(self.backend.http_code, 200)

    def test_headers(self):
        _ = self.visit()
        self.assertTrue(self.backend.headers.keys > 0)
