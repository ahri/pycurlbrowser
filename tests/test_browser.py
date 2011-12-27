from unittest import TestCase
from pycurlbrowser import Browser, CannedResponse
from datetime import timedelta

class TestBrowser(TestCase):

    """
    Some rather brittle tests based upon existing websites
    """

    def setUp(self):
        self.browser = Browser()

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

    def test_canned_response_duckduckgo(self):
        """Let's pretend that duckduckgo.com's frontpage 404s"""
        # Arrange
        can = CannedResponse()
        can.code = 404
        self.browser.canned_response['duckduckgo.com/html'] = can
        # Act, Assert
        self.assertEqual(self.browser.go('duckduckgo.com/html'), 404)

    def test_canned_content_duckduckgo(self):
        """Let's pretend that duckduckgo.com's frontpage has a silly message"""
        # Arrange
        can = CannedResponse()
        can.src = "Try Google"
        self.browser.canned_response['duckduckgo.com/html'] = can
        # Act
        self.browser.go('duckduckgo.com/html')
        # Assert
        self.assertEqual(self.browser.src, can.src)

    def test_canned_roundtrip_duckduckgo(self):
        """Let's pretend that duckduckgo.com's really slow"""
        # Arrange
        can = CannedResponse()
        can.roundtrip = timedelta(5)
        self.browser.canned_response['duckduckgo.com/html'] = can
        # Act
        self.browser.go('duckduckgo.com/html')
        # Assert
        self.assertEqual(self.browser.roundtrip, can.roundtrip)

    def test_canned_exception_duckduckgo(self):
        """Let's pretend that duckduckgo.com's really slow"""
        # Arrange
        can = CannedResponse()
        self.browser.canned_response['duckduckgo.com/html'] = can
        # Act
        self.browser.go('duckduckgo.com/html')
        # Assert
        self.assertRaises(Exception, self.browser.go('duckduckgo.com/html'))
