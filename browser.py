# Copyright (C) Adam Piper, 2012
# See COPYING for licence details (GNU AGPLv3)

import pycurl
import StringIO
from lxml.html import fromstring
from urllib import urlencode

class Browser(object):
    @classmethod
    def check_curl(cls, item):
        return item in pycurl.version_info()[8]

    def __init__(self):
        self.curl = pycurl.Curl() # note: this is an "easy" connection
        self.curl.setopt(pycurl.FOLLOWLOCATION, 1) # follow location headers
        self.curl.setopt(pycurl.MAXREDIRS, 5)
        self.buf = StringIO.StringIO()
        self.curl.setopt(pycurl.WRITEFUNCTION, self.buf.write) # callback for content buffer
        self.curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/11.0.696.65 Chrome/11.0.696.65 Safari/534.24")
        self.curl.setopt(pycurl.COOKIEFILE, "") # use cookies
        self.reset()

    def go(self, url):
        self.buf.truncate(0)
        self.curl.setopt(pycurl.URL, url)
        if self.url:
            self.curl.setopt(pycurl.REFERER, self.url)

        self.curl.perform()

        self.reset()
        self.url = self.curl.getinfo(pycurl.EFFECTIVE_URL)
        self.parse()
        return self.curl.getinfo(pycurl.RESPONSE_CODE)

    def save(self, filename):
        with open(filename, 'w') as fp:
            fp.write(self.buf.getvalue())

    def reset(self):
        self.url = None
        self.tree = None
        self.form = None
        self.curl.setopt(pycurl.POST, 0)
        self.form_data = {}

    def parse(self):
        if self.tree is not None:
            return

        self.tree = fromstring(self.buf.getvalue())
        self.tree.make_links_absolute(self.curl.getinfo(pycurl.EFFECTIVE_URL))

    # form selection/submission

    def select_form(self, idx):
        self.parse()
        self.form = self.tree.forms[idx]

    def __setitem__(self, *args, **kwargs):
        self.form_data.__setitem__(*args, **kwargs)

    def set_data(self, **kwargs):
        self.form_data.update(kwargs)

    def get_form_fields(self):
        return self.form.fields

    def submit(self):
        assert self.form is not None, "A form must be selected"

        data = {}
        for key, val in self.form.form_values():
            data[key] = val

        if self.form_data:
            data.update(self.form_data)

        data = urlencode(data)

        if self.form.method.upper() == 'POST':
            self.curl.setopt(pycurl.POST, 1)
            self.curl.setopt(pycurl.POSTFIELDS, data)

            return self.go(self.form.action)

        sep = '?' if self.form.action.find('?') == -1 else '&'
        return self.go("%(current)s%(sep)s%(data)s" % {'current': self.form.action,
                                                       'sep'    : sep,
                                                       'data'   : data})

    def post(self, url, data):
        data = urlencode(data)
        self.curl.setopt(pycurl.POST, 1)
        self.curl.setopt(pycurl.POSTFIELDS, data)
        return self.go(url)
