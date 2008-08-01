from __future__ import with_statement

import os
import urlparse
from docutils.core import publish_string
from docutils import utils
from xml.dom import minidom
import xml.dom
import email.Utils
from atomat import atom, xhtmlutil, datatypes
from pygments import lexers, formatters, highlight

from docutils.parsers import rst
from docutils import nodes
from cStringIO import StringIO

def sourcecode(name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine):
    filename = options.get('filename', None)
    if filename is None:
        code = u'\n'.join(content)
    else:
        source = state_machine.input_lines.source(
            lineno - state_machine.input_offset - 1)
        source_dir = os.path.dirname(os.path.abspath(source))
        filename = os.path.normpath(os.path.join(source_dir, filename))
        filename = utils.relative_path(None, filename)
        state.document.settings.record_dependencies.add(filename)
        with file(filename) as f:
            code = f.read().decode('utf-8')

    if arguments:
        (syntax,) = arguments
    else:
        syntax = 'text'
    lexer = lexers.get_lexer_by_name(syntax)
    formatter = formatters.HtmlFormatter()
    html = highlight(
        code=code,
        lexer=lexer,
        formatter=formatter,
        )

    title_text = options.get('title')
    if title_text:
        text_nodes, messages = state.inline_text(title_text, lineno)
        title = nodes.caption('', '# ', *text_nodes)
    else:
        messages = []
        title = None

    fig = nodes.figure('')
    fig['classes'].append('py-listing')
    if title is not None:
        fig += title

    fig += nodes.raw('', html, format='html')

    return [fig] + messages

sourcecode.arguments = (0, 1, True)
sourcecode.options = dict(filename=rst.directives.path,
                          title=rst.directives.unchanged,
                          )
sourcecode.content = 1

rst.directives.register_directive('sourcecode', sourcecode)

def comment(name, arguments, options, content, lineno,
            content_offset, block_text, state, state_machine):
    pass
comment.content = 1

rst.directives.register_directive('comment', comment)


def blockquote(name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine):
    # TODO want to put options['cite'] in <blockquote cite="...">
    q = nodes.block_quote('')
    for text in content:
        # TODO use nested_parse to allow rst markup inside of the
        # blockquote
        q += nodes.Text(text)

    if options['author']:
        addr = nodes.Element()
        if options['cite']:
            addr += nodes.raw('', '<a href="', format='html')
            addr += nodes.Text(options['cite'])
            addr += nodes.raw('', '">', format='html')
        addr += nodes.Text(options['author'])
        if options['cite']:
            addr += nodes.raw('', '</a>', format='html')
        q += nodes.raw('', '<address>', format='html')
        q += addr.children
        q += nodes.raw('', '</address>', format='html')

    return [q]
blockquote.arguments = (0, 0, True)
blockquote.options = dict(cite=rst.directives.uri,
                          author=str,
                          )
blockquote.content = True

rst.directives.register_directive('blockquote', blockquote)


def convertString(rst, filename=None, **kw):
    """Convert reStructuredText to iatom.IEntry."""

    html = publish_string(source=rst,
                          source_path=filename,
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

    # fix the links; otherwise foo/bar.rst saying <a href="quux">
    # will link to quux, not foo/quux
    for a in newdoc.firstChild.getElementsByTagName('a'):
        href = a.getAttribute('href')
        if href.startswith('#'):
            continue
        href = urlparse.urljoin(filename, href)

        a.setAttribute('href', href)

    content = atom.XHTMLContent(newdoc.firstChild)

    kw.update(metadata)
    e = atom.Entry(title=title,
                   content=content,
                   **kw)
    return e

