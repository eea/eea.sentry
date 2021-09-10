"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope import schema


class IEeaSentryLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ISentrySettings(Interface):
    """ This interface defines the sentry setting fields """

    sentry_dsn = schema.TextLine(
        title=u"Sentry DSN key",
        description=u"A site specific Sentry DSN key"
    )
