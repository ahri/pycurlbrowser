# coding: utf-8

from datetime import timedelta
from .base import HttpBackend

class MockResponse(object):

    """
    A fictional response predominantly for testing purposes.
    """

    def __init__(self):
        """Set up some defaults"""
        self.http_code = 200
        self.exception = None
        self.roundtrip = timedelta()
        self.headers = dict()
        self.redirect = None
        self.src = ''

class ResponseCollection(object):

    def __init__(self):
        self._responses = []

    def add(self, mock, url, method='GET', data=None, headers=None):
        """Store a mock response."""
        self._responses.append(dict(mock=mock,
                                    url=url,
                                    method=method,
                                    data=data if not self._empty(data) else None,
                                    headers=headers))

    @staticmethod
    def _to_set(dictionary):
        """Turn a dictionary into a set"""
        return set(['='.join(map(str, p)) for p in dictionary.items()])

    @staticmethod
    def _empty(v):
        """Is a var empty? PHP stylee"""
        return v is None or len(v) == 0

    def get(self, url, method, data, headers):
        """
        Get a matching response, where the url, method and headers match exactly
        and the data is matched on a best-case basis.
        """
        data = data if not self._empty(data) else None

        # reduce
        potentials = [r for r in self._responses if \
            r['url'] == url and \
            r['method'] == method and \
            r['headers'] == headers]

        try:
            # ideally we don't have to best-match the data
            # like if it's None
            if data is None:
                potentials_no_data = [p
                                      for p in potentials
                                      if p['data'] is None]
                if len(potentials_no_data) == 1:
                    return potentials_no_data[0]['mock']
                else:
                    raise LookupError()

            # or if it's a string
            if type(data) is str:
                potentials_str_data = [p
                                      for p in potentials
                                      if p['data'] == data]
                if len(potentials_str_data) == 1:
                    return potentials_str_data[0]['mock']
                else:
                    raise LookupError()

            # of well, best-match it is
            def difference_size(p):
                return len(reference.difference(self._to_set(p['data'])))

            # reduce by matching data
            reference = self._to_set(data)
            potentials_with_crossover = [p
                for p in potentials
                if len(reference.intersection(self._to_set(p['data']))) > 0]
            return min(potentials_with_crossover, key=difference_size)['mock']

        except (LookupError, AttributeError, ValueError):
            raise LookupError("Could not make a choice with " + \
                    "input data: %s, from choices: %s" %
                        (dict(url=url,
                              method=method,
                              data=data,
                              headers=headers),
                         [dict(url=r['url'],
                               method=r['method'],
                               data=r['data'],
                               headers=r['headers'])
                          for r in self._responses]))

class MockBackend(HttpBackend):

    """
    Mock response backend
    """

    def __init__(self, *args, **kwargs):
        super(MockBackend, self).__init__(*args, **kwargs)

        self.responses = ResponseCollection()
        self._resp = None
        self._url = None

    def go(self, url, method, data, headers, follow, agent, retries, debug):
        """Visit a URL"""

        # pick the best-matching MockResponse
        self._resp = self.responses.get(url, method, data, headers)

        if self._resp.exception is not None:
            raise self._resp.exception

        self._url = url

        # redirect (recurse) if neccessary
        if follow and self._resp.redirect is not None:
            self.go(self._resp.redirect, method, data, headers)

    @property
    def src(self):
        """Read-only page-source"""
        return self._resp.src

    @property
    def url(self):
        """Read-only current URL"""
        return self._url

    @property
    def roundtrip(self):
        """Read-only request roundtrip timing"""
        return self._resp.roundtrip

    @property
    def http_code(self):
        """Read-only last HTTP response code"""
        return self._resp.http_code

    @property
    def headers(self):
        """Read-only headers dict"""
        return self._resp.headers
