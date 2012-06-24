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
        def just_args(s):
            return dict(args=s.args, varargs=s.varargs)

        comp = just_args(inspect.getargspec(HttpBackend.go))
        for t in derived_types():
            sig = just_args(inspect.getargspec(t.go))
            self.assertEqual(comp, sig, "Type %(t)s does not adhere to the spec %(spec)s with signature %(sig)s" % dict(t=t, spec=comp, sig=sig))

    def test_properties(self):
        comp = set(dir(HttpBackend))
        for t in derived_types():
            self.assertEqual(comp - set(dir(t)), set())


    def test_properties_overriden(self):
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
