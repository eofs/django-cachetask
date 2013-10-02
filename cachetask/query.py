import hashlib

from django.db import models

from cachetask.base import CacheTask


class CacheQuerySet(models.query.QuerySet):
    def get(self, *args, **kwargs):
        qs = self.filter(*args, **kwargs)
        return QueryGetTask(self.model, qs.query).get()

    def __len__(self):
        # Get executed QuerySet from cache (or run synchronously to get one)
        qs = QueryLenTask(self.model, self.query).get()
        # Using internals, but should be relative stable
        self._result_cache = qs._result_cache
        return super(CacheQuerySet, self).__len__()


class BaseQueryTask(CacheTask):
    def __init__(self, model, query):
        self.model = model
        self.query = query

    def key(self, *args, **kwargs):
        return '%s-%s' % (
            self.model.__name__,
            self._get_hash(self.query),
        )

    def _get_hash(self, query):
        """
        Calculate SHA1 hash for the query using its string representation
        """
        return hashlib.sha1(str(query)).hexdigest()

    def get_constructor_kwargs(self):
        return {
            'model': self.model,
            'query': self.query,
        }


class QueryGetTask(BaseQueryTask):
    """
    Cache task to run the query in background worker.
    """
    def run(self, *args, **kwargs):
        # Create a fake query
        qs = self.model.objects.all()
        # Restore original query
        qs.query = self.query
        # Execute and return result
        return qs.get()


class QueryLenTask(BaseQueryTask):
    """
    Cache task to run the query in background worker.
    """
    def run(self, *args, **kwargs):
        # Create a fake query
        qs = self.model.objects.all()

        if type(qs) == CacheQuerySet:
            # Swap back to original QuerySet to avoid
            # recursive lookups. Required by GreedyCacheManager.
            qs.__class__ = models.query.QuerySet

        # Restore original query
        qs.query = self.query
        # Execute the query
        len(qs)
        return qs
