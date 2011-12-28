from unittest import TestCase
from pycurlbrowser import RestClient, RestClientJson, CannedResponse
from urllib import urlencode

class TestRest(TestCase):

    """
    Use the canned response ability of the Browser to test REST
    capabilities.
    """

    def setUp(self):
        self.client = RestClient('http://canned')

    def test_create(self):
        """Positive test for CREATE"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = 'success'

        url = '%s/object' % self.client.base
        method = 'POST'
        data = urlencode(dict(a=1, b=2, c=3))

        self.client.add_canned_response(can, url, method, data, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.create('object', data), can.src)

    def test_read(self):
        """Positive test for READ"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = 'success'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'GET'

        self.client.add_canned_response(can, url, method, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.read('object', uid), can.src)

    def test_head(self):
        """Positive test for HEAD"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = 'failure'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'HEAD'

        self.client.add_canned_response(can, url, method, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.head('object', uid), None)

    def test_update(self):
        """Positive test for UPDATE"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = 'success'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'PUT'
        data = urlencode(dict(a=1, b=2, c=3))

        self.client.add_canned_response(can, url, method, data, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.update('object', uid, data), can.src)

    def test_delete(self):
        """Positive test for DELETE"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = 'success'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'DELETE'

        self.client.add_canned_response(can, url, method, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.destroy('object', uid), can.src)

class TestJsonRest(TestCase):

    """
    Use the canned response ability of the Browser to test JSON
    REST capabilities.
    """

    def setUp(self):
        self.client = RestClientJson('http://canned')

    def test_create(self):
        """Positive test for JSON CREATE"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = '"success"'
        expected = "success"

        url = '%s/object' % self.client.base
        method = 'POST'
        data = dict(a=1, b=2, c=3)
        expected_data = '{"a": 1, "c": 3, "b": 2}'

        self.client.add_canned_response(can, url, method, expected_data, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.create('object', data), expected)

    def test_read(self):
        """Positive test for JSON READ"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = '"success"'
        expected = "success"

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'GET'

        self.client.add_canned_response(can, url, method, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.read('object', uid), expected)

    def test_head(self):
        """Positive test for JSON HEAD"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = 'failure'

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'HEAD'

        self.client.add_canned_response(can, url, method, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.head('object', uid), None)

    def test_update(self):
        """Positive test for JSON UPDATE"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = '"success"'
        expected = "success"

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'PUT'
        data = dict(a=1, b=2, c=3)
        expected_data = '{"a": 1, "c": 3, "b": 2}'

        self.client.add_canned_response(can, url, method, expected_data, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.update('object', uid, data), expected)

    def test_delete(self):
        """Positive test for JSON DELETE"""
        # Arrange
        can = CannedResponse()
        can.code = 200
        can.src = '"success"'
        expected = "success"

        uid = 1
        url = '%s/object/%s' % (self.client.base, uid)
        method = 'DELETE'

        self.client.add_canned_response(can, url, method, escaped=True)

        # Act, Assert
        self.assertEqual(self.client.destroy('object', uid), expected)
