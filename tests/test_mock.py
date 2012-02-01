from unittest import TestCase
from pycurlbrowser import Browser, MockBackend, MockResponse
from datetime import timedelta
import pycurl

class TestBackendApi(TestCase):

    """
    Test that the HttpBackend API is adhered-to.
    """

    def setUp(self):
        self.backend = MockBackend()

    def mocked_visit(self):
        mock = MockResponse()
        mock.src = "test data"
        mock.http_code = 123
        mock.headers = {}

        url = ""
        method  = 'GET'
        data    = None
        headers = None
        follow  = None
        agent   = None
        retries = None
        debug   = None

        self.backend.responses.add(mock, url, method, data, headers)
        self.backend.go(url, method, data, headers, follow, agent, retries, debug)
        return url, mock

    def test_go(self):
        self.mocked_visit()

    def test_src(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.backend.src, mock.src)

    def test_url(self):
        url, _ = self.mocked_visit()
        self.assertEqual(self.backend.url, url)

    def test_roundtrip(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.backend.roundtrip, mock.roundtrip)

    def test_http_code(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.backend.http_code, mock.http_code)

    def test_headers(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.backend.headers, mock.headers)

class TestBrowserMocked(TestCase):

    """
    Tests on mocked responses
    """

    def setUp(self):
        self.backend = MockBackend()
        self.browser = Browser(backend=self.backend)

    def go(self, url, method='GET', data=None, headers=None):
        self.backend.go(url=url,
                        method=method,
                        data=data,
                        headers=headers,
                        follow=None,
                        agent=None,
                        retries=None,
                        debug=None)

        return self.backend.http_code

    def test_mocked_response_duckduckgo(self):
        """Let's pretend that duckduckgo.com's frontpage 404s"""
        # Arrange
        url = 'duckduckgo.com/html'
        mock = MockResponse()
        mock.http_code = 404
        self.backend.responses.add(mock, url)
        # Act, Assert
        self.assertEqual(self.go(url), 404)

    def test_mocked_content_duckduckgo(self):
        """Let's pretend that duckduckgo.com's frontpage has a silly message"""
        # Arrange
        url = 'duckduckgo.com/html'
        mock = MockResponse()
        mock.src = "Try Google"
        self.backend.responses.add(mock, url)
        # Act
        self.go(url)
        # Assert
        self.assertEqual(self.backend.src, mock.src)

    def test_mocked_roundtrip_duckduckgo(self):
        """Let's pretend that duckduckgo.com's really slow"""
        # Arrange
        url = 'duckduckgo.com/html'
        mock = MockResponse()
        mock.roundtrip = timedelta(5)
        self.backend.responses.add(mock, url)
        # Act
        self.go(url)
        # Assert
        self.assertEqual(self.backend.roundtrip, mock.roundtrip)

    def test_mocked_exception_duckduckgo(self):
        """What if curl raises an exception?"""
        # Arrange
        url = 'duckduckgo.com/html'
        mock = MockResponse()
        mock.exception = pycurl.error()
        self.backend.responses.add(mock, url)
        # Act, Assert
        self.assertRaises(pycurl.error, self.go, url)

    def test_mocked_code_verbs(self):
        """Different mocked response codes for different verbs"""
        # Arrange
        url = 'duckduckgo.com/html'

        mock_post = MockResponse()
        mock_post.http_code = 1
        self.backend.responses.add(mock_post, url, 'POST')

        mock_get = MockResponse()
        mock_get.http_code = 2
        self.backend.responses.add(mock_get, url, 'GET')

        mock_put = MockResponse()
        mock_put.http_code = 3
        self.backend.responses.add(mock_put, url, 'PUT')

        mock_delete = MockResponse()
        mock_delete.http_code = 4
        self.backend.responses.add(mock_delete, url, 'DELETE')

        # Act, Assert
        self.assertEqual(self.go(url, 'POST'),   1)
        self.assertEqual(self.go(url, 'GET'),    2)
        self.assertEqual(self.go(url, 'PUT'),    3)
        self.assertEqual(self.go(url, 'DELETE'), 4)

    def test_mocked_code_data(self):
        """Different mocked response codes for different data passed"""
        # Arrange
        url = 'duckduckgo.com/html'
        method = 'POST'

        mock_one = MockResponse()
        mock_one.http_code = 1
        data_one = dict(foo='bar')
        self.backend.responses.add(mock_one, url, method, data_one)

        mock_two = MockResponse()
        mock_two.http_code = 2
        data_two = dict(bar='foo')
        self.backend.responses.add(mock_two, url, method, data_two)

        # Act, Assert
        self.assertEqual(self.go(url, method, data_one), 1)
        self.assertEqual(self.go(url, method, data_two), 2)

    def test_no_choices(self):
        """If there are no choices set, raise an exception"""
        self.assertRaises(LookupError, self.go, "someurl")

    def test_match_data(self):
        """Pick the best data match"""
        url = 'form'
        form = MockResponse()
        form.src = """
            <form method="post">
                <input type="text" name="one" value="one" />
                <input type="text" name="two" value="two" />
                <input type="text" name="three" value="three" />
                <input type="submit" />
            </form>
        """
        right = MockResponse()
        right.src = "right"
        wrong = MockResponse()
        wrong.src = "wrong"

        self.backend.responses.add(form, url)
        self.backend.responses.add(wrong, url, 'POST', dict(one="one"))
        self.backend.responses.add(wrong, url, 'POST', dict(two="two"))
        self.backend.responses.add(right, url, 'POST', dict(one="one", two="two"))
        self.backend.responses.add(wrong, url, 'POST', dict(three="three"))

        self.browser.go(url)
        self.browser.form_select(0)
        self.browser.form_submit()
        self.assertEqual(right.src, self.browser.src)

    def test_no_match_data(self):
        """Error when no canned data matches"""
        url = 'form'
        form = MockResponse()
        form.src = """
            <form method="post">
                <input type="text" name="one" value="one" />
                <input type="text" name="two" value="two" />
                <input type="text" name="three" value="three" />
                <input type="submit" />
            </form>
        """
        wrong = MockResponse()
        wrong.src = "wrong"

        self.backend.responses.add(form, url)
        self.backend.responses.add(wrong, url, 'POST', dict(four="four"))

        self.browser.go(url)
        self.browser.form_select(0)
        self.assertRaises(LookupError, self.browser.form_submit)

    def test_string_data(self):
        """Data passed as a string should be compared one-to-one"""
        mock = MockResponse()
        mock.http_code = 200
        url = 'mock'
        method = 'POST'
        data = "abc123"
        self.backend.responses.add(mock=mock, url=url, method=method, data=data)
        self.assertEqual(self.go(url=url, method=method, data=data), 200)

    def test_header_passed(self):
        """Pass a header and make sure the correct data comes back"""
        right = MockResponse()
        wrong = MockResponse()
        right.src = "right"
        wrong.src = "wrong"
        headers_for_right = dict(a=1, b=2)
        url = "header"
        self.backend.responses.add(right, url, headers=headers_for_right)
        self.backend.responses.add(wrong, url)
        self.go(url=url, headers=headers_for_right)
        self.assertEqual(self.backend.src, right.src)

    def test_returned_headers(self):
        """Set some headers in the mock and check they are passed back"""
        # Arrange
        mock = MockResponse()
        mock.headers = dict(a=1, b=2)

        url = ""

        self.backend.responses.add(mock, url)

        # Act
        self.go(url)

        # Assert
        self.assertEqual(self.backend.headers, mock.headers)
