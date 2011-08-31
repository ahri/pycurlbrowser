# coding: utf-8
from browser import Browser
import pycurl
import simplejson as json

class RestClient(Browser):

    """
    A simple REST client based upon pycurlbrowser
    """

    def __init__(self, base):
        super(RestClient, self).__init__()
        self._curl.setopt(pycurl.USERAGENT, "pycurl.rest_client 0.1")
        self.base = base

    def go(self, obj, uid=None):
        url = '%(base)s/%(obj)s' % {'base': self.base,
                                    'obj' : obj}
        if uid is not None:
            url += '/%s' % uid

        res = super(RestClient, self).go(url)
        assert res == 200, "Only handle success, not: %d" % res
        return res

    def get(self, obj, uid=None):
        self._curl.setopt(pycurl.HTTPGET, 1)
        self.go(obj, uid)
        return self.src

    def head(self, obj, uid=None):
        # TODO: care about headers
        self._curl.setopt(pycurl.HTTPGET, 1)
        self._curl.setopt(pycurl.NOBODY, 1)
        self.go(obj, uid)

    def post(self, obj, data=None):
        self._curl.setopt(pycurl.POST, 1)
        self._curl.setopt(pycurl.POSTFIELDS, data)
        self.go(obj)
        return self.src

    def put(self, obj, uid, data=None):
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
        self._curl.setopt(pycurl.POSTFIELDS, data)
        self.go(obj, uid)
        return self.src

    def delete(self, obj, uid):
        # TODO: care about headers
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        self.go(obj, uid)
        return self.src

class RestClientJson(RestClient):
    """
    A REST client that only speaks JSON
    """

    def get(self, obj, uid=None):
        return json.loads(super(RestClientJson, self).get(obj, uid))

    def post(self, obj, data=None):
        self._curl.setopt(pycurl.HTTPHEADER, ['Content-Type: text/json'])
        return json.loads(super(RestClientJson, self).post(obj, json.dumps(data)))

    def put(self, obj, uid, data=None):
        self._curl.setopt(pycurl.HTTPHEADER, ['Content-Type: text/json'])
        return json.loads(super(RestClientJson, self).put(obj, uid, json.dumps(data)))

    def delete(self, obj, uid):
        return json.loads(super(RestClientJson, self).delete(obj, uid))
