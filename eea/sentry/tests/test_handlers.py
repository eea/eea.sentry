"""Tests for eea.sentry module-level handler functions."""

import os
import unittest
from unittest.mock import patch, MagicMock

from eea.sentry import (
    _get_browser_from_request,
    _get_form_from_request,
    _get_other_from_request,
    _get_lazyitems_from_request,
    _get_request_from_request,
    _get_user_from_request,
    _before_send,
    before_send,
    environment,
)


class MockRequest:
    """Mock request for testing."""

    def __init__(self):
        self.environ = {}
        self.form = {}
        self.other = {}
        self._lazies = {}
        self.method = "GET"
        self.stdin = MagicMock()
        self.stdin.tell.return_value = 0
        self._rest_cors_preflight = False

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


class TestGetBrowserFromRequest(unittest.TestCase):
    """Test _get_browser_from_request()."""

    def test_edge_browser(self):
        """Test Edge detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 Edg/118.0"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Edge", "118.0"))

    def test_firefox_browser(self):
        """Test Firefox detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 Firefox/119.0"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Firefox", "119.0"))

    def test_chrome_browser(self):
        """Test Chrome detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 Chrome/118.0.0.0"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Chrome", "118.0.0.0"))

    def test_safari_browser(self):
        """Test Safari detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 Safari/605.1.15"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Safari", "605.1.15"))

    def test_ie_browser(self):
        """Test Internet Explorer detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 MSIE/9.0"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Internet Explorer", "9.0"))

    def test_opera_browser(self):
        """Test Opera detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 OPR/102.0"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Opera", "102.0"))

    def test_unknown_browser(self):
        """Test unknown browser returns None."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "SomeUnknownBrowser/1.0"
        result = _get_browser_from_request(req)
        self.assertIsNone(result)

    def test_empty_user_agent(self):
        """Test empty User-Agent returns None."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = ""
        result = _get_browser_from_request(req)
        self.assertIsNone(result)

    def test_no_user_agent(self):
        """Test missing HTTP_USER_AGENT returns None."""
        req = MockRequest()
        result = _get_browser_from_request(req)
        self.assertIsNone(result)

    def test_trident_ie(self):
        """Test Trident (IE) detection."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0 Trident/7.0"
        result = _get_browser_from_request(req)
        self.assertEqual(result, ("Internet Explorer", "7.0"))


class TestGetFormFromRequest(unittest.TestCase):
    """Test _get_form_from_request()."""

    def test_normal_form_fields(self):
        """Test normal form fields are returned."""
        req = MockRequest()
        req.form = {"title": "hello", "count": 42}
        result = _get_form_from_request(req)
        self.assertIn("title", result)
        self.assertIn("count", result)

    def test_password_field_obscured(self):
        """Test that password fields are obscured."""
        req = MockRequest()
        req.form = {"username": "admin", "password": "secret123"}
        result = _get_form_from_request(req)
        self.assertEqual(result["username"], repr("admin"))
        self.assertEqual(result["password"], repr("<password obscured>"))

    def test_empty_form(self):
        """Test empty form returns empty dict."""
        req = MockRequest()
        req.form = {}
        result = _get_form_from_request(req)
        self.assertEqual(result, {})


class TestGetOtherFromRequest(unittest.TestCase):
    """Test _get_other_from_request()."""

    def test_normal_other_fields(self):
        """Test normal other fields are returned."""
        req = MockRequest()
        req.other = {"key1": "val1", "key2": "val2"}
        result = _get_other_from_request(req)
        self.assertIn("key1", result)
        self.assertIn("key2", result)

    def test_parents_excluded(self):
        """Test that PARENTS is excluded."""
        req = MockRequest()
        req.other = {"PARENTS": [1, 2], "data": "keep"}
        result = _get_other_from_request(req)
        self.assertNotIn("PARENTS", result)
        self.assertIn("data", result)

    def test_response_excluded(self):
        """Test that RESPONSE is excluded."""
        req = MockRequest()
        req.other = {"RESPONSE": "resp", "data": "keep"}
        result = _get_other_from_request(req)
        self.assertNotIn("RESPONSE", result)
        self.assertIn("data", result)

    def test_password_in_other_obscured(self):
        """Test that password fields in other are obscured."""
        req = MockRequest()
        req.other = {"password": "secret", "data": "keep"}
        result = _get_other_from_request(req)
        self.assertEqual(result["password"], repr("<password obscured>"))


class TestGetLazyItemsFromRequest(unittest.TestCase):
    """Test _get_lazyitems_from_request()."""

    def test_normal_lazy_items(self):
        """Test normal lazy items are returned."""
        req = MockRequest()
        req._lazies = {"lazy1": "val1", "lazy2": "val2"}
        result = _get_lazyitems_from_request(req)
        self.assertIn("lazy1", result)
        self.assertIn("lazy2", result)

    def test_password_in_lazy_obscured(self):
        """Test that password fields in lazy items are obscured."""
        req = MockRequest()
        req._lazies = {"password": "secret", "data": "keep"}
        result = _get_lazyitems_from_request(req)
        self.assertEqual(result["password"], repr("<password obscured>"))

    def test_empty_lazy_items(self):
        """Test empty lazy items returns empty dict."""
        req = MockRequest()
        req._lazies = {}
        result = _get_lazyitems_from_request(req)
        self.assertEqual(result, {})


class TestGetRequestFromRequest(unittest.TestCase):
    """Test _get_request_from_request()."""

    def test_returns_dict_with_expected_keys(self):
        """Test that result has headers, url, method, host."""
        req = MockRequest()
        req.environ = {
            "URL": "http://localhost:8080/Plone/page",
            "REMOTE_ADDR": "192.168.1.1",
        }
        result = _get_request_from_request(req)
        self.assertIn("headers", result)
        self.assertIn("url", result)
        self.assertIn("method", result)
        self.assertIn("host", result)

    def test_url_from_geturl(self):
        """Test that url comes from request.getURL()."""
        req = MockRequest()
        result = _get_request_from_request(req)
        self.assertEqual(result["url"], "http://localhost:8080/Plone")

    def test_method(self):
        """Test that method is returned."""
        req = MockRequest()
        req.method = "POST"
        result = _get_request_from_request(req)
        self.assertEqual(result["method"], "POST")

    def test_host_from_remote_addr(self):
        """Test that host comes from REMOTE_ADDR."""
        req = MockRequest()
        req.environ["REMOTE_ADDR"] = "10.0.0.1"
        result = _get_request_from_request(req)
        self.assertEqual(result["host"], "10.0.0.1")

    def test_user_agent_header_mapped(self):
        """Test that HTTP_USER_AGENT is mapped to User-Agent."""
        req = MockRequest()
        req.environ["HTTP_USER_AGENT"] = "Mozilla/5.0"
        result = _get_request_from_request(req)
        self.assertEqual(result["headers"]["User-Agent"], "Mozilla/5.0")

    def test_query_string_extracted(self):
        """Test that QUERY_STRING is extracted to query_string."""
        req = MockRequest()
        req.environ["QUERY_STRING"] = "page=1&sort=asc"
        result = _get_request_from_request(req)
        self.assertEqual(result["query_string"], "page=1&sort=asc")

    def test_non_string_env_values_converted(self):
        """Test that non-string env values are converted to string."""
        req = MockRequest()
        req.environ = {"SOME_INT": 42}
        result = _get_request_from_request(req)
        self.assertEqual(result["headers"]["SOME_INT"], "42")


class TestGetUserFromRequest(unittest.TestCase):
    """Test _get_user_from_request()."""

    def test_user_with_authenticated_user(self):
        """Test with AUTHENTICATED_USER set on request."""
        req = MockRequest()
        req.AUTHENTICATED_USER = MockUser(
            username="john", user_id="john123", email="john@example.com"
        )
        result = _get_user_from_request(req)
        self.assertEqual(result["id"], "john123")
        self.assertEqual(result["email"], "john@example.com")

    def test_user_with_no_email(self):
        """Test user with empty email returns empty string."""
        req = MockRequest()
        req.AUTHENTICATED_USER = MockUser(username="john", user_id="john123", email="")
        result = _get_user_from_request(req)
        self.assertEqual(result["email"], "")

    def test_user_none_returns_anonymous(self):
        """Test that None user returns Anonymous."""
        req = MockRequest()
        with patch("eea.sentry.getSecurityManager") as mock_sm:
            mock_sm.return_value.getUser.return_value = None
            result = _get_user_from_request(req)
            self.assertEqual(result["id"], "Anonymous")


class TestEnvironment(unittest.TestCase):
    """Test environment() module-level function."""

    @patch("eea.sentry.request.urlopen")
    def test_environment_returns_response(self, mock_urlopen):
        """Test environment returns rancher-metadata response."""
        mock_conn = MagicMock()
        mock_conn.read.return_value = b"production"
        mock_urlopen.return_value.__enter__.return_value = mock_conn
        mock_urlopen.return_value.__exit__.return_value = False
        result = environment()
        self.assertEqual(result, "production")

    @patch("eea.sentry.request.urlopen")
    def test_environment_fallback_devel(self, mock_urlopen):
        """Test environment falls back to devel on error."""
        mock_urlopen.side_effect = Exception("Connection refused")
        result = environment()
        self.assertEqual(result, "devel")


class TestBeforeSend(unittest.TestCase):
    """Test _before_send() and before_send()."""

    def test_before_send_with_request(self):
        """Test _before_send injects extra data from request."""
        event = {"extra": {}}
        req = MockRequest()
        req.form = {"key": "value"}
        req.other = {"data": "test"}
        req._lazies = {"lazy": "val"}
        req.environ = {"URL": "http://localhost", "REMOTE_ADDR": "127.0.0.1"}
        with patch("eea.sentry.getRequest", return_value=req):
            result = _before_send(event, None)
            self.assertIn("other", result["extra"])
            self.assertIn("lazy items", result["extra"])
            self.assertIn("form", result["extra"])
            self.assertIn("request", result["extra"])

    def test_before_send_without_request(self):
        """Test _before_send with no request leaves event unchanged."""
        event = {"extra": {}}
        with patch("eea.sentry.getRequest", return_value=None):
            result = _before_send(event, None)
            self.assertEqual(result, event)

    def test_before_send_with_existing_extra(self):
        """Test _before_send does not overwrite existing extra keys."""
        event = {"extra": {"form": "already_set"}}
        req = MockRequest()
        with patch("eea.sentry.getRequest", return_value=req):
            result = _before_send(event, None)
            self.assertEqual(result["extra"]["form"], "already_set")

    def test_before_send_wrapper_passes_through(self):
        """Test before_send wrapper passes event through on success."""
        event = {"extra": {}}
        with patch("eea.sentry._before_send", return_value=event):
            result = before_send(event, None)
            self.assertEqual(result, event)

    def test_before_send_wrapper_catches_keyerror(self):
        """Test before_send wrapper catches KeyError and returns None."""
        with patch("eea.sentry._before_send", side_effect=KeyError("missing")):
            result = before_send({"extra": {}}, None)
            self.assertIsNone(result)


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
