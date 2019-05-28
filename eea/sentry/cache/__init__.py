""" Caching module
"""
import logging
logger = logging.getLogger("eea.sentry")
try:
    from eea.cache import cache as ramcache
except ImportError:
    # Fail quiet if required cache packages are not installed in order to use
    # this package without caching
    logger.warn("eea.cache not installed. Memcached support DISABLED.")
    from eea.sentry.cache.nocache import ramcache

__all__ = [
    ramcache.__name__,
]
