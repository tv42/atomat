import sys, os
from twisted.python import usage
from nevow import rend, loaders
import atomat
from atomat import rst2entry

def readEntries(path):
    for filename in os.listdir(path):
        if (filename.startswith('.')
            or filename.startswith('#')
            or filename.startswith('_')):
            continue
        if not filename.endswith('.rst'):
            continue
        f = file(os.path.join(path, filename))
        s = f.read()
        f.close()
        yield rst2entry.convertString(s, id=filename[:-len('.rst')])

def readFeed(path):
    f = file(os.path.join(path, '_feed.rst'))
    s = f.read()
    f.close()
    atom = rst2entry.convertString(s)
    atom.entries = list(readEntries(path))
    # newest-first is often wanted for website output,
    # so let's just default to that
    atom.entries.sort()
    atom.entries.reverse()
    return atom

class Atom(rend.Page):
    docFactory = loaders.xmlfile('feed.xml',
                templateDir=os.path.join(
        os.path.split(os.path.abspath(atomat.__file__))[0],
        'html'))

    path = None

    def __init__(self, **kwargs):
        path = kwargs.pop('path', None)
        if path is not None:
            self.path = path
        super(Atom, self).__init__(**kwargs)

    def data_feed(self, ctx, data):
        return readFeed(self.path)

    def render_timestamp(self, ctx, data):
        return ctx.tag.clear()[data.strftime('%Y-%m-%dT%H:%M:%SZ')]

    def render_if(self, context, data):
        r=context.tag.allPatterns(str(bool(data)))
        return context.tag.clear()[r]

OUTPUT = sys.stdout

class Import(usage.Options):
    """Convert a tree of files to Atom"""

    path = None

    def parseArgs(self, path=None):
        if path is None:
            raise usage.UsageError, "source directory is missing"
        self.path = path

    def _print(self, result):
        OUTPUT.write(result)
        OUTPUT.write('\n') # I want a final newline in there.

    def run(self):
        a = Atom(path=self.path)
        d = a.renderString()
        d.addCallback(self._print)
        return d

    def complete(self, pre, post):
        return [] #TODO filename completion?

