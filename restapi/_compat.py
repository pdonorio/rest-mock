# -*- coding: utf-8 -*-
"""

Found this file reading this interesting post about code working with both
python2 and python3
http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/

Note: i downloaded this file with the command
$ svn export https://github.com/mitsuhiko/jinja2/trunk/jinja2/_compat.py

Note to note: it is not possible to do the same with git on github,
read the stack overflow question about it:
http://stackoverflow.com/a/18324458/2114395

    jinja2._compat
    ~~~~~~~~~~~~~~

    Some py2/py3 compatibility support based on a stripped down
    version of six so we don't have to depend on a specific version
    of it.

    :copyright: Copyright 2013 by the Jinja team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import sys

PY2 = sys.version_info[0] == 2
PYPY = hasattr(sys, 'pypy_translation_info')
_identity = lambda x: x


if not PY2:
    unichr = chr
    range_type = range
    text_type = str
    string_types = (str,)
    integer_types = (int,)

    iterkeys = lambda d: iter(d.keys())
    itervalues = lambda d: iter(d.values())
    iteritems = lambda d: iter(d.items())

    import pickle
    from io import BytesIO, StringIO
    NativeStringIO = StringIO

    def reraise(tp, value, tb=None):
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    ifilter = filter
    imap = map
    izip = zip
    intern = sys.intern

    implements_iterator = _identity
    implements_to_string = _identity
    encode_filename = _identity
    get_next = lambda x: x.__next__

else:
    unichr = unichr
    text_type = unicode
    range_type = xrange
    string_types = (str, unicode)
    integer_types = (int, long)

    iterkeys = lambda d: d.iterkeys()
    itervalues = lambda d: d.itervalues()
    iteritems = lambda d: d.iteritems()

    import cPickle as pickle
    from cStringIO import StringIO as BytesIO, StringIO
    NativeStringIO = BytesIO

    exec('def reraise(tp, value, tb=None):\n raise tp, value, tb')

    from itertools import imap, izip, ifilter
    intern = intern

    def implements_iterator(cls):
        cls.next = cls.__next__
        del cls.__next__
        return cls

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode('utf-8')
        return cls

    get_next = lambda x: x.next

    def encode_filename(filename):
        if isinstance(filename, unicode):
            return filename.encode('utf-8')
        return filename


def with_metaclass(meta, *bases):
    """Create a base class with a metaclass."""
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.
    class metaclass(type):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})


try:
    from urllib.parse import quote_from_bytes as url_quote
except ImportError:
    from urllib import quote as url_quote

"""
jinja2$ grep _compat *

_compat.py:    jinja2._compat
_stringdefs.py:from jinja2._compat import unichr
bccache.py:from jinja2._compat import BytesIO, pickle, PY2, text_type
compiler.py:from jinja2._compat import range_type, text_type, string_types, \
debug.py:from jinja2._compat import iteritems, reraise, PY2
defaults.py:from jinja2._compat import range_type
environment.py:from jinja2._compat import imap, ifilter, string_types, iteritems, \
exceptions.py:from jinja2._compat import imap, text_type, PY2, implements_to_string
ext.py:from jinja2._compat import with_metaclass, string_types, iteritems
filters.py:from jinja2._compat import imap, string_types, text_type, iteritems
lexer.py:from jinja2._compat import iteritems, implements_iterator, text_type, \
loaders.py:from jinja2._compat import string_types, iteritems
meta.py:from jinja2._compat import string_types
nodes.py:from jinja2._compat import izip, with_metaclass, text_type
parser.py:from jinja2._compat import imap
runtime.py:from jinja2._compat import imap, text_type, iteritems, \
sandbox.py:from jinja2._compat import string_types, PY2
tests.py:from jinja2._compat import text_type, string_types, integer_types
utils.py:from jinja2._compat import text_type, string_types, implements_iterator, \

"""