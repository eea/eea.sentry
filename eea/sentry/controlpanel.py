"""
    Define site-specific sentry dsn
"""
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from eea.sentry.interfaces import ISentrySettings

class SentryControlPanelForm(RegistryEditForm):
    """
    Define form logic
    """

    id = "SentryControlPanel"
    schema = ISentrySettings
    schema_prefix = 'eea.sentry'
    label = 'Sentry Settings'
    description = u'Sentry settings allowing site-specific monitoring'

SentryControlPanelView = layout.wrap_form(
        SentryControlPanelForm, ControlPanelFormWrapper)