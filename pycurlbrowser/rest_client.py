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
    """Post exceptions based on HTTP status codes"""
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

    def post(self, obj, data=None, headers=None):
        """Post"""
        self.go(obj, 'POST', data=data, headers=headers)
        return self.src

    def get(self, obj, uid=None, headers=None):
        """Get"""
        self.go(obj, 'GET', uid=uid, headers=headers)
        return self.src

    def head(self, obj, uid=None, headers=None):
        """Head"""
        # TODO: care about headers
        # TODO: think about self._curl.setopt(pycurl.NOBODY, 1)
        self.go(obj, 'HEAD', uid=uid, headers=headers)

    def put(self, obj, uid, data=None, headers=None):
        """Put"""
        self.go(obj, 'PUT', uid=uid, data=data, headers=headers)
        return self.src

    def delete(self, obj, uid, headers=None):
        """Delete"""
        # TODO: care about headers
        self.go(obj, 'DELETE', uid=uid, headers=headers)
        return self.src

class RestClientJson(RestClient):

    """
    A REST client that only speaks JSON
    """

    def post(self, obj, data=None):
        """Post"""
        res = super(RestClientJson, self).post(obj, json.dumps(data), headers={'Content-Type': 'text/json'})
        if len(res) > 0:
            return json.loads(res)
        return None

    def get(self, obj, uid=None):
        """Get"""
        return json.loads(super(RestClientJson, self).get(obj, uid))

    def put(self, obj, uid, data=None):
        """Put"""
        res = super(RestClientJson, self).put(obj, uid, json.dumps(data), headers={'Content-Type': 'text/json'})
        if len(res) > 0:
            return json.loads(res)
        return None

    def delete(self, obj, uid):
        """Delete"""
        res = super(RestClientJson, self).delete(obj, uid)
        if len(res) > 0:
            return json.loads(res)
        return None
