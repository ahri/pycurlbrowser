from unittest import TestCase
from pycurlbrowser import Browser, MockBackend, MockResponse

class TestBackendApi(TestCase):

    """
    Test that the HttpBackend API is adhered-to.
    """

    def setUp(self):
        self.backend = MockBackend()
        self.browser = Browser(backend=self.backend)

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
        self.browser.go(url, method, data, headers, follow, agent, retries, debug)
        return url, mock

    def test_go(self):
        self.mocked_visit()

    def test_src(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.browser.src, mock.src)

    def test_url(self):
        url, _ = self.mocked_visit()
        self.assertEqual(self.browser.url, url)

    def test_roundtrip(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.browser.roundtrip, mock.roundtrip)

    def test_http_code(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.browser.http_code, mock.http_code)

    def test_headers(self):
        _, mock = self.mocked_visit()
        self.assertEqual(self.browser.headers, mock.headers)

class TestForms(TestCase):

    """
    Tests around form behaviour.
    """

    def setUp(self):
        self.backend = MockBackend()
        self.browser = Browser(backend=self.backend)

    def test_no_method(self):
        """When no method is specified in a form the default should be GET"""
        form = MockResponse()
        form.src = """
            <form>
                <input type="hidden" name="name" value="value" />
                <input type="submit" />
            </form>
        """
        self.backend.responses.add(form, 'form')
        self.backend.responses.add(form, 'form?name=value', 'GET')
        self.browser.go('form')
        self.browser.form_select(0)
        self.browser.form_submit()

    def test_no_action(self):
        """When no action is specified in a form the URL should be replicated"""
        url = 'form'
        form = MockResponse()
        form.src = """
            <form method="post">
                <input type="submit" />
            </form>
        """
        self.backend.responses.add(form, url)
        self.backend.responses.add(form, url, 'POST', dict())
        self.browser.go(url)
        self.browser.form_select(0)
        self.browser.form_submit()
