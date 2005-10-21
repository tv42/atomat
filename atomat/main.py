import os, sys
from twisted.python import usage
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
    opts.run()

def runApp(*a, **kw):
    try:
        main(*a, **kw)
    except KeyboardInterrupt:
        n = cliplug.getCmdName()
        print >>sys.stderr, '%s: interrupted.' % n
        sys.exit(1)
