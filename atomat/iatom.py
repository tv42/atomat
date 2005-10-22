from zope.interface import Interface, Attribute, Invalid, invariant
from nevow import inevow, accessors, compy

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

def rfc3339time(attr):
    def timeformat_invariant(obj):
        time = getattr(obj, attr, None)
        #TODO
    return timeformat_invariant

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
    invariant(rfc3339time('updated'))
    #TODO use datetime

    #### recommended
    #TODO author

    #TODO link

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

class IText(Interface):
    #### required
    dom = Attribute("DOM tree of document ready to be inlined.")
    invariant(required('dom'))

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
    invariant(rfc3339time('updated'))
    #TODO use datetime


    #### recommended
    #TODO author

    content = Attribute("Is, or links to, the complete content of the entry.")
    invariant(mustprovide(IContent, 'content'))

    #TODO link
    #TODO summary


    #### optional
    #TODO category
    #TODO contributor
    #TODO published
    #TODO source
    #TODO rights

compy.registerAdapter(accessors.ObjectContainer, IEntry, inevow.IContainer)
