from unittest import TestCase
from pycurlbrowser import Browser, CannedResponse
from pycurlbrowser.browser import post_data_present, post_best_fit, canned_key_partial_subset
from datetime import timedelta
import pycurl

class TestBrowserCanned(TestCase):

    """
    Tests on canned responses
    """

    def setUp(self):
        self.browser = Browser()
        self.browser.offline = True

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
        self.assertRaises(pycurl.error, self.browser.go, url)

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

    def test_offline_mode(self):
        """If in offline mode and no canned response, raise an exception"""
        self.assertRaises(LookupError, self.browser.go, "someurl")

class TestForms(TestCase):

    """
    Tests around form behaviour.
    """

    def setUp(self):
        self.browser = Browser()
        self.browser.offline = True

    def test_no_method(self):
        """When no method is specified in a form the default should be GET"""
        form = CannedResponse()
        form.src = """
            <form>
                <input type="hidden" name="name" value="value" />
                <input type="submit" />
            </form>
        """
        self.browser.add_canned_response(form, 'form')
        self.browser.add_canned_response(form, 'form?name=value', 'GET', dict(name="value"))
        self.browser.go('form')
        self.browser.form_select(0)
        self.browser.form_submit()

    def test_no_action(self):
        """When no action is specified in a form the URL should be replicated"""
        url = 'form'
        form = CannedResponse()
        form.src = """
            <form method="post">
                <input type="submit" />
            </form>
        """
        self.browser.add_canned_response(form, url)
        self.browser.add_canned_response(form, url, 'POST', dict())
        self.browser.go(url)
        self.browser.form_select(0)
        self.browser.form_submit()

    def test_match_data(self):
        """Pick the best data match"""
        url = 'form'
        form = CannedResponse()
        form.src = """
            <form method="post">
                <input type="text" name="one" value="one" />
                <input type="text" name="two" value="two" />
                <input type="text" name="three" value="three" />
                <input type="submit" />
            </form>
        """
        right = CannedResponse()
        right.src = "right"
        wrong = CannedResponse()
        wrong.src = "wrong"

        self.browser.add_canned_response(form, url)
        self.browser.add_canned_response(wrong, url, 'POST', dict(one="one"))
        self.browser.add_canned_response(wrong, url, 'POST', dict(two="two"))
        self.browser.add_canned_response(right, url, 'POST', dict(one="one", two="two"))
        self.browser.add_canned_response(wrong, url, 'POST', dict(three="three"))

        self.browser.go(url)
        self.browser.form_select(0)
        self.browser.form_submit()
        self.assertEqual(right.src, self.browser.src)

    def test_no_match_data(self):
        """Error when no canned data matches"""
        url = 'form'
        form = CannedResponse()
        form.src = """
            <form method="post">
                <input type="text" name="one" value="one" />
                <input type="text" name="two" value="two" />
                <input type="text" name="three" value="three" />
                <input type="submit" />
            </form>
        """
        wrong = CannedResponse()
        wrong.src = "wrong"

        self.browser.add_canned_response(form, url)
        self.browser.add_canned_response(wrong, url, 'POST', dict(four="four"))

        self.browser.go(url)
        self.browser.form_select(0)
        self.assertRaises(ValueError, self.browser.form_submit)

class Util(TestCase):

    """
    Exercise the utilities
    """

    def test_data_present(self):
        """Ensure that the reference data exists in the input data"""
        d_ref = "a=1&b=2"
        d_in  = "a=1&c=3&b=2"

        self.assertTrue(post_data_present(d_ref, d_in))

    def test_data_not_present(self):
        """Ensure that the reference data exists in the input data, and fail when it doesn't"""
        d_ref = "a=1&c=3&b=2"
        d_in  = "a=1&b=2"

        self.assertFalse(post_data_present(d_ref, d_in))

    def test_data_best_fit(self):
        """Determine the best match from a list of data"""
        d_in = "a=1&b=2&some=other&uninteresting=crap"
        expected_winner = "a=1&b=2"
        d_ref  = ["a=1&b=2&c=3&d=4&e=5", "a=1", expected_winner, "a=1&b=2&c=3&d=4&e=5&f=6"]
        self.assertEqual(post_best_fit(d_in, *d_ref), expected_winner)

    def test_partial_key_match(self):
        """Knowing that a canned key is (url, method, data), match keys on (url, method)"""
        matcher = ('a', 'b')
        sample = [('a', 'b', 'c=1'), ('d', 'e', 'f=2'), ('a', 'b', 'i=3')]
        expected = ['c=1', 'i=3']
        self.assertEqual(canned_key_partial_subset(matcher, sample), expected)
