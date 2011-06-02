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
        self._curl = pycurl.Curl() # note: this is an "easy" connection
        self._curl.setopt(pycurl.FOLLOWLOCATION, 1) # follow location headers
        self._curl.setopt(pycurl.AUTOREFERER, 1)
        self._curl.setopt(pycurl.MAXREDIRS, 20)
        self._curl.setopt(pycurl.ENCODING, "gzip")
        self._buf = StringIO.StringIO()
        self._curl.setopt(pycurl.WRITEFUNCTION, self._buf.write) # callback for content buffer
        self._curl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (X11; Linux i686) AppleWebKit/534.24 (KHTML, like Gecko) Ubuntu/10.10 Chromium/11.0.696.65 Chrome/11.0.696.65 Safari/534.24")
        self._curl.setopt(pycurl.COOKIEFILE, "") # use cookies
        self.reset()

    def reset(self):
        self._tree = None
        self._form = None
        self._curl.setopt(pycurl.POST, 0)
        self._form_data = {}

    def go(self, url):
        self._buf.truncate(0)
        self._curl.setopt(pycurl.URL, url)

        # execute
        try:
            self._curl.perform()
        except pycurl.error, e:
            code, message = e
            if code == 60:
                # SSL cert error; retry
                self._curl.perform()
            else:
                raise e

        self.reset()
        return self._curl.getinfo(pycurl.RESPONSE_CODE)

    def save(self, filename):
        with open(filename, 'w') as fp:
            fp.write(self._buf.getvalue())

    def parse(self):
        if self._tree is not None:
            return

        self._tree = fromstring(self._buf.getvalue())
        self._tree.make_links_absolute(self._curl.getinfo(pycurl.EFFECTIVE_URL))

    # form selection/submission

    def select_form(self, idx):
        self.parse()
        self._form = self._tree.forms[idx]

    def __setitem__(self, *args, **kwargs):
        self._form_data.__setitem__(*args, **kwargs)

    def set_data(self, **kwargs):
        self._form_data.update(kwargs)

    def get_form_fields(self):
        return dict(self._form.form_values())

    def submit(self, submit_num = None):
        data = self.get_form_fields()

        submits = self.submits
        assert len(submits) == 1 or submit_num is not None, "Implicit submit is not possible; an explicit choice must be passed: %s" % submits
        submit = submits[0 if submit_num is None else submit_num]
        data[submit['name']] = submit['value'] if 'value' in submit else ''

        if self._form_data:
            data.update(self._form_data)

        data = urlencode(data)

        if self._form.method.upper() == 'POST':
            self._curl.setopt(pycurl.POST, 1)
            self._curl.setopt(pycurl.POSTFIELDS, data)

            return self.go(self._form.action)

        sep = '?' if self._form.action.find('?') == -1 else '&'
        return self.go("%(current)s%(sep)s%(data)s" % {'current': self._form.action,
                                                       'sep'    : sep,
                                                       'data'   : data})

    def post(self, url, data):
        data = urlencode(data)
        self._curl.setopt(pycurl.POST, 1)
        self._curl.setopt(pycurl.POSTFIELDS, data)
        return self.go(url)

    # helpers

    @property
    def url(self):
        return self._curl.getinfo(pycurl.EFFECTIVE_URL)

    @property
    def title(self):
        self.parse()
        return self._tree.xpath("/html/head/title/text()")[0].strip()

    @property
    def forms(self):
        self.parse()
        forms = []
        for i, form in enumerate(self._tree.forms):
            items = {'form_number': i}
            for name, value in form.items():
                if name in ('name', 'id', 'class'):
                    items[name] = value
            forms.append(items)
        return forms

    @property
    def submits(self):
        assert self._form is not None, "A form must be selected: %s" % self.forms

        submit_lst = self._form.xpath("//input[@type='submit']")
        assert len(submit_lst) > 0, "The selected form must contain a submit button"

        submits = []
        for i, submit in enumerate(submit_lst):
            items = {'submit_number': i}
            for name, value in submit.items():
                if name in ('name', 'value'):
                    items[name] = value
            submits.append(items)
        return submits

    def xpath(self, *argv, **kwargs):
        self.parse()
        return self._tree.xpath(*argv, **kwargs)

    def set_follow(self, switch):
        self._curl.setopt(pycurl.FOLLOWLOCATION, 1 if switch else 0)

    def set_debug(self, switch):
        def debug(typ, msg):
            indicators = {pycurl.INFOTYPE_TEXT:       '%',
                          pycurl.INFOTYPE_HEADER_IN:  '<',
                          pycurl.INFOTYPE_HEADER_OUT: '>',
                          pycurl.INFOTYPE_DATA_OUT:   '>>'}
            if typ in indicators.keys():
                print "%(ind)s %(msg)s" % {'ind': indicators[typ], 'msg': msg.strip()}

        self._curl.setopt(pycurl.VERBOSE, 1 if switch else 0)
        self._curl.setopt(pycurl.DEBUGFUNCTION, debug)
