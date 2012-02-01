# coding: utf-8

"""
Test the backend API

Written so that after creating a new backend, you can immediately see which
parts are missing!
"""

from unittest import TestCase
import inspect
from pycurlbrowser.backend import *
from pycurlbrowser import Browser

def is_http_backend_derived(t):
    if t is HttpBackend:
        return False

    try:
        return HttpBackend in inspect.getmro(t)
    except AttributeError:
        return False

def derived_types():
    return [t for t in globals().values() if is_http_backend_derived(t)]

class ApiTests(TestCase):

    def test_go(self):
        """Ensure that 'go' can be called consistently"""
        comp = set(inspect.getargspec(HttpBackend.go).args)
        for t in derived_types():
            res = comp - set(inspect.getargspec(t.go).args)
            self.assertEqual(res, set(), "Function %(c)s.go is missing params: %(p)s" % dict(c=t.__name__, p=", ".join(res)))

    def test_properties(self):
        """Kinda pointless test given that HttpBackend supplies them all anyway..."""
        comp = set(dir(HttpBackend))
        for t in derived_types():
            res = comp - set(dir(t))
            self.assertEqual(res, set(), "Class %(c)s is missing properties: %(p)s" % dict(c=t.__name__, p=", ".join(res)))


    def test_properties_overriden(self):
        """Check that properties are appropriately overriden"""
        comp = dir(HttpBackend)
        for t in derived_types():
            o = t()
            for p in comp:
                try:
                    getattr(o, p)
                except NotImplementedError:
                    raise NotImplementedError("Property '%(p)s' is not overriden for type %(t)s" % (dict(p=p, t=t)))
                except:
                    pass
