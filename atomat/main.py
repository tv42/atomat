import os, sys
from twisted.python import usage, log
from twisted.internet import defer, reactor
from twisted import plugin
from atomat import iatomat, cliplug

class Options(cliplug.SubCommandOptions):
    name = None

    def getSynopsis(self):
        return 'Usage: %s [options]' % self.name

    def complete(self, pre, post):
        plugins = plugin.getPlugins(iatomat.IAtomatCommand)
        plugins = list(plugins)
        def _cmp(a, b):
            return cmp(a.getFactory().__name__, b.getFactory().__name__)
        plugins.sort(_cmp)
        for p in plugins:
            cmd = p.getFactory()
            name = cmd.__name__.lower()
            if name.startswith('_'):
                continue
            if name == 'complete':
                continue
            if name.startswith(pre):
                yield name+' '

def prepareOptions(appname=None):
    if appname is None:
        appname='tadaa'
    appname = os.path.basename(appname)

    opts = Options()
    opts.name = appname

    return opts

def main(args, appname=None):
    opts = prepareOptions(appname)
    try:
        opts.parseOptions(args)
    except usage.UsageError, errortext:
        n = cliplug.getCmdName(opts)
        print >>sys.stderr, '%s: %s' % (n, errortext)
        print >>sys.stderr, '%s: Try --help for usage details.' % n
        sys.exit(1)
    opts = cliplug.getActiveSubcommand(opts)
    d = defer.maybeDeferred(opts.run)
    return d

_exitStatus = 0
def runApp(*a, **kw):
    d = main(*a, **kw)
    def eb(fail):
        log.err(fail)
        global _exitStatus
        _exitStatus = 1
    d.addErrback(eb)
    def cb(d):
        """
        Delay things so that if d triggers immediately,
        reactor.stop is not called before reactor.run.
        """
        d.addBoth(lambda _: reactor.stop())
    reactor.callLater(0, cb, d)
    reactor.run()
    sys.exit(_exitStatus)
