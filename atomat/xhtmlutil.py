from xml.dom import minidom

def getOnlyElementByTagName(iNode, name):
    elem = iNode.getElementsByTagName(name)
    assert len(elem)==1
    return elem[0]

def getHead(top):
    html = getOnlyElementByTagName(top, 'html')
    head = getOnlyElementByTagName(html, 'head')
    return head

def getTitle(top):
    head = getHead(top)
    title = getOnlyElementByTagName(head, 'title')
    return title

def getNodeContentsAsText(node):
    l = []
    for t in node.childNodes:
        assert isinstance(t, minidom.Text), \
               "Node contents must be text: %r" % t
        l.append(t.data)
    return u''.join(l).encode('utf-8')

def getBody(top):
    html = getOnlyElementByTagName(top, 'html')
    body = getOnlyElementByTagName(html, 'body')
    return body

def getElementsByClass(iNode, name):
    """Return list of elements with CSS class name."""
    matches = []
    matches_append = matches.append # faster lookup. don't do this at home
    slice=[iNode]
    while len(slice)>0:
        c = slice.pop(0)
        if hasattr(c, 'getAttribute'):
            classes = c.getAttribute("class")
            if classes and name in classes.split(None):
                matches_append(c)
        slice[:0] = c.childNodes
    return matches

def removeClass(node, name):
    """Remove CSS class name from node."""
    s = node.getAttribute("class")
    if s:
        classes = s.split(None)
        classes.remove(name)
        if classes:
            node.setAttribute("class", ' '.join(classes))
        else:
            node.removeAttribute("class")

def elementHasClass(node, name):
    if hasattr(node, 'getAttribute'):
        classes = node.getAttribute("class")
        if classes and name in classes.split(None):
            return True
    return False

def only(iterable):
    l = list(iterable)
    if not l:
        raise RuntimeError("only() got empty iterable")
    if len(l) > 1:
        raise RuntimeError("only() got iterable with %d items" % len(l))
    return l[0]

def stripLeadingWhitespace(node):
    while (node.firstChild is not None
           and node.firstChild.nodeType == node.TEXT_NODE
           and not node.firstChild.data.strip()):
        node.removeChild(node.firstChild)

def stripTrailingWhitespace(node):
    while (node.lastChild is not None
           and node.lastChild.nodeType == node.TEXT_NODE
           and not node.lastChild.data.strip()):
        node.removeChild(node.lastChild)
