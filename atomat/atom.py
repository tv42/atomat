from zope.interface import implements
from atomat import iatom

class XHTMLContent(object):
    implements(iatom.IInlineContent)

    type = 'xhtml'

    def __init__(self, dom):
        self.dom = dom

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
                     'category', 'contributor', 'published',
                     'source', 'rights']:
            val = kw.pop(attr, None)
            if val is not None:
                setattr(self, attr, val)
