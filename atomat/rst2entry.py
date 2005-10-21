from docutils.core import publish_string
from xml.dom import minidom
import xml.dom
from atomat import atom, xhtmlutil

def convertString(rst, **kw):
    """Convert reStructuredText to iatom.IEntry."""

    html = publish_string(source=rst,
                          writer_name='html',
                          settings_overrides={'input_encoding': 'utf-8',
                                              'output_encoding': 'utf-8',
                                              })
    tree = minidom.parseString(html)
    title = xhtmlutil.getNodeContentsAsText(xhtmlutil.getTitle(tree))

    body = xhtmlutil.getBody(tree)

    doc = xhtmlutil.only(xhtmlutil.getElementsByClass(body, 'document'))

    # kill h1.title
    for h1 in doc.getElementsByTagName('h1'):
        if xhtmlutil.elementHasClass(h1, 'title'):
            h1.parentNode.removeChild(h1)
            break

    # kill .docinfo
    for docinfo in xhtmlutil.getElementsByClass(doc, 'docinfo'):
        docinfo.parentNode.removeChild(docinfo)

    xhtmlutil.removeClass(doc, 'document')

    newdoc = xml.dom.getDOMImplementation().createDocument(
        'http://www.w3.org/1999/xhtml',
        'div', None)
    # kludge it to force xmlns to show up on output
    ns = newdoc.createAttribute('xmlns')
    ns.nodeValue = 'http://www.w3.org/1999/xhtml'
    newdoc.firstChild.setAttributeNode(ns)

    xhtmlutil.stripLeadingWhitespace(doc)
    xhtmlutil.stripTrailingWhitespace(doc)

    # if what is left is a single <p>, grab it's contents but not the <p>
    if (len(doc.childNodes) == 1
        and doc.firstChild.nodeType == doc.ELEMENT_NODE
        and doc.firstChild.tagName == 'p'):
        doc = doc.firstChild

    while doc.firstChild is not None:
        newdoc.firstChild.appendChild(doc.firstChild)
    content = atom.XHTMLContent(newdoc.firstChild)

    e = atom.Entry(updated='2005-10-21T18:30:02Z',
                   title=title,
                   content=content,
                   **kw)
    return e

