from zope.interface import implements
import sets, re
from atomat import iatom

class XHTMLContent(object):
    implements(iatom.IInlineContent)

    type = 'xhtml'

    def __init__(self, dom):
        self.dom = dom

class Link(object):
    implements(iatom.ILink)

    href = None
    RELATIONSHIPS = sets.ImmutableSet(['alternate',
                                       'enclosure',
                                       'related',
                                       'self',
                                       'via'])
    FULL_URI_RE = re.compile('^[a-z]+:')
    rel = 'alternate'
    type = None
    hreflang = None
    title = None
    length = None

    def __init__(self, **kw):
        self.href = kw.pop('href')

        rel = kw.pop('rel', None)
        if rel is not None:
            assert (rel in self.RELATIONSHIPS
                    or self.FULL_URI_RE.match(rel))
            self.rel = rel

        for a in ['type', 'hreflang', 'title', 'length']:
            v = kw.pop(a, None)
            if v is not None:
                setattr(self, a, v)

        super(Link, self).__init__(**kw)

class Entry(object):
    implements(iatom.IEntry)

    id = None
    title = None
    updated = None

    author = None
    content = None
    link = None
    summary = None

    category = None
    contributor = None
    published = None
    source = None
    rights = None

    def __init__(self, **kw):
        self.id = kw.pop('id')
        self.title = kw.pop('title')
        self.updated = kw.pop('updated')

        for attr in ['author', 'content', 'link', 'summary',
                     'contributor', 'published',
                     'source', 'rights']:
            val = kw.pop(attr, None)
            if val is not None:
                setattr(self, attr, val)

        category = kw.pop('category', None)
        if category is not None:
            self.category = sets.Set(category)

    def __repr__(self):
        attrs = []
        for attr in dir(self):
            if attr.startswith('_'):
                continue
            val = getattr(self, attr)
            if val is None:
                continue
            attrs.append('%s=%r' % (attr, val))
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join(attrs))

    def __lt__(self, other):
        try:
            other = iatom.IEntry(other)
        except TypeError:
            return NotImplemented
        def _getPublished(entry):
            p = entry.published
            if p is None:
                p = entry.updated
            return p

        me = _getPublished(self)
        him = _getPublished(other)
        if me != him:
            return me < him
        if self.id != other.id:
            return self.id < other.id
        if self.title != other.title:
            return self.title < other.title
        raise RuntimeError

    def __le__(self, other):
        return self==other or self<other

    def __gt__(self, other):
        try:
            other = iatom.IEntry(other)
        except TypeError:
            return NotImplemented
        return other < self

    def __ge__(self, other):
        return self==other or self>other

    def __eq__(self, other):
        try:
            other = iatom.IEntry(other)
        except TypeError:
            return NotImplemented

        attrs = sets.Set()
        attrs.update([x for x in dir(self) if not x.startswith('_')])
        attrs.update([x for x in dir(other) if not x.startswith('_')])

        class _SENTINEL_1(object): pass
        class _SENTINEL_2(object): pass
        for attr in attrs:
            if (getattr(self, attr, _SENTINEL_1)
                != getattr(other, attr, _SENTINEL_2)):
                return False

        return True

    def __ne__(self, other):
        return not (self==other)

class Feed(object):
    implements(iatom.IFeed)

    id = None
    title = None
    updated = None

    author = None
    link = None
    category = None
    contributor = None
    generator = None
    icon = None
    logo = None
    rights = None
    subtitle = None

    def __init__(self, **kw):
        for a in ['id',
                  'title',
                  'updated']:
            v = kw.pop(a)
            setattr(self, a, v)

        entries = kw.pop('entries')
        self.entries = sets.Set(entries)

        for a in ['author',
                  'link',
                  'category',
                  'contributor',
                  'generator',
                  'icon',
                  'logo',
                  'rights',
                  'subtitle']:
            v = kw.pop(a, None)
            if v is not None:
                setattr(self, a, v)

