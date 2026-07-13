"""Tests for setup handlers."""

import unittest

from eea.sentry.setuphandlers import HiddenProfiles


class TestHiddenProfiles(unittest.TestCase):
    """Test HiddenProfiles."""

    def setUp(self):
        self.hidden = HiddenProfiles()

    def test_get_non_installable_profiles(self):
        """Test that uninstall and universal profiles are hidden."""
        profiles = self.hidden.getNonInstallableProfiles()
        self.assertIsInstance(profiles, list)
        self.assertIn("eea.sentry:uninstall", profiles)
        self.assertIn("eea.sentry:universal", profiles)

    def test_profiles_are_strings(self):
        """Test that all profile entries are strings."""
        for profile in self.hidden.getNonInstallableProfiles():
            self.assertIsInstance(profile, str)

    def test_no_installable_profile_leaked(self):
        """Test that the default profile is NOT hidden."""
        profiles = self.hidden.getNonInstallableProfiles()
        self.assertNotIn("eea.sentry:default", profiles)


def test_suite():
    """Test suite."""
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
