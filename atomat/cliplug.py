from zope.interface import implements
import os, sys
from twisted import plugin
from twisted.python import usage

class ICliPlugin(plugin.IPlugin):
    """
    Command line plugin.
    """
    def getFactory():
        """
        Get a twisted.python.usage.Options factory.

        Expected to implement the twisted.python.usage.Options API,
        but there's no Interface defined for that :(
        """
        pass

class SubCommandOptions(usage.Options):
    def __init__(self):
        usage.Options.__init__(self)
        self.subCommands = []
        plugins = plugin.getPlugins(ICliPlugin)
        plugins = list(plugins)
        def _cmp(a, b):
            return cmp(a.getFactory().__name__, b.getFactory().__name__)
        plugins.sort(_cmp)
        for p in plugins:
            cmd = p.getFactory()
            name = cmd.__name__.lower()
            description = cmd.__doc__
            self.subCommands.append((name,
                                     None,
                                     cmd,
                                     description))
        self.subCommands.sort()


    def run(self):
        if not hasattr(self, 'subOptions'):
            self.opt_help()

    def getUsage(self, *a, **kw):
        # skip commands with names starting with an underscore
        # TODO work on integrating this into t.p.usage
        save = self.subCommands
        self.subCommands = [x
                            for x in self.subCommands
                            if not x[0].startswith('_')]
        r = super(SubCommandOptions, self).getUsage(*a, **kw)
        self.subCommands = save
        return r

def getCmdName(config=None):
    l = [os.path.basename(sys.argv[0])]
    while config is not None and config.subCommand is not None:
        l.append(config.subCommand)
        config = config.subOptions
    return ' '.join(l)

def getActiveSubcommand(opts):
    while (opts.subCommand is not None
           and opts.subOptions is not None):
        opts = opts.subOptions
    return opts

class CommandFactory(object):
    implements(ICliPlugin)

    def __init__(self, factory):
        self.factory = factory

    def getFactory(self):
        return self.factory
