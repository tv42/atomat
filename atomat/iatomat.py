from atomat.cliplug import ICliPlugin

class IAtomatCommand(ICliPlugin):
    def getFactory():
        """
        Get a factory class that will instantiate to option parsers.

        @rtype: twisted.python.usage.Options
        """
        pass
