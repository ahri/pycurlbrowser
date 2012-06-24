# coding: utf-8
from .util import StopWatch

class RequestsBackend(object):

    """
    HTTP backend using Requests
    """

    def __init__(self, *args, **kwargs):
        super(RequestsBackend, self).__init__(*args, **kwargs)
        self._r = None
        self._roundtrip = None
        import requests
        self._session = requests.session()

    def go(self, url, method, data, headers, auth, follow, agent, retries, debug):
        """Visit a URL"""
        with StopWatch() as sw:
            exception = Exception("Dummy exception")

            while retries >= 0 and exception is not None:
                retries -= 1
                try:
                    self._r = self._session.request(method=method,
                                                    url=url,
                                                    data=data,
                                                    headers=headers,
                                                    auth=auth,
                                                    allow_redirects=follow)
                    exception = None
                except Exception, ex:
                    exception = ex

            if exception is not None:
                raise exception

        self._roundtrip = sw.total

    @property
    def src(self):
        """Read-only page-source"""
        return self._r.text

    @property
    def url(self):
        """Read-only current URL"""
        return self._r.url

    @property
    def roundtrip(self):
        """Read-only request roundtrip timing"""
        return self._roundtrip

    @property
    def http_code(self):
        """Read-only last HTTP response code"""
        return self._r.status_code

    @property
    def headers(self):
        """Read-only headers dict"""
        return self._r.headers
