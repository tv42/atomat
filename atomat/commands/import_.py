import sys, os
from twisted.python import usage
from nevow import rend, loaders, tags
import atomat
from atomat import rst2entry

def readEntries(path):
    for filename in os.listdir(path):
        if (filename.startswith('.')
            or filename.startswith('#')):
            continue
        if not filename.endswith('.rst'):
            continue
        f = file(os.path.join(path, filename))
        s = f.read()
        f.close()
        yield rst2entry.convertString(s, id=filename[:-len('.rst')])

class Atom(rend.Page):
    docFactory = loaders.xmlfile('feed.xml',
                templateDir=os.path.join(
        os.path.split(os.path.abspath(atomat.__file__))[0],
        'html'))

    def __init__(self, src):
        self.src = src
        super(Atom, self).__init__()

    def data_feed(self, ctx, data):
        return {'updated': '2005-10-21T18:30:02Z',
                'entries': readEntries(self.src),
                'title': "Tv's Cobweb",
                }

    def render_dom(self, ctx, data):
        return ctx.tag.clear()[tags.xml(data.dom.toxml())]

    def render_timestamp(self, ctx, data):
        return ctx.tag.clear()[data.strftime('%Y-%m-%dT%H:%M:%SZ')]

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
        a = Atom(self.src)
        d = a.renderString()
        d.addCallback(self._print)
        return d

    def complete(self, pre, post):
        return [] #TODO filename completion?

