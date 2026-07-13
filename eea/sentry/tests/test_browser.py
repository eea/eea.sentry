"""Tests for Sentry browser view."""

import json
import os
import socket
import unittest
from unittest.mock import patch, MagicMock

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import alsoProvides

from eea.sentry.browser.sentry import Sentry, get_site


class MockRequest:
    """Mock request for testing."""

    def __init__(self):
        self.environ = {}
        self.form = {}
        self.other = {}
        self._lazies = {}
        self.method = "GET"
        self._rest_cors_preflight = False
        alsoProvides(self, IAttributeAnnotatable)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def getURL(self):
        return self.environ.get("URL", "http://localhost:8080/Plone")


class MockUser:
    """Mock authenticated user."""

    def __init__(self, username="Anonymous User", user_id="anonymous", email=""):
        self._username = username
        self._id = user_id
        self._email = email

    def getUserName(self):
        return self._username

    def getId(self):
        return self._id

    def getProperty(self, name):
        if name == "email":
            return self._email
        return None


class MockSite:
    """Mock site object."""

    def __init__(self, site_id="Plone"):
        self._id = site_id

    def getId(self):
        return self._id


class TestSentryDSN(unittest.TestCase):
    """Test Sentry.dsn()."""

    def setUp(self):
        self.request = MockRequest()
        self.view = Sentry(MagicMock(), self.request)

    @patch.dict(os.environ, {"SENTRY_DSN": ""})
    def test_dsn_empty(self):
        """Test dsn with empty SENTRY_DSN."""
        self.assertEqual(self.view.dsn(), "")

    @patch.dict(os.environ, {"SENTRY_DSN": "https://abc123@sentry.io/1"})
    def test_dsn_no_password(self):
        """Test dsn without password — returned as-is."""
        result = self.view.dsn()
        self.assertEqual(result, "https://abc123@sentry.io/1")

    @patch.dict(os.environ, {"SENTRY_DSN": "https://abc123:def456@sentry.io/1"})
    def test_dsn_with_password_stripped(self):
        """Test dsn with password — password stripped."""
        result = self.view.dsn()
        self.assertEqual(result, "https://abc123@sentry.io/1")

    @patch.dict(os.environ, {"SENTRY_DSN": "http://key:secret@sentry.example.com/42"})
    def test_dsn_http_with_password(self):
        """Test dsn over http with password — password stripped."""
        result = self.view.dsn()
        self.assertEqual(result, "http://key@sentry.example.com/42")

    @patch.dict(os.environ, {}, clear=True)
    def test_dsn_unset(self):
        """Test dsn with SENTRY_DSN not set."""
        self.assertEqual(self.view.dsn(), "")


class TestSentryVersion(unittest.TestCase):
    """Test Sentry.version()."""

    def setUp(self):
        self.request = MockRequest()
        self.view = Sentry(MagicMock(), self.request)

    @patch.dict(os.environ, {"SENTRY_RELEASE": "1.2.3"})
    def test_version_from_sentry_release(self):
        """Test version reads SENTRY_RELEASE."""
        self.assertEqual(self.view.version(), "1.2.3")

    @patch.dict(os.environ, {"EEA_KGS_VERSION": "5.0.0"}, clear=True)
    def test_version_from_kgs(self):
        """Test version falls back to EEA_KGS_VERSION."""
        self.assertEqual(self.view.version(), "5.0.0")

    @patch.dict(
        os.environ, {"SENTRY_RELEASE": "1.0", "EEA_KGS_VERSION": "5.0"}, clear=True
    )
    def test_version_sentry_release_takes_precedence(self):
        """Test SENTRY_RELEASE takes precedence over EEA_KGS_VERSION."""
        self.assertEqual(self.view.version(), "1.0")

    @patch.dict(os.environ, {}, clear=True)
    def test_version_empty(self):
        """Test version with no env vars."""
        self.assertEqual(self.view.version(), "")


