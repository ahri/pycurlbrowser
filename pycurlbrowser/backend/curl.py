# coding: utf-8

from urllib import urlencode
import StringIO
from .base import HttpBackend
from .util import StopWatch

class CurlBackend(HttpBackend):

    """
    Curl backend
    """

    def __init__(self, *args, **kwargs):
        super(CurlBackend, self).__init__(*args, **kwargs)

        self._head_buf = StringIO.StringIO()
        self._body_buf = StringIO.StringIO()
        self._roundtrip = None
        self._http_code = None

        import pycurl
        self._pycurl = pycurl

        self._curl = self._pycurl.Curl() # note: this is an "easy" connection
        self._curl.setopt(self._pycurl.AUTOREFERER, 1)
        self._curl.setopt(self._pycurl.MAXREDIRS, 20)
        self._curl.setopt(self._pycurl.ENCODING, "gzip")
        self._curl.setopt(self._pycurl.HEADERFUNCTION,
                          self._head_buf.write) # callback for header buffer
        self._curl.setopt(self._pycurl.WRITEFUNCTION,
                          self._body_buf.write) # callback for content buffer
        self._curl.setopt(self._pycurl.COOKIEFILE, "") # use cookies
        self._curl.setopt(self._pycurl.CONNECTTIMEOUT, 2)
        self._curl.setopt(self._pycurl.TIMEOUT, 4)

    def check_curl(self, item):
        """Convenience method to check whether curl supports a given feature"""
        return item in self._pycurl.version_info()[8]

    def _setup_url(self, url):
        """Pass the url on to curl"""
        self._curl.setopt(self._pycurl.URL, url)

    def _setup_method(self, method):
        """Pass the method on to curl"""
        self._curl.setopt(self._pycurl.CUSTOMREQUEST, method)

    def _setup_data(self, method, data):
        """Preprocess the data if possible, then pass it along to curl"""
        if data is not None and method != 'GET':
            try:
                data = urlencode(data)
            except TypeError:
                # If there's a type error then just pass the data along
                pass

            self._curl.setopt(self._pycurl.POSTFIELDS, data)

    def _setup_headers(self, headers):
        """Convert the data to a list of headers and pass to curl"""
        if headers is not None:
            self._curl.setopt(self._pycurl.HTTPHEADER,
                              [': '.join(map(str, i)) for i in headers.items()])

    def _setup_follow(self, follow):
        """Pass the follow status on to curl"""
        if follow:
            self._curl.setopt(self._pycurl.FOLLOWLOCATION, 1 if follow else 0)

    def _setup_agent(self, agent):
        """Pass the user agent on to curl"""
        self._curl.setopt(self._pycurl.USERAGENT, agent)

    def _setup_debug(self, debug):
        """Pass a pretty helper on to curl for debugging if neccessary"""
        if debug:
            def debug_echo(typ, msg):
                """Closure to pass in that makes debug info more readable"""
                indicators = {self._pycurl.INFOTYPE_TEXT:       '%',
                              self._pycurl.INFOTYPE_HEADER_IN:  '<',
                              self._pycurl.INFOTYPE_HEADER_OUT: '>',
                              self._pycurl.INFOTYPE_DATA_OUT:   '>>'}
                if typ in indicators.keys():
                    print "%(ind)s %(msg)s" % {'ind': indicators[typ],
                                               'msg': msg.strip()}

            self._curl.setopt(self._pycurl.VERBOSE, 1)
            self._curl.setopt(self._pycurl.DEBUGFUNCTION, debug_echo)

        else:
            self._curl.setopt(self._pycurl.VERBOSE, 0)

    def go(self, url, method, data, headers, follow, agent, retries, debug):
        """Visit a URL, return an HTTP response code"""
        self._setup_url(url)
        self._setup_method(method)
        self._setup_data(method, data)
        self._setup_headers(headers)
        self._setup_follow(follow)
        self._setup_agent(agent)
        self._setup_debug(debug)

        self._head_buf.truncate(0)
        self._body_buf.truncate(0)
        with StopWatch() as sw:
            exception = Exception("Dummy exception")

            while retries >= 0 and exception is not None:
                retries -= 1
                try:
                    self._curl.perform()
                    exception = None
                except self._pycurl.error, ex:
                    exception = ex

            if exception is not None:
                raise exception

        self._roundtrip = sw.total

        self._http_code = self._curl.getinfo(self._pycurl.RESPONSE_CODE)

    @property
    def src(self):
        """Read-only page-source"""
        return self._body_buf.getvalue()

    @property
    def url(self):
        """Read-only current URL"""
        return self._curl.getinfo(self._pycurl.EFFECTIVE_URL)

    @property
    def roundtrip(self):
        """Read-only request roundtrip timing"""
        return self._roundtrip

    @property
    def http_code(self):
        """Read-only last HTTP response code"""
        return self._http_code

    @property
    def headers(self):
        """Read-only headers dict"""
        return dict([h for h in [h.split(': ') for h in self._head_buf.getvalue().splitlines()] if len(h) == 2])
