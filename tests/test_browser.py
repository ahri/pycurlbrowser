from unittest import TestCase
from pycurlbrowser import Browser

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
        self.assertTrue(search in self.browser.src)
