# coding: utf-8
# Copyright (C) Adam Piper, 2012
# See COPYING for licence details (GNU AGPLv3)

"""
A python web browser for scraping purposes.
Includes canned responses for testing.
"""

from urllib import urlencode
from .backend import HttpBackend, CurlBackend

def url_for_get(url, data):
    """Encode the given data onto a URL"""
    sep = '&' if '?' in url else '?'
    url = "%(current)s%(sep)s%(data)s" % {'current': url,
                                          'sep'    : sep,
                                          'data'   : urlencode(data)}

    return url

class Browser(HttpBackend):

    """
    Emulate a normal browser.

    A lazy-loading backend-agnostic minimal web browser.
    """

    def __init__(self, url=None, backend=CurlBackend()):
        self._backend = backend

        self.retries = 0
        self.follow = True
        self.debug = False
        # TODO: come up with a new user-agent, supply version
        self.agent = "Mozilla/5.0 (X11; Linux i686) " +\
                     "AppleWebKit/534.24 (KHTML, like Gecko) " +\
                     "Ubuntu/10.10 Chromium/11.0.696.65 " +\
                     "Chrome/11.0.696.65 Safari/534.24"

        self._reset_state()

        if url is not None:
            self.go(url)

    def _reset_state(self):
        """Clear out the browser state"""
        self._tree = None
        self._form = None
        self._form_data = {}

    @property
    def roundtrip(self):
        """Read-only request roundtrip timing"""
        return self._backend.roundtrip

    @property
    def headers(self):
        """Read-only headers dict"""
        return self._backend.headers

    def go(self,
           url,
           method='GET',
           data=None,
           headers=None,
           follow=None,
           agent=None,
           retries=None,
           debug=None):
        """Go to a url, return the HTTP response code"""
        method = method.upper()

        if data is not None and method == 'GET':
            url = url_for_get(url, data)
            data = None

        self._backend.go(url=url,
                         method=method,
                         data=data,
                         headers=headers,
                         follow=follow or self.follow,
                         retries=retries or self.retries,
                         agent=agent or self.agent,
                         debug=debug or self.debug)

        self._reset_state()

        return self.http_code

    def save(self, filename):
        """Save the current page"""
        with open(filename, 'w') as fp:
            fp.write(self.src)

    def save_pretty(self, filename):
        """Save the current page, after lxml has prettified it"""
        self.parse()

        # lazy-load LXML
        from lxml.builder import ET
        with open(filename, 'w') as fp:
            fp.write(ET.tostring(self._tree, pretty_print=True))

    def parse(self):
        """Parse the current page into a node tree"""
        if self._tree is not None:
            return

        # lazy-load LXML
        from lxml.html import fromstring
        self._tree = fromstring(self.src)
        self._tree.make_links_absolute(self.url)

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
                                           if idx in
                                              (f.get('name'),
                                               f.get('id'))][0]['__number']]

        self._form_data = dict(self.form_fields)

        # set the default values for all dropdowns in this form
        for d in self.form_dropdowns:
            self.form_fill_dropdown(d)

    def form_data_update(self, **kwargs):
        """Check that a form is selected, and update the state"""
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms
        self._form_data.update(kwargs)

    def _form_dropdown_options_raw(self, select_name):
        """Get the options for a dropdown"""
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms
        return self._form.xpath('.//select[@name="%s"]//option' % select_name)

    def form_dropdown_options(self, select_name):
        """List options for the given dropdown"""
        return dict(((o.text, o.get('value')) for o in
                    self._form_dropdown_options_raw(select_name)))

    def form_fill_dropdown(self, select_name, option_title=None):
        """Fill the value for a dropdown"""

        nodes = self._form_dropdown_options_raw(select_name)
        if option_title is None:
            node = nodes[0]
        else:
            node = [n for n in nodes if n.text == option_title][0]

        self.form_data_update(**{select_name:node.get('value')})

    def form_submit(self, submit_button=None):
        """
        Submit the currently selected form with the given (or the first)
        submit button.
        """
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms

        submits = self.form_submits
        assert len(submits) <= 1 or submit_button is not None, \
                               "Implicit submit is not possible; " + \
                               "an explicit choice must be passed: %s" % submits
        if len(submits) > 0:
            try:
                submit = submits[0 if submit_button is None else submit_button]
            except TypeError:
                # perhaps we've been given a name/id
                submit = submits[[s for s in submits
                                  if submit_button in
                                      s.values()][0]['__number']]

            if 'name' in submit:
                self.form_data_update(**{submit['name']: submit['value']
                                                         if 'value' in submit
                                                         else ''})

        action = self._form.action if   self._form.action is not None\
                                   else self.url

        return self.form_submit_data(action,
                                     self._form.method,
                                     self._form_data)

    def form_submit_no_button(self):
        """
        Submit the currently selected form, but don't use a button to do it.
        """
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms
        return self.form_submit_data(self._form.action,
                                     self._form.method,
                                     self._form_data)

    def form_submit_data(self, action, method, data):
        """Submit data, intelligently, to the given action URL"""
        assert action is not None, "action must be supplied"
        assert method is not None, "method must be supplied"
        return self.go(action, method=method, data=data)

    def follow_link(self, name_or_xpath):
        """Emulate clicking a link"""
        if name_or_xpath[0] == '/':
            xpath = name_or_xpath
        else:
            xpath = '//*[text()="%s"]/ancestor::a' % name_or_xpath
        link = self.xpath(xpath)[0]
        return self.go(link.get('href'))

    # helpers

    @property
    def http_code(self):
        """Read-only last HTTP response code"""
        return self._backend.http_code

    @property
    def src(self):
        """Read-only page-source"""
        return self._backend.src

    @property
    def url(self):
        """Read-only current URL"""
        return self._backend.url

    @property
    def title(self):
        """Read-only convenience for getting the HTML title"""
        self.parse()
        try:
            return self._tree.xpath("/html/head/title/text()")[0].strip()
        except IndexError:
            return None

    @property
    def forms(self):
        """Convenience for grabbing the HTML form nodes"""
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
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms
        return self._form.xpath('.//select')

    @property
    def form_dropdowns(self):
        """Names of dropdowns for selected form"""
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms
        return (s.get('name') for s in self.form_dropdowns_nodes)

    @property
    def form_fields(self):
        """Dict of fields and values for selected form"""
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms
        return dict((pair for pair in self._form.fields.items()
                          if pair[0] != ''))

    @property
    def form_submits(self):
        """Dict of submits for selected form"""
        assert self._form is not None, \
            "A form must be selected: %s" % self.forms

        submit_lst = self._form.xpath(".//input[@type='submit']")
        assert len(submit_lst) > 0, \
            "The selected form must contain a submit button"

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
