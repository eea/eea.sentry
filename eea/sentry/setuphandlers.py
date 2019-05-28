""" Custom setup
"""
from zope.interface import implementer
try:
    from Products.CMFPlone.interfaces import INonInstallable
except ImportError:
    from zope.interface import Interface
    class INonInstallable(Interface):
        """ Not a Plone context
        """


@implementer(INonInstallable)
class HiddenProfiles(object):
    """ Hidden profiles
    """

    def getNonInstallableProfiles(self):
        """ Hide uninstall profile from site-creation and quickinstaller.
        """
        return [
            'eea.sentry:universal',
            'eea.sentry:uninstall',
        ]


def post_install(context):
    """ Post install script
    """
    # Do something at the end of the installation of this package.


def uninstall(context):
    """ Uninstall script
    """
    # Do something at the end of the uninstallation of this package.
