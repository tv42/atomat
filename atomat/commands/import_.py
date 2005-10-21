import sys, os
from twisted.python import usage
from nevow import rend, loaders
import atomat

class Atom(rend.Page):
    docFactory = loaders.xmlfile('feed.xml',
                templateDir=os.path.join(
        os.path.split(os.path.abspath(atomat.__file__))[0],
        'html'))

    def data_feed(self, ctx, data):
        return {'updated': '2005-10-21T18:30:02Z',
                'entries': [
            {'id': 'foo',
             'title': 'Foo',
             'updated': '2005-09-30T12:03:00Z',
             'content': 'foo',
             },
            {'id': 'bar',
             'title': 'Bar',
             'updated': '2005-10-21T18:30:02Z',
             'content': 'bar',
             },
            ],
                }

OUTPUT = sys.stdout

class Import(usage.Options):
    """Convert a tree of files to Atom"""

    src = None

    def parseArgs(self, src=None):
        if src is None:
            raise usage.UsageError, "source directory is missing"
        self.src = src

    def _print(self, result):
        OUTPUT.write(result)
        OUTPUT.write('\n') # I want a final newline in there.

    def run(self):
        a = Atom()
        d = a.renderString()
        d.addCallback(self._print)
        return d

    def complete(self, pre, post):
        return [] #TODO filename completion?

