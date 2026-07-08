"""Test layer for eea.sentry."""

from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile

import eea.sentry


class EeaSentryLayer(PloneSandboxLayer):
    """Test layer for eea.sentry."""

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        self.loadZCML(package=eea.sentry)

    def setUpPloneSite(self, portal):
        """Set up Plone site."""
        applyProfile(portal, "eea.sentry:universal")


EEA_SENTRY_FIXTURE = EeaSentryLayer()

EEA_SENTRY_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EEA_SENTRY_FIXTURE,),
    name="EeaSentryLayer:IntegrationTesting",
)
