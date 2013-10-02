import time

from django.core.cache import cache

from cachetask import tasks


class CacheTask(object):
    """
    All data is stored in tuple (expiry, value). When expiry value is None, new task is already working on it refresh the data.
    Value will always be available during the refresh process.
    """

    # By default lifetime for cache item is 5 minutes. After this value is
    # considered stale and requires update.
    lifetime = 600

    # This value controls how often new Celery task may be created for a single
    # cache item.
    refresh_timeout = 60

    def get(self, *args, **kwargs):
        key = self.key(*args, **kwargs)
        item = cache.get(key)

        if item is None:
            # Cache MISS
            # Refresh cache synchronously
            return self.refresh(*args, **kwargs)

        expiry, data = item
        delta = time.time() - expiry
        if delta > 0:
            # Cache MISS but STALE data
            # Refresh cache asynchronously
            self.refresh_async(*args, **kwargs)
        return data

    def invalidate(self, *args, **kwargs):
        key = self.key(*args, **kwargs)
        item = cache.get(key)
        if item is not None:
            expiry, data = item
            self.cache_set(key, self.timeout(*args, **kwargs), data)
            self.refresh_async(*args, **kwargs)

    def delete(self, *args, **kwargs):
        key = self.key(*args, **kwargs)
        item = cache.get(key)
        if item is not None:
            cache.delete(key)


    ####################
    # Helper functions #
    ####################
    @property
    def class_path(self):
        return '%s.%s' % (self.__module__, self.__class__.__name__)

    def key(self, *args, **kwargs):
        """
        Return cache key
        """
        if not args and not kwargs:
            return self.class_path
        try:
            if args and not kwargs:
                return hash(args)
            return '%s:%s:%s' % (hash(args), hash(tuple(kwargs.keys())),
                                 hash(tuple(kwargs.values())))
        except TypeError:
            raise RuntimeError('Unable to generate cache key. Reimplement key().')


    def cache_set(self, key, expiry, data):
        """
        Update or set cache item.
        """
        cache.set(key, (expiry, data))

        __, cached_data = cache.get(key, (None, None))
        if data is not None and cached_data is None:
            print "Could not cache..."

    def expiry(self, *args, **kwargs):
        """
        Return expiry timestamp for cache item.
        """
        return time.time() + self.lifetime

    def timeout(self, *args, **kwargs):
        """
        Return refresh timeout for cache item.
        """
        return time.time() + self.refresh_timeout

    def refresh(self, *args, **kwargs):
        """
        Get refreshed result synchronously and update the cache.
        """
        result = self.run(*args, **kwargs)
        self.cache_set(self.key(*args, **kwargs),
                       self.expiry(*args, **kwargs),
                       result)
        return result

    def refresh_async(self, *args, **kwargs):
        tasks.refresh_cache.delay(
            call_args=args,
            call_kwargs=kwargs
        )


    ###################
    # Implement these #
    ###################
    def run(self, *args, **kwargs):
        """
        Run the actual expensive work.
        """
        raise NotImplementedError()
