from unittest import TestCase
from pycurlbrowser import Browser, CannedResponse
from datetime import timedelta
import pycurl

class TestBrowserLive(TestCase):

    """
    Some rather brittle tests based upon existing websites
    """

    def setUp(self):
        self.browser = Browser()
        self.browser._curl.setopt(pycurl.CONNECTTIMEOUT, 5)
        self.browser._curl.setopt(pycurl.TIMEOUT, 10)

    def test_visit_duckduckgo(self):
        """Visit a website, check that we get there"""
        self.assertEqual(self.browser.go('duckduckgo.com'), 200)
        self.assertEqual(self.browser.url.lower(), 'http://duckduckgo.com')

    def test_search_duckduckgo(self):
        """Hopefully a search results page will include the search string"""
        search = "a crumble layer that you swirl"
        self.assertEqual(self.browser.go('duckduckgo.com/html'), 200)
        self.browser.form_select(0)
        self.assertTrue('q' in self.browser.form_fields)
        self.browser.form_data_update(q=search)
        self.assertEqual(self.browser.form_submit(), 200)
        print self.browser.src
        self.assertTrue(search in self.browser.src)

class TestBrowserCanned(TestCase):

    """
    Tests on canned responses
    """

    def setUp(self):
        self.browser = Browser()

    def test_canned_response_duckduckgo(self):
        """Let's pretend that duckduckgo.com's frontpage 404s"""
        # Arrange
        url = 'duckduckgo.com/html'
        can = CannedResponse()
        can.code = 404
        self.browser.add_canned_response(can, url)
        # Act, Assert
        self.assertEqual(self.browser.go(url), 404)

    def test_canned_content_duckduckgo(self):
        """Let's pretend that duckduckgo.com's frontpage has a silly message"""
        # Arrange
        url = 'duckduckgo.com/html'
        can = CannedResponse()
        can.src = "Try Google"
        self.browser.add_canned_response(can, url)
        # Act
        self.browser.go(url)
        # Assert
        self.assertEqual(self.browser.src, can.src)

    def test_canned_roundtrip_duckduckgo(self):
        """Let's pretend that duckduckgo.com's really slow"""
        # Arrange
        url = 'duckduckgo.com/html'
        can = CannedResponse()
        can.roundtrip = timedelta(5)
        self.browser.add_canned_response(can, url)
        # Act
        self.browser.go(url)
        # Assert
        self.assertEqual(self.browser.roundtrip, can.roundtrip)

    def test_canned_exception_duckduckgo(self):
        """What if curl raises an exception?"""
        # Arrange
        url = 'duckduckgo.com/html'
        can = CannedResponse()
        can.exception = pycurl.error()
        self.browser.add_canned_response(can, url)
        # Act, Assert
        # nb. for some reason assertRaises(pycurl.error, ...) doesn't seem to
        #     work, so here's a hack around that
        try:
            self.browser.go(url)
            self.assertTrue(False)
        except pycurl.error:
            self.assertTrue(True)

    def test_canned_code_verbs(self):
        """Different canned response codes for different verbs"""
        # Arrange
        url = 'duckduckgo.com/html'

        can_post = CannedResponse()
        can_post.code = 1
        self.browser.add_canned_response(can_post, url, 'POST')

        can_get = CannedResponse()
        can_get.code = 2
        self.browser.add_canned_response(can_get, url, 'GET')

        can_put = CannedResponse()
        can_put.code = 3
        self.browser.add_canned_response(can_put, url, 'PUT')

        can_delete = CannedResponse()
        can_delete.code = 4
        self.browser.add_canned_response(can_delete, url, 'DELETE')

        # Act, Assert
        self.assertEqual(self.browser.go(url, 'POST'),   1)
        self.assertEqual(self.browser.go(url, 'GET'),    2)
        self.assertEqual(self.browser.go(url, 'PUT'),    3)
        self.assertEqual(self.browser.go(url, 'DELETE'), 4)

    def test_canned_code_data(self):
        """Different canned response codes for different data passed"""
        # Arrange
        url = 'duckduckgo.com/html'
        method = 'POST'

        can_one = CannedResponse()
        can_one.code = 1
        data_one = dict(foo='bar')
        self.browser.add_canned_response(can_one, url, method, data_one)

        can_two = CannedResponse()
        can_two.code = 2
        data_two = dict(bar='foo')
        self.browser.add_canned_response(can_two, url, method, data_two)

        # Act, Assert
        self.assertEqual(self.browser.go(url, method, data_one), 1)
        self.assertEqual(self.browser.go(url, method, data_two), 2)
