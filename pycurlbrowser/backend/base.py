# coding: utf-8

class HttpBackend(object):

    """
    Interface for HTTP backends
    """

    def go(self, url, method, data, headers, follow, agent, retries, debug):
        """
        Visit a URL.

        params:

            url:     URL to request
            method:  HTTP verb to use
            data:    Dict of data to supply, or None
            headers: Dict of headers to supply, or None
            follow:  Whether to automatically follow 3xx responses
            agent:   User agent to supply
            retries: Number of times to try the HTTP request
            debug:   Whether to output debug data
        """
        raise NotImplementedError()

    @property
    def src(self):
        """Read-only page-source"""
        raise NotImplementedError()

    @property
    def url(self):
        """Read-only current URL"""
        raise NotImplementedError()

    @property
    def roundtrip(self):
        """Read-only request roundtrip timing"""
        raise NotImplementedError()

    @property
    def http_code(self):
        """Read-only last HTTP response code"""
        raise NotImplementedError()

    @property
    def headers(self):
        """Read-only headers dict"""
        raise NotImplementedError()
