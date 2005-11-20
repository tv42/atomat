from twisted.trial import unittest
import os
from atomat import main
from atomat.commands import import_

class Blackbox(unittest.TestCase):
    def setUp(self):
        self.outputFilename = self.mktemp()
        self.output = file(self.outputFilename, 'w')
        self.oldOutput, import_.OUTPUT = import_.OUTPUT, self.output

    def tearDown(self):
        self.output.close()
        import_.OUTPUT, self.output = self.oldOutput, None
        self.oldOutput = None

    def check(self, name):
        path = os.path.split(os.path.abspath(__file__))[0]
        d = main.main(['import', os.path.join(path, name)])
        d.addCallback(self._check_result, name, path)
        return d

    def _check_result(self, dummy, name, path):
        self.output.close()

        filename = os.path.join(
            os.path.split(os.path.abspath(self.outputFilename))[0],
            name+'.xml')
        os.rename(self.outputFilename, filename)

        atomfile = os.path.join(path, name+'.xml')

        want = file(atomfile).read()
        got = file(filename).read()
        self.assertEquals(got, want,
                          ("File content does not match for %s"
                           + "\nWANTED-----------------\n%s"
                           + "\nGOT--------------------\n%s") \
                          % (name, want, got))

    def test_simple(self):
        return self.check('import_simple')
