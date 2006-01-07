from zope.interface import Interface, Attribute, Invalid, invariant
import datetime
from nevow import inevow, accessors, compy, flat, tags

class RequiredAttributeMissingError(Invalid):
    """Missing required attribute"""

    def __init__(self, obj, attr):
        Invalid.__init__(self)
        self.obj = obj
        self.attr = attr

    def __repr__(self):
        return "%s: %r has no attr %r." % (self.__doc__,
                                           self.obj,
                                           self.attr)

def required(attr):
    def required_invariant(obj):
        if getattr(obj, attr, None) is None:
            raise RequiredAttributeMissingError(obj, attr)
    return required_invariant


class NotDateTimeError(Invalid):
    """Value is not of type datetime.datetime"""

    def __init__(self, value):
        Invalid.__init__(self)
        self.value = value

    def __repr__(self):
        return "%s: %r." % (self.__doc__,
                            self.value)

def isdatetime(attr):
    def isdatetime_invariant(obj):
        val = getattr(obj, attr, None)
        if not isinstance(val, datetime.datetime):
            raise NotDateTimeError(val)
    return isdatetime_invariant

class MustProvideError(Invalid):
    """Object must provide interface"""

    def __init__(self, obj, iface):
        Invalid.__init__(self)
        self.obj = obj
        self.iface = iface

    def __repr__(self):
        return "%s: %r does not provide %r." % (self.__doc__,
                                                self.obj,
                                                self.iface)

def mustprovide(iface, attr):
    def provide_invariant(obj):
        val = getattr(obj, attr)
        if not iface.providedBy(val):
            raise MustProvideError(val, iface)
    return provide_invariant



class IllegalValueError(Invalid):
    """Object has invalid value"""

    def __init__(self, value, allowed):
        Invalid.__init__(self)
        self.value = value
        self.allowed = allowed

    def __repr__(self):
        return "%s: %r is not in %r." % (self.__doc__,
                                         self.value,
                                         self.allowed)

def enumeratedvalues(attr, allowed):
    def enum_invariant(obj):
        val = getattr(obj, attr)
        if val not in allowed:
            raise IllegalValueError(val, allowed)
    return enum_invariant

class IFeed(Interface):
    """An Atom v1.0 feed."""

    #### required
    id = Attribute("Identifies the feed using a universally unique "
                   + "and permanent URI.")
    invariant(required('id'))

    title = Attribute("A human readable title for the feed.")
    invariant(required('title'))

    updated = Attribute("Indicates the last time the feed was modified "
                        + "in a significant way.""")
    invariant(required('updated'))
    invariant(isdatetime('updated'))
    #TODO use datetime

    #### recommended
    #TODO author

    #TODO link -- what about rel?

    #### optional
    #TODO category
    #TODO contributor
    #TODO generator
    #TODO icon
    #TODO logo
    #TODO rights
    #TODO subtitle

    #### entries
    entries = Attribute("A Set of IEntry objects.")

class EntrySetContainer(accessors.ListContainer):
    def __init__(self, *a, **kw):
        accessors.ListContainer.__init__(self, *a, **kw)
        self.original = list(self.original)

    def child(self, context, name):
        if name == 'sorted':
            l = self.original[:]
            l.sort()
            return l
        elif name == 'reversed':
            l = self.original[:]
            l.sort()
            l.reverse()
            return l
        else:
            return accessors.ListContainer.child(self, context, name)

    def __iter__(self):
        return iter(self.original)

class FeedContainer(accessors.ObjectContainer):
    def child(self, ctx, name):
        if name == 'entries':
            return EntrySetContainer(self.original.entries)
        else:
            return accessors.ObjectContainer.child(self, ctx, name)

compy.registerAdapter(FeedContainer, IFeed, inevow.IContainer)

class IText(Interface):
    #### required
    dom = Attribute("DOM tree of document ready to be inlined.")
    invariant(required('dom'))

def flattenIText(orig, ctx):
    assert orig.dom.nodeType == orig.dom.ELEMENT_NODE
    assert orig.dom.namespaceURI == 'http://www.w3.org/1999/xhtml'
    assert orig.dom.nodeName == 'div'

    for node in orig.dom.childNodes:
        yield tags.xml(node.toxml())
flat.registerFlattener(flattenIText, IText)

class IContent(Interface):
    """
    An Atom v1.0 feed entry content.

    Consider this Interface an abstract superclass only. You should
    always implement IInlineContent or ILinkedContent.
    """

    type = Attribute("One of 'text', 'html' or 'xhtml', or media type of content.")
    invariant(required('type'))
    # TODO type is really more freeform, I'm just not supporting those yet

class IInlineContent(IContent, IText):
    """Feed entry content that is inlined in the feed."""

class ILinkedContent(IContent):
    """Feed entry content that is located elsewhere."""

    #### required
    src = Attribute("URI where the content can be found.")
    invariant(required('src'))

    #### optional
    type = Attribute("Media type of content.")

class ILink(Interface):
    href = Attribute("URI of the referenced resource.")
    invariant(required('href'))

    rel = Attribute("""
    Relationship type of this link, as a string.

    One of

    - 'alternate': alternate representation of the entry or feed.
      Default.

    - 'enclosure': a potentially large related resource, such as podcast

    - 'related': an document related to the entry or feed

    - 'self': the feed itself.

    - 'via': the source of the information provided in the entry.

    - a full URI

    """)

    type = Attribute("Media type of the resource.")

    hreflang = Attribute("Language of the resource.")

    title = Attribute("Title of the resource.")

    length = Attribute("Length of the resource, in bytes.")
    # TODO invariant(integer('length'))

compy.registerAdapter(accessors.ObjectContainer, ILink, inevow.IContainer)

class IEntry(Interface):
    """An Atom 1.0 feed entry."""

    #### required
    id = Attribute("Identifies the entry using a universally unique "
                   + "and permanent URI.")
    invariant(required('id'))

    title = Attribute("A human readable title for the entry.")
    invariant(required('title'))

    updated = Attribute("Indicates the last time the entry was modified "
                        + "in a significant way.""")
    invariant(required('updated'))
    invariant(isdatetime('updated'))
    #TODO use datetime


    #### recommended
    #TODO author

    content = Attribute("Is, or links to, the complete content of the entry.")
    invariant(mustprovide(IContent, 'content'))

    link = Attribute("A Set of ILink entries.")
    #TODO invariant at most one of each `rel` and `hreflang` combination.

    #TODO summary


    #### optional
    category = Attribute("A Set of categories, where each category is a string.")
    #TODO support scheme and label in categories

    #TODO contributor
    #TODO published
    #TODO source
    #TODO rights

class LinkSetContainer(accessors.ListContainer):
    def child(self, context, name):
        for link in self.original:
            if link.rel == name:
                return link
        return accessors.ListContainer.child(self, context, name)

class EntryContainer(accessors.ObjectContainer):
    def child(self, ctx, name):
        if name == 'link':
            return LinkSetContainer(self.original.link)
        else:
            return accessors.ObjectContainer.child(self, ctx, name)

compy.registerAdapter(EntryContainer, IEntry, inevow.IContainer)
