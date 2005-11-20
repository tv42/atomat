from docutils.core import publish_string
from xml.dom import minidom
import xml.dom
import email.Utils
from atomat import atom, xhtmlutil, datatypes

from docutils.parsers import rst
from docutils import nodes
from cStringIO import StringIO
from twisted.python import htmlizer

def python(name, arguments, options, content, lineno,
           content_offset, block_text, state, state_machine):
    inp = StringIO('\n'.join(content).encode('utf-8'))
    outp = StringIO()
    outp.write('<div class="py-listing">')
    htmlizer.filter(inp, outp, writer=htmlizer.SmallerHTMLWriter)
    outp.write('</div>')
    html = outp.getvalue()
    return [nodes.raw('', html, format='html')]
python.content = 1

rst.directives.register_directive('python', python)

def comment(name, arguments, options, content, lineno,
            content_offset, block_text, state, state_machine):
    pass
comment.content = 1

rst.directives.register_directive('comment', comment)


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

    # kill .docinfo, but store the data
    metadata = {}
    for docinfo in xhtmlutil.getElementsByClass(doc, 'docinfo'):
        for field in docinfo.getElementsByTagName('tr'):
            nameElem = xhtmlutil.only(xhtmlutil.getElementsByClass(field, 'docinfo-name'))
            name = xhtmlutil.getNodeContentsAsText(nameElem)
            name = name.rstrip(':')

            bodyElem = xhtmlutil.only(field.getElementsByTagName('td'))

            # undo automatic link creation by reStructuredText
            for node in bodyElem.childNodes:
                if (node.nodeType == bodyElem.ELEMENT_NODE
                    and node.tagName == 'a'):
                    while node.hasChildNodes():
                        bodyElem.insertBefore(node.firstChild, node)
                    bodyElem.removeChild(node)

            body = xhtmlutil.getNodeContentsAsText(bodyElem)

            metadata[name.lower()] = body
        docinfo.parentNode.removeChild(docinfo)

    for attr in ['updated', 'published']:
        val = metadata.get(attr, None)
        if val is not None:
            val = datatypes.DateTime().coerce(val, None)
            metadata[attr] = val

    metadata.setdefault('updated', metadata.get('published', None))
    if not metadata.get('updated', None):
        raise RuntimeError("Metadata field 'updated' not set.")

    # split author to separate name and email
    if 'author' in metadata:
        realname, address = email.Utils.parseaddr(metadata['author'])
        metadata['author'] = {'name': realname,
                              'email': address,
                              }

    tags = metadata.pop('tags', '').split(None)
    if tags:
        metadata['category'] = tags

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

    kw.update(metadata)
    e = atom.Entry(title=title,
                   content=content,
                   **kw)
    return e

