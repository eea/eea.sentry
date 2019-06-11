""" Main product initializer
"""
import os
import logging
import urllib2
from contextlib import closing
from raven.contrib.zope import ZopeSentryHandler
from zope.i18nmessageid.message import MessageFactory
EEAMessageFactory = MessageFactory('eea')
logger = logging.getLogger()


def environment():
    """ Try to get environment from rancher-metadata
    """
    url = "http://rancher-metadata/latest/self/stack/environment_name"
    try:
        with closing(urllib2.urlopen(url)) as conn:
            env = conn.read()
    except Exception as err:
        logger.warn("Couldn't get environ from rancher-metadata: %s.", err)
        env = "devel"
    return env


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    sentry_dsn = os.environ.get('SENTRY_DSN', '')
    if not sentry_dsn:
        return

    sentry_handler = ZopeSentryHandler(sentry_dsn,
        site=os.environ.get('SENTRY_SITE',
             os.environ.get('SERVER_NAME', "dev")),
        release=os.environ.get('SENTRY_RELEASE',
                os.environ.get('EEA_KGS_VERSION', 'dev')),
        environment=os.environ.get("SENTRY_ENVIRONMENT", environment()),
        processors=['eea.sentry.processors.SanitizeZopeProcessor'],
    )
    logger.addHandler(sentry_handler)
