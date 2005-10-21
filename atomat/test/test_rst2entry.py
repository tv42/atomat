from twisted.trial import unittest
from atomat import iatom, rst2entry

class Convert(unittest.TestCase):
    def testSimple(self):
        got = rst2entry.convertString("""\
Bar
===

:updated: 2005-10-21T18:30:02Z


bar
""",
                                      id='xyzzy')
        self.failUnless(iatom.IEntry.providedBy(got), "convert() must return IEntry objects")
        iatom.IEntry.validateInvariants(got)

        self.assertEquals(got.id, 'xyzzy')
        self.assertEquals(got.title, 'Bar')
        self.assertEquals(got.updated, '2005-10-21T18:30:02Z')
        self.failUnless(iatom.IContent.providedBy(got.content), "content must provide IContent")

        self.assertEquals(got.content.dom.toxml(), u'<div xmlns="http://www.w3.org/1999/xhtml">bar</div>')


    def testMultipleParagraphs(self):
        """<p> is not stripped when there are multiple paragraphs."""
        got = rst2entry.convertString("""\
Bar
===

bar

baz
""",
                                      id='xyzzy')

        self.assertEquals(got.content.dom.toxml(), u'<div xmlns="http://www.w3.org/1999/xhtml"><p>bar</p>\n<p>baz</p></div>')
