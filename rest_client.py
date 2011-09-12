# coding: utf-8
from browser import Browser
import pycurl
import simplejson as json

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
    if   100 <= status < 200:
        return StatusInformational()
    elif 300 <= status < 400:
        return StatusRedirection()
    elif 400 <= status < 500:
        return StatusClientError()
    elif 500 <= status < 600:
        return StatusServerError()

    raise ValueError("I only deal with HTTP statuses in ranges I understand, and not success")


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
        if res != 200:
            raise status_factory(res)
        return res

    # CRUD

    def create(self, obj, data=None):
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'POST')
        self._curl.setopt(pycurl.POSTFIELDS, data)
        self.go(obj)
        return self.src

    def read(self, obj, uid=None):
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'GET')
        self.go(obj, uid)
        return self.src

    def head(self, obj, uid=None):
        # TODO: care about headers
        self._curl.setopt(pycurl.NOBODY, 1)
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'HEAD')
        self.go(obj, uid)

    def update(self, obj, uid, data=None):
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'PUT')
        self._curl.setopt(pycurl.POSTFIELDS, data)
        self.go(obj, uid)
        return self.src

    def destroy(self, obj, uid):
        # TODO: care about headers
        self._curl.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
        self.go(obj, uid)
        return self.src

class RestClientJson(RestClient):

    """
    A REST client that only speaks JSON
    """

    def create(self, obj, data=None):
        self._curl.setopt(pycurl.HTTPHEADER, ['Content-Type: text/json'])
        res = super(RestClientJson, self).create(obj, json.dumps(data))
        if len(res) > 0:
            return json.loads(res)
        return None

    def read(self, obj, uid=None):
        return json.loads(super(RestClientJson, self).read(obj, uid))

    def update(self, obj, uid, data=None):
        self._curl.setopt(pycurl.HTTPHEADER, ['Content-Type: text/json'])
        res = super(RestClientJson, self).update(obj, uid, json.dumps(data))
        if len(res) > 0:
            return json.loads(res)
        return None

    def destroy(self, obj, uid):
        res = super(RestClientJson, self).destroy(obj, uid)
        if len(res) > 0:
            return json.loads(res)
        return None
