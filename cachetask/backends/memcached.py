from django.core.cache.backends import memcached



class MemcachedCache(memcached.CacheClass):
    """
    Supports timeout value 0 (sets maximum timeout value possible)
    """
    def _get_memcache_timeout(self, timeout=None):
        if timeout == 0:
            return 0
        return super(MemcachedCache, self)._get_memcache_timeout(timeout)
