from twisted.trial import unittest
import datetime
from atomat import atom

class Compare(unittest.TestCase):
    def check_decreasing_sequence(self, a, b, c):
        self.assertEquals(a, a)
        self.assertEquals(b, b)
        self.assertEquals(c, c)
        self.assertNotEquals(a, b)
        self.assertNotEquals(a, c)
        self.assertNotEquals(b, a)
        self.assertNotEquals(b, c)
        self.assertNotEquals(c, a)
        self.assertNotEquals(c, b)
        self.failUnless(a <= a, 'a <= a')
        self.failUnless(b <= b, 'b <= b')
        self.failUnless(c <= c, 'c <= c')
        self.failUnless(a >= a, 'a >= a')
        self.failUnless(b >= b, 'b >= b')
        self.failUnless(c >= c, 'c >= c')

        self.failUnless(b < a, 'b < a')
        self.failUnless(b <= a, 'b <= a')
        self.failUnless(c < b, 'c < b')
        self.failUnless(c <= b, 'c <= b')
        self.failUnless(c < a, 'c < a')
        self.failUnless(c <= a, 'c <= a')

        self.failIf(a < b, 'a < b')
        self.failIf(a <= b, 'a <= b')
        self.failIf(a < c, 'a < c')
        self.failIf(a <= c, 'a <= c')
        self.failIf(b < c, 'b < c')
        self.failIf(b <= c, 'b <= c')

        self.failUnless(a > b, 'a > b')
        self.failUnless(a >= b, 'a >= b')
        self.failUnless(b > c, 'b > c')
        self.failUnless(b >= c, 'b >= c')
        self.failUnless(a > c, 'a > c')
        self.failUnless(a >= c, 'a >= c')

        self.failIf(a < b, 'a < b')
        self.failIf(a <= b, 'a <= b')
        self.failIf(a < c, 'a < c')
        self.failIf(a <= c, 'a <= c')
        self.failIf(b < c, 'b < c')
        self.failIf(b <= c, 'b <= c')

        self.failIf(b > a, 'b > a')
        self.failIf(b >= a, 'b >= a')
        self.failIf(c > a, 'c > a')
        self.failIf(c >= a, 'c >= a')
        self.failIf(c > b, 'c > b')
        self.failIf(c >= b, 'c >= b')

    def test_compare_published(self):
        a = atom.Entry(id='foo',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        b = atom.Entry(id='bar',
                       title='Bar',
                       updated=datetime.datetime(2005,11,20, 12,42,16))
        c = atom.Entry(id='quux',
                       title='Quux',
                       updated=datetime.datetime(2005,11,20, 18,10,1),
                       published=datetime.datetime(2005,11,20, 12,40,16))
        self.check_decreasing_sequence(a, b, c)

    def test_compare_id(self):
        a = atom.Entry(id='quux',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        b = atom.Entry(id='bar',
                       title='Bar',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        c = atom.Entry(id='foo',
                       title='Quux',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2),
                       published=datetime.datetime(2005,11,20, 12,40,16))
        self.check_decreasing_sequence(a, b, c)

    def test_compare_title(self):
        a = atom.Entry(id='i',
                       title='Quux',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        b = atom.Entry(id='i',
                       title='Bar',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        c = atom.Entry(id='i',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2),
                       published=datetime.datetime(2005,11,20, 12,40,16))
        self.check_decreasing_sequence(a, b, c)

    def test_equality(self):
        a = atom.Entry(id='foo',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        b = atom.Entry(id='foo',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        self.failIfIdentical(a, b)
        self.failIfEquals(a, 42)
        self.failUnless(a == b, 'a == b')
        self.failIf(a != b, 'a != b')

    def test_equality_extraAttribute(self):
        a = atom.Entry(id='foo',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2))
        b = atom.Entry(id='foo',
                       title='Foo',
                       updated=datetime.datetime(2005,11,20, 13, 0, 2),
                       link='http://www.example.com/')
        self.failIfEquals(a, b)
        self.failUnless(a != b, 'a != b')

        self.failIfEquals(b, a)
        self.failUnless(b != a, 'b != a')

