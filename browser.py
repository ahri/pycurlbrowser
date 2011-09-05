# Copyright (C) Adam Piper, 2012
# See COPYING for licence details (GNU AGPLv3)

import pycurl
import StringIO
from lxml.html import fromstring
from urllib import urlencode
from datetime import datetime

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
        self._curl.setopt(pycurl.CONNECTTIMEOUT, 2)
        self._curl.setopt(pycurl.TIMEOUT, 4);
        self.reset()

    def reset(self):
        self._tree = None
        self._form = None
        self._curl.setopt(pycurl.HTTPGET, 1)
        self._form_data = {}
        self._roundtrip = None

    roundtrip = property(lambda self: self._roundtrip)

    def go(self, url):
        self._buf.truncate(0)
        self._curl.setopt(pycurl.URL, url)

        # execute
        try:
            before = datetime.now()
            self._curl.perform()
        except pycurl.error, e:
            code, message = e
            if code == 60:
                # SSL cert error; retry
                before = datetime.now()
                self._curl.perform()
            else:
                raise e

        self.reset()
        self._roundtrip = datetime.now() - before
        return self._curl.getinfo(pycurl.RESPONSE_CODE)

    def save(self, filename):
        with open(filename, 'w') as fp:
            fp.write(self.src)

    def parse(self):
        if self._tree is not None:
            return

        self._tree = fromstring(self.src)
        self._tree.make_links_absolute(self._curl.getinfo(pycurl.EFFECTIVE_URL))

    # form selection/submission

    def select_form(self, idx):
        self.parse()
        try:
            self._form = self._tree.forms[idx]
        except TypeError:
            # perhaps we've been given a name/id
            if idx is None:
                raise
            self._form = self._tree.forms[filter(lambda f: idx in (f.get('name'), f.get('id')),
                                                 self.forms)[0]['__number']]

    def __setitem__(self, *args, **kwargs):
        self._form_data.__setitem__(*args, **kwargs)

    def set_form_data(self, **kwargs):
        self._form_data.update(kwargs)

    def get_form_fields(self):
        return dict(filter(lambda pair: pair[0] != '', self._form.fields.items()))

    def submit(self, submit_button=None):
        data = self.get_form_fields()

        submits = self.submits
        assert len(submits) <= 1 or submit_button is not None, "Implicit submit is not possible; an explicit choice must be passed: %s" % submits
        if len(submits) > 0:
            try:
                submit = submits[0 if submit_button is None else submit_button]
            except TypeError:
                # perhaps we've been given a name/id
                submit = submits[filter(lambda b: submit_button in b.values(),
                                        submits)[0]['__number']]

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

    def follow_link(self, name_or_xpath):
        if name_or_xpath[0] == '/':
            xpath = name_or_xpath
        else:
            xpath = '//a[text()="%s"]' % name_or_xpath
        link = self.xpath(xpath)[0]
        self.go(link.get('href'))

    # helpers

    @property
    def src(self):
        return self._buf.getvalue()

    @property
    def url(self):
        return self._curl.getinfo(pycurl.EFFECTIVE_URL)

    @property
    def title(self):
        self.parse()
        try:
            return self._tree.xpath("/html/head/title/text()")[0].strip()
        except IndexError:
            return None

    @property
    def forms(self):
        self.parse()
        forms = []
        for i, form in enumerate(self._tree.forms):
            items = {'__number': i}
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
            items = {'__number': i}
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
