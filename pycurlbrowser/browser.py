# Copyright (C) Adam Piper, 2012
# See COPYING for licence details (GNU AGPLv3)

import pycurl
import StringIO
from lxml.html import fromstring
from urllib import urlencode
from datetime import datetime

class Browser(object):

    """
    Emulate a normal browser

    This class is a convenience on top of libcurl and lxml; it should behave
    like a normal browser (but lacking Javascript), and allow DOM queries.
    """

    @classmethod
    def check_curl(cls, item):
        return item in pycurl.version_info()[8]

    def __init__(self, url=None):
        self.retries = 0
        self._curl = pycurl.Curl() # note: this is an "easy" connection
        self.set_follow(True) # follow location headers
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

        if url is not None:
            self.go(url)

    def reset(self):
        """Clear out the browser state"""
        self._tree = None
        self._form = None
        self._curl.setopt(pycurl.HTTPGET, 1)
        self._form_data = {}
        self._roundtrip = None

    roundtrip = property(lambda self: self._roundtrip)

    def go(self, url):
        """Go to a url"""
        self._buf.truncate(0)
        self._curl.setopt(pycurl.URL, url)

        before = datetime.now()
        retries = self.retries
        exception = True

        while retries >= 0 and exception is not None:
            retries -= 1
            try:
                self._curl.perform()
                exception = None
            except pycurl.error, e:
                exception = e

        if exception is not None:
            raise exception

        self.reset()
        self._roundtrip = datetime.now() - before
        return self._curl.getinfo(pycurl.RESPONSE_CODE)

    def save(self, filename):
        """Save the current page"""
        with open(filename, 'w') as fp:
            fp.write(self.src)

    def save_pretty(self, filename):
        """Save the current page, after lxml has prettified it"""
        self.parse()
        from lxml.builder import ET
        with open(filename, 'w') as fp:
            fp.write(ET.tostring(self._tree, pretty_print=True))

    def parse(self):
        """Parse the current page into a node tree"""
        if self._tree is not None:
            return

        self._tree = fromstring(self.src)
        self._tree.make_links_absolute(self._curl.getinfo(pycurl.EFFECTIVE_URL))

    # form selection/submission

    def form_select(self, idx):
        """Select a form on the current page"""
        self.parse()
        try:
            self._form = self._tree.forms[idx]
        except TypeError:
            # perhaps we've been given a name/id
            if idx is None:
                raise
            self._form = self._tree.forms[[f for f in self.forms
                                           if idx in (f.get('name'), f.get('id'))][0]['__number']]

        self._form_data = dict(self.form_fields)

        # set the default values for all dropdowns in this form
        for d in self.form_dropdowns:
            self.form_fill_dropdown(d)

    def form_data_update(self, **kwargs):
        assert self._form is not None, "A form must be selected: %s" % self.forms
        self._form_data.update(kwargs)

    def _form_dropdown_options_raw(self, select_name):
        assert self._form is not None, "A form must be selected: %s" % self.forms
        return self._form.xpath('.//select[@name="%s"]//option' % select_name)

    def form_dropdown_options(self, select_name):
        """List options for the given dropdown"""
        return dict(((o.text, o.get('value')) for o in self._form_dropdown_options_raw(select_name)))

    def form_fill_dropdown(self, select_name, option_title=None):
        """Fill the value for a dropdown"""

        nodes = self._form_dropdown_options_raw(select_name)
        if option_title is None:
            node = nodes[0]
        else:
            node = [n for n in nodes if n.text == option_title][0]

        self.form_data_update(**{select_name:node.get('value')})

    def form_submit(self, submit_button=None):
        """Submit the currently selected form with the given (or the first) submit button"""
        assert self._form is not None, "A form must be selected: %s" % self.forms

        submits = self.form_submits
        assert len(submits) <= 1 or submit_button is not None, "Implicit submit is not possible; an explicit choice must be passed: %s" % submits
        if len(submits) > 0:
            try:
                submit = submits[0 if submit_button is None else submit_button]
            except TypeError:
                # perhaps we've been given a name/id
                submit = submits[[s for s in submits if submit_button in s.values()][0]['__number']]

            if 'name' in submit:
                self.form_data_update(**{submit['name']: submit['value'] if 'value' in submit else ''})

        return self.form_submit_data(self._form.method, self._form.action, self._form_data)

    def form_submit_no_button(self):
        """Submit the currently selected form, but don't use a button to do it"""
        assert self._form is not None, "A form must be selected: %s" % self.forms
        return self.form_submit_data(self._form.method, self._form.action, self._form_data)

    def form_submit_data(self, method, action, data):
        """Submit data, intelligently, to the given action URL"""
        assert self._form is not None, "A form must be selected: %s" % self.forms
        data = urlencode(data)

        if method.upper() == 'POST':
            self._curl.setopt(pycurl.POST, 1)
            self._curl.setopt(pycurl.POSTFIELDS, data)

            return self.go(self._form.action)

        sep = '?' if action.find('?') == -1 else '&'
        return self.go("%(current)s%(sep)s%(data)s" % {'current': action,
                                                       'sep'    : sep,
                                                       'data'   : data})

    def follow_link(self, name_or_xpath):
        """Emulate clicking a link"""
        if name_or_xpath[0] == '/':
            xpath = name_or_xpath
        else:
            xpath = '//a[text()="%s"]' % name_or_xpath
        link = self.xpath(xpath)[0]
        return self.go(link.get('href'))

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
    def form_dropdowns_nodes(self):
        """Names of dropdowns for selected form"""
        assert self._form is not None, "A form must be selected: %s" % self.forms
        return self._form.xpath('.//select')

    @property
    def form_dropdowns(self):
        """Names of dropdowns for selected form"""
        assert self._form is not None, "A form must be selected: %s" % self.forms
        return (s.get('name') for s in self.form_dropdowns_nodes)

    @property
    def form_fields(self):
        """Dict of fields and values for selected form"""
        assert self._form is not None, "A form must be selected: %s" % self.forms
        return dict((pair for pair in self._form.fields.items() if pair[0] != ''))

    @property
    def form_submits(self):
        """Dict of submits for selected form"""
        assert self._form is not None, "A form must be selected: %s" % self.forms

        submit_lst = self._form.xpath(".//input[@type='submit']")
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
        """Execute an XPATH against the current node tree"""
        self.parse()
        return self._tree.xpath(*argv, **kwargs)

    def set_follow(self, switch):
        """Indicate whether the browser should automatically follow redirect headers"""
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
