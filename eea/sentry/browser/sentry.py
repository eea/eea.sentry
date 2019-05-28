""" Sentry
"""
import os
import logging
from urlparse import urlparse
from eventlet.green import urllib2
from contextlib import closing
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.sentry.cache import ramcache

logger = logging.getLogger("eea.sentry")

RANCHER_METADATA = 'http://rancher-metadata/latest'
TIMEOUT = 15

class Sentry(BrowserView):
    """ return sentry DSN env variable
    """
    _environment = os.environ.get("SENTRY_ENVIRONMENT", None)

    def __init__(self, context, request, view=None, manager=None):
        super(Sentry, self).__init__(context, request)
        self.view = view
        self.manager = manager

    @ramcache(lambda *args: "environment", lifetime=86400)
    def environment(self):
        """ Sentry environment
        """
        if not self._environment:
            self._environment = os.environ.get('ENVIRONMENT',
                                os.environ.get('SENTRY_ENVIRONMENT', ''))
            if not self._environment:
                url = RANCHER_METADATA + '/self/stack/environment_name'
                try:
                    with closing(urllib2.urlopen(url, timeout=TIMEOUT)) as con:
                        self._environment = con.read()
                except Exception as err:
                    logger.warn(
                        "Please provide SENTRY_ENVIRONMENT env as we "
                        "could not get it automatically from %s due to: %s", 
                        url, err)
                    self._environment = 'devel'
        return self._environment

    @ramcache(lambda *args: "version", lifetime=86400)
    def version(self):
        """ KGS version
        """
        return os.environ.get("SENTRY_RELEASE",
            os.environ.get("EEA_KGS_VERSION", ""))

    @ramcache(lambda *args: "dsn", lifetime=86400)
    def dsn(self):
        """ Public Sentry DSN
        """
        dsn = os.environ.get("SENTRY_DSN", "")
        if not "@" in dsn:
            return dsn

        # Remove password from SENTRY_DSN
        url = urlparse(dsn)
        public = url._replace(netloc="{}@{}".format(
            url.username, url.hostname))
        return public.geturl()

    @ramcache(lambda *args: "site", lifetime=86400)
    def site(self):
        """ Sentry site
        """
        return os.environ.get("SENTRY_SITE",
            os.environ.get("SERVER_NAME", ""))

    def __call__(self):
        return self.index()

    def render(self):
        return self.index()