class TestSentryEnvironment(unittest.TestCase):
    """Test Sentry.environment()."""

    def setUp(self):
        self.request = MockRequest()
        # Reset _environment class attribute to force re-read
        Sentry._environment = None
        self.view = Sentry(MagicMock(), self.request)

    def tearDown(self):
        Sentry._environment = None

    @patch.dict(os.environ, {"SENTRY_ENVIRONMENT": "production"})
    def test_environment_from_sentry_env(self):
        """Test environment reads SENTRY_ENVIRONMENT."""
        Sentry._environment = None
        view = Sentry(MagicMock(), self.request)
        self.assertEqual(view.environment(), "production")

    @patch.dict(os.environ, {"ENVIRONMENT": "staging"}, clear=True)
    def test_environment_from_env_var(self):
        """Test environment reads ENVIRONMENT as fallback."""
        Sentry._environment = None
        view = Sentry(MagicMock(), self.request)
        self.assertEqual(view.environment(), "staging")

    @patch.dict(os.environ, {}, clear=True)
    def test_environment_fallback_devel(self):
        """Test environment falls back to devel when no env var set."""
        Sentry._environment = None
        view = Sentry(MagicMock(), self.request)
        with patch("eea.sentry.browser.sentry.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("Connection refused")
            self.assertEqual(view.environment(), "devel")


class TestSentryServer(unittest.TestCase):
    """Test Sentry.server()."""

    def setUp(self):
        self.request = MockRequest()
        self.view = Sentry(MagicMock(), self.request)

    def test_server_returns_hostname(self):
        """Test server returns hostname."""
        result = self.view.server()
        self.assertEqual(result, socket.gethostname())
        self.assertIsInstance(result, str)


class TestSentryUser(unittest.TestCase):
    """Test Sentry.user()."""

    def setUp(self):
        self.request = MockRequest()
        self.view = Sentry(MagicMock(), self.request)

    def test_user_authenticated(self):
        """Test user with authenticated user."""
        self.request.AUTHENTICATED_USER = MockUser(
            username="john", user_id="john123", email="john@example.com"
        )
        result = json.loads(self.view.user())
        self.assertEqual(result, {"id": "john123"})

    def test_user_anonymous(self):
        """Test user with anonymous user."""
        self.request.AUTHENTICATED_USER = MockUser(
            username="Anonymous User", user_id="anonymous"
        )
        result = json.loads(self.view.user())
        self.assertEqual(result, {})

    def test_user_none(self):
        """Test user with no AUTHENTICATED_USER."""
        result = json.loads(self.view.user())
        self.assertEqual(result, {})


class TestGetSite(unittest.TestCase):
    """Test get_site() function."""

    def test_get_site_from_plone(self):
        """Test get_site with Plone portal available."""
        mock_site = MockSite("Plone")
        with patch("eea.sentry.browser.sentry.api") as mock_api:
            mock_api.portal.get.return_value = mock_site
            mock_api.exc.CannotGetPortalError = Exception
            result = get_site(MockRequest())
            self.assertEqual(result, mock_site)

    def test_get_site_no_plone_no_parents(self):
        """Test get_site with no Plone and no PARENTS."""
        request = MockRequest()
        with patch("eea.sentry.browser.sentry.api") as mock_api:
            mock_api.portal.get.side_effect = Exception("No portal")
            mock_api.exc.CannotGetPortalError = Exception
            with patch("eea.sentry.browser.sentry.CannotGetPortalError", Exception):
                result = get_site(request)
                self.assertIsNone(result)

    def test_get_site_fallback_to_parents(self):
        """Test get_site fallback to request.PARENTS."""
        mock_site = MockSite("FallbackSite")
        request = MockRequest()
        with patch("eea.sentry.browser.sentry.api") as mock_api:
            mock_api.portal.get.side_effect = Exception("No portal")
            mock_api.exc.CannotGetPortalError = Exception
            request.PARENTS = [mock_site, "other"]
            with patch("eea.sentry.browser.sentry.CannotGetPortalError", Exception):
                result = get_site(request)
                self.assertEqual(result, mock_site)


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
