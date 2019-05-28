""" No cache
"""
CACHE = {}

def ramcache(get_key, dependencies=None, lifetime=3600):
    """ RAM cache
    """
    def decorator(method):
        """ Decorator
        """
        def replacement(*args, **kwargs):
            """ Replacement
            """
            key = get_key()
            if key not in CACHE:
                CACHE[key] = method(*args, **kwargs)
            return CACHE[key]
        return replacement
    return decorator
