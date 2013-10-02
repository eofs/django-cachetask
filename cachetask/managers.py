from django.db import models

from cachetask.query import CacheQuerySet


class CacheManager(models.Manager):
    """
    Caches only selected queries
    """
    def cached(self):
        return CacheQuerySet(model=self.model, using=self._db)


class GreedyCacheManager(CacheManager):
    """
    Caches every query
    """
    def get_query_set(self):
        return CacheQuerySet(model=self.model, using=self._db)
