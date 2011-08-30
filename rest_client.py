# coding: utf-8
from browser import Browser
import pycurl
import simplejson

class RestClient(Browser):
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
        return simplejson.loads(self.src)

    def head(self, obj, uid=None):
        self._curl.setopt(pycurl.HTTPGET, 1)
        self._curl.setopt(pycurl.NOBODY, 1)
        self.go(obj, uid)
        # TODO: care about headers

    def post(self, obj, data):
        self._curl.setopt(pycurl.HTTPPOST, 1)
        self._curl.setopt(pycurl.POSTFIELDS, simplejson.loads(data))
        return simplejson.loads(self.src)

    def put(self, obj, uid, data):
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
        self._curl.setopt(pycurl.POSTFIELDS, simplejson.loads(data))
        return simplejson.loads(self.src)

    def delete(self, obj, uid):
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        # TODO: care about headers
