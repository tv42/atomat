import sys, os
from twisted.python import usage
from nevow import rend, loaders
import atomat
from atomat import rst2entry

def readEntries(path, feedId):
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
        yield rst2entry.convertString(s, id='%s#%s' % (feedId, filename[:-len('.rst')]))

def readFeed(path):
    f = file(os.path.join(path, '_feed.rst'))
    s = f.read()
    f.close()
    atom = rst2entry.convertString(s)
    atom.entries = list(readEntries(path, atom.id))
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

    def render_if_isUpdated(self, ctx, data):
        published = getattr(data, 'published', None)
        if published is None:
            r = False
        else:
            r = (published != data.updated)
        return self.render_if(ctx, r)

OUTPUT = sys.stdout

class Import(usage.Options):
    """Convert a tree of files to Atom"""

    path = None

    optParameters = [
        ('template', None, None,
         'Nevow template file to use.'),
        ]

    def parseArgs(self, path=None):
        if path is None:
            raise usage.UsageError, "source directory is missing"
        self.path = path

    def _print(self, result):
        OUTPUT.write(result)
        OUTPUT.write('\n') # I want a final newline in there.

    def run(self):
        kwargs = {
            'path': self.path,
            }

        template = self.get('template', None)
        if template is not None:
            kwargs['docFactory'] = loaders.xmlfile(template)

        a = Atom(**kwargs)
        d = a.renderString()
        d.addCallback(self._print)
        return d

    def complete(self, pre, post):
        return [] #TODO filename completion?

