""" Raven custom processors for Zope
"""
from raven.processors import SanitizePasswordsProcessor


class SanitizeZopeProcessor(SanitizePasswordsProcessor):
    """ Sanitize zope request
    """
    HEADERS = frozenset([
        "HTTP_COOKIE",
        "HTTP_X_FORWARDED_FOR",
        "HTTP_X_USERNAME",
    ])

    def filter_extra(self, data):
        """ Filter REQUEST headers
        """
        data = super(SanitizeZopeProcessor, self).filter_extra(data)
        if "request" not in data:
            return data

        self.filter_http(data["request"])

        if "headers" not in data["request"]:
            return data

        for header in self.HEADERS:
            if header in data["request"]["headers"]:
                data["request"]["headers"][header] = self.MASK

        return data
