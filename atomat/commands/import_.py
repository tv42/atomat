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
        return {'updated': 'foo',
                'entries': [
            {'id': 'foo',
             'title': 'foo',
             'updated': 'foo',
             'content': 'foo',
             },
            {'id': 'foo',
             'title': 'foo',
             'updated': 'foo',
             'content': 'foo',
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

