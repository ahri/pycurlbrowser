# coding: utf-8

"""
REST functionality based off pycurlbrowser's Browser.
"""

try:
    import simplejson as json
except ImportError:
    import json
from . import Browser

class StatusInformational(Exception):

    """
    Represent 1xx status codes
    """

class StatusRedirection(Exception):

    """
    Represent 3xx status codes
    """

class StatusClientError(Exception):

    """
    Represent 4xx status codes
    """

class StatusServerError(Exception):

    """
    Represent 5xx status codes
    """

def status_factory(status):
    """Create exceptions based on HTTP status codes"""
    if   100 <= status < 200:
        return StatusInformational()
    elif 300 <= status < 400:
        return StatusRedirection()
    elif 400 <= status < 500:
        return StatusClientError()
    elif 500 <= status < 600:
        return StatusServerError()

    raise ValueError("Unsupported error code: %d" % status)


class RestClient(Browser):

    """
    A simple REST client based upon pycurlbrowser
    """

    def __init__(self, base, *args, **kwargs):
        super(RestClient, self).__init__(*args, **kwargs)
        self.base = base

    def go(self, obj, method, uid=None, data=None, headers=None):
        url = '%(base)s/%(obj)s' % {'base': self.base,
                                    'obj' : obj}
        if uid is not None:
            url += '/%s' % uid

        super(RestClient, self).go(url=url,
                                   method=method,
                                   data=data,
                                   headers=headers)
        if self.http_code != 200:
            raise status_factory(self.http_code)

        return self.http_code

    # CRUD

    def create(self, obj, data=None, headers=None):
        """Create (POST)"""
        self.go(obj, 'POST', data=data, headers=headers)
        return self.src

    def read(self, obj, uid=None, headers=None):
        """Read (GET)"""
        self.go(obj, 'GET', uid=uid, headers=headers)
        return self.src

    def head(self, obj, uid=None, headers=None):
        """Head (HEAD)"""
        # TODO: care about headers
        # TODO: think about self._curl.setopt(pycurl.NOBODY, 1)
        self.go(obj, 'HEAD', uid=uid, headers=headers)

    def update(self, obj, uid, data=None, headers=None):
        """Update (PUT)"""
        self.go(obj, 'PUT', uid=uid, data=data, headers=headers)
        return self.src

    def destroy(self, obj, uid, headers=None):
        """Destroy (DELETE)"""
        # TODO: care about headers
        self.go(obj, 'DELETE', uid=uid, headers=headers)
        return self.src

class RestClientJson(RestClient):

    """
    A REST client that only speaks JSON
    """

    def create(self, obj, data=None):
        """Create (POST)"""
        res = super(RestClientJson, self).create(obj, json.dumps(data), headers={'Content-Type': 'text/json'})
        if len(res) > 0:
            return json.loads(res)
        return None

    def read(self, obj, uid=None):
        """Read (GET)"""
        return json.loads(super(RestClientJson, self).read(obj, uid))

    def update(self, obj, uid, data=None):
        """Update (PUT)"""
        res = super(RestClientJson, self).update(obj, uid, json.dumps(data), headers={'Content-Type': 'text/json'})
        if len(res) > 0:
            return json.loads(res)
        return None

    def destroy(self, obj, uid):
        """Destroy (DELETE)"""
        res = super(RestClientJson, self).destroy(obj, uid)
        if len(res) > 0:
            return json.loads(res)
        return None
