import sys, os, sets
from twisted.python import usage
from nevow import rend, loaders
import atomat
from atomat import rst2entry, atom

def badFilename(filename):
    return (filename.startswith('.')
            or filename.startswith('#')
            or filename.startswith('_'))

def walk(path):
    filenames = []
    dirnames = []
    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            dirnames.append(f)
        else:
            filenames.append(f)
    yield '.', dirnames, filenames
    for dirname in dirnames:
        for dirname2, dirs2, files2 in walk(os.path.join(path, dirname)):
            prefix = dirname
            if dirname2 != '.':
                prefix = os.path.join(prefix, dirname2)
            yield prefix, dirs2, files2


def readEntries(path, feedId):
    for dirname, dirs, files in walk(path):
        dirs[:] = [f for f in dirs if not badFilename(f)]
        files[:] = [f for f in files
                    if (not badFilename(f)
                        and f.endswith('.rst'))]
        for filename in files:
            f = file(os.path.join(path, dirname, filename))
            s = f.read()
            f.close()

            href = os.path.join(dirname,
                                (os.path.splitext(filename)[0]
                                 + os.path.extsep
                                 + 'html'))
            link = atom.Link(href=href)

            id_ = ''
            if dirname != '.':
                id_ += dirname.replace('/', '-')+'_'
            id_ += filename[:-len('.rst')]
            id_ = '%s#%s' % (feedId, id_)

            x = rst2entry.convertString(
                s,
                id=id_,
                link=sets.Set([link]))
            yield x
 
def readFeed(path):
    f = file(os.path.join(path, '_feed.rst'))
    s = f.read()
    f.close()
    fake = rst2entry.convertString(s)
    kw = {}
    for k in dir(fake):
        v = getattr(fake, k)
        kw[k] = v
    feed = atom.Feed(entries=readEntries(path, fake.id),
                     **kw)
    return feed

class Atom(rend.Page):
    docFactory = loaders.xmlfile('feed.xml',
                templateDir=os.path.join(
        os.path.split(os.path.abspath(atomat.__file__))[0],
        'html'))

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

    def render_if_hasAlternateLink(self, ctx, data):
        links = getattr(data, 'link', None)
        r = False
        if links is not None:
            for link in links:
                if getattr(link, 'rel', None) == 'alternate':
                    r = True
                    break
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
        kwargs = {}
        template = self.get('template', None)
        if template is not None:
            kwargs['docFactory'] = loaders.xmlfile(template)

        feed = readFeed(self.path)
        a = Atom(feed, **kwargs)
        d = a.renderString()
        d.addCallback(self._print)
        return d

    def complete(self, pre, post):
        return [] #TODO filename completion?

