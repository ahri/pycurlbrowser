from unittest import TestCase
from pycurlbrowser import RestClient, RestClientJson, MockBackend, MockResponse
from urllib import urlencode

class TestRest(TestCase):

    """
    Use the mock backend for the Browser to test REST capabilities.
    """

    def setUp(self):
        self.backend = MockBackend()
        self.client = RestClient('http://mocked', backend=self.backend)

    def test_post(self):
        """Positive test for POST"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = 'success'

        url = '%s/object' % self.client.base
        method = 'POST'
        data = urlencode(dict(a=1, b=2, c=3))

        self.backend.responses.add(mock, url, method, data)

        # Act, Assert
        self.assertEqual(self.client.post('object', data), mock.src)

    def test_get(self):
        """Positive test for GET"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = 'success'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'GET'

        self.backend.responses.add(mock, url, method)

        # Act, Assert
        self.assertEqual(self.client.get('object', uid), mock.src)

    def test_head(self):
        """Positive test for HEAD"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = 'failure'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'HEAD'

        self.backend.responses.add(mock, url, method)

        # Act, Assert
        self.assertEqual(self.client.head('object', uid), None)

    def test_put(self):
        """Positive test for PUT"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = 'success'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'PUT'
        data = urlencode(dict(a=1, b=2, c=3))

        self.backend.responses.add(mock, url, method, data)

        # Act, Assert
        self.assertEqual(self.client.put('object', uid, data), mock.src)

    def test_delete(self):
        """Positive test for DELETE"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = 'success'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'DELETE'

        self.backend.responses.add(mock, url, method)

        # Act, Assert
        self.assertEqual(self.client.delete('object', uid), mock.src)

class TestJsonRest(TestCase):

    """
    Use the mock backend for the Browser to test JSON REST capabilities.
    """

    def setUp(self):
        self.backend = MockBackend()
        self.client = RestClientJson('http://mocked', backend=self.backend)

    def test_post(self):
        """Positive test for JSON POST"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = '"success"'
        expected = "success"

        url = '%s/object' % self.client.base
        method = 'POST'
        data = dict(a=1, b=2, c=3)
        expected_data = '{"a": 1, "c": 3, "b": 2}'
        headers = { 'Content-Type': 'text/json' }

        self.backend.responses.add(mock, url, method, expected_data, headers)

        # Act, Assert
        self.assertEqual(self.client.post('object', data), expected, {'Content-Type': 'text/json'})

    def test_get(self):
        """Positive test for JSON GET"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = '"success"'
        expected = "success"

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'GET'

        self.backend.responses.add(mock, url, method)

        # Act, Assert
        self.assertEqual(self.client.get('object', uid), expected)

    def test_head(self):
        """Positive test for JSON HEAD"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = 'failure'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'HEAD'

        self.backend.responses.add(mock, url, method)

        # Act, Assert
        self.assertEqual(self.client.head('object', uid), None)

    def test_put(self):
        """Positive test for JSON PUT"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = '"success"'
        expected = "success"

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'PUT'
        data = dict(a=1, b=2, c=3)
        expected_data = '{"a": 1, "c": 3, "b": 2}'
        headers = { 'Content-Type': 'text/json' }

        self.backend.responses.add(mock, url, method, expected_data, headers)

        # Act, Assert
        self.assertEqual(self.client.put('object', uid, data), expected)

    def test_delete(self):
        """Positive test for JSON DELETE"""
        # Arrange
        mock = MockResponse()
        mock.http_code = 200
        mock.src = '"success"'
        expected = "success"

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'DELETE'

        self.backend.responses.add(mock, url, method)

        # Act, Assert
        self.assertEqual(self.client.delete('object', uid), expected)
